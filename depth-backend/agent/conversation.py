import json
import os
import re

from google import genai
from google.genai import types
from fastapi import APIRouter, HTTPException

from agent.prompts import SYSTEM_PROMPT
from integrations import human_delta, openfda
from models.schemas import ChatRequest, ChatResponse, TriageData, DrugInteraction, MedSource, Message

router = APIRouter()


def _get_client() -> genai.Client:
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


async def _make_config(user_message: str) -> types.GenerateContentConfig:
    results = await human_delta.search(user_message, limit=5)
    if results:
        chunks = "\n\n---\n\n".join(
            f"[{r['page_title'] or r['source_url']}]\n{r['text']}"
            for r in results if r.get("text")
        )
        context_block = (
            "\n\n## MEDICAL KNOWLEDGE CONTEXT\n"
            "Ground your medical statements in these indexed sources. "
            "Do not make medical claims not supported here.\n\n" + chunks
        )
    else:
        context_block = ""

    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + context_block,
    )


def _has_age_sex(text: str) -> bool:
    return bool(re.search(r'\b\d{1,3}\s*(year[s\s]?old|male|female)\b', text, re.IGNORECASE))


def _medications_collected(history, current_message: str = "") -> bool:
    """True once the model asked about medications AND the patient replied."""
    for i, msg in enumerate(history):
        if msg.role == "model" and "medication" in msg.content.lower():
            if i + 1 < len(history) and history[i + 1].role == "user":
                return True
            if i == len(history) - 1 and current_message:
                return True  # current message is the reply
    return False


def _history_collected(history, current_message: str = "") -> bool:
    """True once the model asked about medical history AND the patient replied."""
    for i, msg in enumerate(history):
        if msg.role == "model" and (
            "medical history" in msg.content.lower() or "allerg" in msg.content.lower()
        ):
            if i + 1 < len(history) and history[i + 1].role == "user":
                return True
            if i == len(history) - 1 and current_message:
                return True  # current message is the reply
    return False


def _summary_in_history(history) -> bool:
    return any(
        "<clinical_summary>" in m.content
        or "S (Subjective):" in m.content
        or "\u200b" in m.content  # sentinel embedded by _parse_structured after two-phase
        for m in history
    )


_CONNECTOR_WORDS = {"and", "or", "the", "a", "an", "also", "with", "plus", "both", "then"}

def _extract_medications(history) -> list[str]:
    """Pull 'Drug Xmg' style medication names from user messages."""
    # Join with ". " so cross-message words (e.g. "male" + "Chlorthalidone") can't form a match
    all_user = ". ".join(m.content for m in history if m.role == "user")
    matches = re.findall(
        r'\b([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+)?)\s+\d+\s*(?:mg|mcg|ml|g)\b',
        all_user, re.IGNORECASE
    )
    result = []
    for m in matches:
        words = m.strip().split()
        if words[0].lower() in _CONNECTOR_WORDS:
            words = words[1:]
        name = " ".join(words).strip()
        if name:
            result.append(name)
    return list(dict.fromkeys(result))


def _extract_text(candidate) -> str:
    try:
        parts = candidate.content.parts
        if not parts:
            return ""
        return "".join(p.text for p in parts if hasattr(p, "text") and p.text)
    except (AttributeError, TypeError):
        return ""


def _parse_structured(text: str) -> tuple[str, str | None, dict | None]:
    clinical_summary = None
    triage = None

    m = re.search(r"<clinical_summary>(.*?)</clinical_summary>", text, re.DOTALL)
    if m:
        clinical_summary = m.group(1).strip()

    m = re.search(r"<triage>(.*?)</triage>", text, re.DOTALL)
    if m:
        try:
            triage = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    clean = re.sub(r"<clinical_summary>.*?</clinical_summary>", "\u200b", text, flags=re.DOTALL)
    clean = re.sub(r"<triage>.*?</triage>", "", clean, flags=re.DOTALL)
    clean = re.sub(r"<tool_code>.*?</tool_code>", "", clean, flags=re.DOTALL)
    clean = re.sub(r"```python.*?```", "", clean, flags=re.DOTALL)
    clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
    return clean, clinical_summary, triage


async def _gemini(client, contents, config):
    try:
        return await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Get a free key at aistudio.google.com/apikey.",
            )
        raise HTTPException(status_code=502, detail=f"Gemini API error: {e}")


def _parse_interactions(raw: str) -> list[DrugInteraction] | None:
    try:
        data = json.loads(raw)
        out = []
        for drug, info in data.items():
            reactions = info.get("top_reactions", [])
            if not reactions:
                continue
            warning_text = "; ".join(r.title() for r in reactions[:3])
            out.append(DrugInteraction(drug=drug, warning=warning_text, severity="MEDIUM"))
        return out or None
    except Exception:
        return None


def _stage(clinical_summary, triage, drug_interactions, two_phase_done=False, history=None) -> str:
    if two_phase_done:
        return "COMPLETE"
    if history and _summary_in_history(history):
        return "COMPLETE"  # follow-up after two-phase already ran
    if drug_interactions:
        return "GUIDANCE"
    if triage:
        return "TRIAGE"
    if clinical_summary:
        return "SUMMARY"
    return "INTAKE"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    client = _get_client()

    base_contents = []
    for msg in request.history:
        base_contents.append({"role": msg.role, "parts": [{"text": msg.content}]})
    base_contents.append({"role": "user", "parts": [{"text": request.message}]})

    all_history_text = " ".join(m.content for m in request.history) + " " + request.message

    # Two-phase triggers only when all intake items are confirmed collected
    needs_two_phase = (
        not _summary_in_history(request.history)
        and _has_age_sex(all_history_text)
        and _medications_collected(request.history, request.message)
        and _history_collected(request.history, request.message)
    )

    if needs_two_phase:
        config = await _make_config(request.message)

        # Phase 1 — force SOAP + triage output
        _PHASE1_PROMPT = (
            "Intake is complete. Proceed to Stage 2 immediately.\n\n"
            "You MUST output both blocks in this exact order:\n"
            "1. <clinical_summary> ... </clinical_summary>\n"
            "2. <triage> {\"level\": \"URGENT|SOON|HOME\", \"explanation\": \"...\"} </triage>\n\n"
            "After </triage>, write 1–2 plain sentences to the patient about what to do next. "
            "Do not mention medications. Do not ask questions. Do not add preamble."
        )
        summary_contents = base_contents + [{"role": "user", "parts": [{"text": _PHASE1_PROMPT}]}]
        summary_resp = await _gemini(client, summary_contents, config)
        summary_candidate = summary_resp.candidates[0] if summary_resp.candidates else None
        summary_raw = _extract_text(summary_candidate)
        summary_clean, clinical_summary, triage_raw = _parse_structured(summary_raw)

        # Retry once if either block is missing
        if not clinical_summary or not triage_raw:
            retry_contents = summary_contents + [
                {"role": "model", "parts": [{"text": summary_raw or ""}]},
                {"role": "user", "parts": [{"text": (
                    "Your response was missing the required XML blocks. "
                    "Output ONLY the <clinical_summary> block and <triage> block now, nothing else before them."
                )}]},
            ]
            retry_resp = await _gemini(client, retry_contents, config)
            retry_candidate = retry_resp.candidates[0] if retry_resp.candidates else None
            retry_raw = _extract_text(retry_candidate)
            _, clinical_summary_retry, triage_raw_retry = _parse_structured(retry_raw)
            if clinical_summary_retry:
                clinical_summary = clinical_summary_retry
                summary_raw = retry_raw
            if triage_raw_retry:
                triage_raw = triage_raw_retry

        triage_obj = None
        if triage_raw:
            triage_obj = TriageData(
                level=triage_raw.get("level", "SOON"),
                explanation=triage_raw.get("explanation", ""),
            )

        # Extract text the model wrote after </triage> (our Phase 1 prompt asks for it)
        after_triage = re.search(r"</triage>\s*(.*)", summary_raw, re.DOTALL)
        post_tag_text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", after_triage.group(1)).strip() if after_triage else ""

        patient_msg = (
            post_tag_text
            or (triage_obj.explanation if triage_obj else "")
            or "I've reviewed your symptoms. Please see the assessment and urgency level in the panel."
        )
        summary_clean = "\u200b" + patient_msg

        # Phase 2 — call openfda directly (no model intermediary) then ask model to explain
        # Include current message so meds mentioned in the triggering reply are captured
        full_history_for_meds = list(request.history) + [Message(role="user", content=request.message)]
        medications = _extract_medications(full_history_for_meds)
        drug_interactions = None
        guidance_clean = ""

        med_sources = None
        if medications:
            drug_raw = json.dumps(await openfda.check_interactions(medications))
            drug_interactions = _parse_interactions(drug_raw)

            # Always include a MedlinePlus link per medication (deterministic, always relevant)
            seen_urls: set[str] = set()
            med_sources: list[MedSource] = []
            for med in medications:
                url = f"https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus&v%3Asources=medlineplus-bundle&query={med.replace(' ', '+')}"
                seen_urls.add(url)
                med_sources.append(MedSource(title=f"{med} — MedlinePlus", url=url))

            # Append HD results only when score is very high AND the med name appears in the result
            symptom_context = (clinical_summary or request.message)[:300]
            for med in medications:
                for r in await human_delta.search(f"{med} {symptom_context}", limit=5):
                    url = r.get("source_url", "")
                    title = r.get("page_title") or ""
                    combined = (title + " " + r.get("text", "")).lower()
                    if (url and url not in seen_urls
                            and r.get("score", 0) > 0.7
                            and med.lower() in combined):
                        seen_urls.add(url)
                        med_sources.append(MedSource(title=title or url, url=url))

            med_sources = med_sources[:6] or None

            explain_contents = base_contents + [
                {"role": "model", "parts": [{"text": summary_raw or "I have reviewed the patient's information."}]},
                {"role": "user", "parts": [{"text": (
                    f"Drug interaction data: {drug_raw}\n\n"
                    "In 2–3 sentences, explain to the patient any relevant medication connections "
                    "to their current symptoms. Flag ⚠️ if any medication is known to cause their chief complaint."
                )}]},
            ]
            explain_resp = await _gemini(client, explain_contents, config)
            explain_candidate = explain_resp.candidates[0] if explain_resp.candidates else None
            guidance_clean, _, _ = _parse_structured(_extract_text(explain_candidate))

        return ChatResponse(
            message=summary_clean,
            stage=_stage(clinical_summary, triage_obj, drug_interactions, two_phase_done=True),
            clinical_summary=clinical_summary,
            triage=triage_obj,
            drug_interactions=drug_interactions,
            drug_interaction_summary=guidance_clean or None,
            med_sources=med_sources,
            clinics=None,
        )

    # Single-phase: intake or post-guidance follow-up — no tools, just conversation
    config = await _make_config(request.message)
    resp = await _gemini(client, list(base_contents), config)
    candidate = resp.candidates[0] if resp.candidates else None
    text = _extract_text(candidate)
    clean_text, clinical_summary, triage_raw = _parse_structured(text)

    triage_obj = None
    if triage_raw:
        triage_obj = TriageData(
            level=triage_raw.get("level", "SOON"),
            explanation=triage_raw.get("explanation", ""),
        )

    return ChatResponse(
        message=clean_text,
        stage=_stage(clinical_summary, triage_obj, None, history=request.history),
        clinical_summary=clinical_summary,
        triage=triage_obj,
        drug_interactions=None,
        clinics=None,
    )
