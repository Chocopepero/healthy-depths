import json
import os
import re
import google.generativeai as genai
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent.prompts import SYSTEM_PROMPT
from agent.tools import DEPTH_TOOLS
from integrations import human_delta, openfda, hrsa
from models.schemas import ChatRequest, ChatResponse, TriageData, DrugInteraction, Clinic

router = APIRouter()


def _build_model() -> genai.GenerativeModel:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[DEPTH_TOOLS],
        system_instruction=SYSTEM_PROMPT,
    )


async def _execute_tool(name: str, args: dict) -> str:
    if name == "search_knowledge_base":
        results = await human_delta.search(args.get("query", ""), limit=5)
        if not results:
            return "No results found in knowledge base."
        chunks = [r.get("text", "") for r in results if r.get("text")]
        return "\n\n".join(chunks[:3])

    if name == "check_drug_interactions":
        medications = args.get("medications", [])
        data = await openfda.check_interactions(medications)
        return json.dumps(data)

    if name == "find_clinics":
        zip_code = args.get("zip_code", "")
        radius = args.get("radius", 10)
        clinics = await hrsa.find_clinics(zip_code, radius)
        return json.dumps(clinics)

    return f"Unknown tool: {name}"


def _parse_structured(text: str) -> tuple[str, str | None, dict | None]:
    clinical_summary = None
    triage = None

    summary_match = re.search(r"<clinical_summary>(.*?)</clinical_summary>", text, re.DOTALL)
    if summary_match:
        clinical_summary = summary_match.group(1).strip()

    triage_match = re.search(r"<triage>(.*?)</triage>", text, re.DOTALL)
    if triage_match:
        try:
            triage = json.loads(triage_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    clean = re.sub(r"<clinical_summary>.*?</clinical_summary>", "", text, flags=re.DOTALL)
    clean = re.sub(r"<triage>.*?</triage>", "", clean, flags=re.DOTALL)
    clean = re.sub(r"\n{3,}", "\n\n", clean).strip()

    return clean, clinical_summary, triage


def _determine_stage(clinical_summary, triage, drug_interactions, clinics) -> str:
    if clinics:
        return "COMPLETE"
    if drug_interactions:
        return "GUIDANCE"
    if triage:
        return "TRIAGE"
    if clinical_summary:
        return "SUMMARY"
    return "INTAKE"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    model = _build_model()

    contents = []
    for msg in request.history:
        contents.append({"role": msg.role, "parts": [msg.content]})
    contents.append({"role": "user", "parts": [request.message]})

    tool_results: dict = {}
    max_iterations = 6

    for _ in range(max_iterations):
        response = await model.generate_content_async(contents)
        candidate = response.candidates[0]

        fn_calls = [
            p.function_call
            for p in candidate.content.parts
            if hasattr(p, "function_call") and p.function_call.name
        ]

        if not fn_calls:
            break

        contents.append(candidate.content)

        fn_response_parts = []
        for fc in fn_calls:
            result = await _execute_tool(fc.name, dict(fc.args))
            tool_results[fc.name] = result
            fn_response_parts.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fc.name,
                        response={"result": result},
                    )
                )
            )

        contents.append(genai.protos.Content(role="function", parts=fn_response_parts))

    raw_text = "".join(
        p.text for p in candidate.content.parts if hasattr(p, "text") and p.text
    )

    clean_text, clinical_summary, triage_raw = _parse_structured(raw_text)

    triage_obj = None
    if triage_raw and isinstance(triage_raw, dict):
        triage_obj = TriageData(
            level=triage_raw.get("level", "SOON"),
            explanation=triage_raw.get("explanation", ""),
        )

    drug_interactions = None
    if "check_drug_interactions" in tool_results:
        try:
            interaction_data = json.loads(tool_results["check_drug_interactions"])
            drug_interactions = []
            for drug, info in interaction_data.items():
                reactions = info.get("top_reactions", [])
                warnings = info.get("label_warnings", [])
                if reactions or warnings:
                    warning_text = "; ".join(reactions[:3]) if reactions else warnings[0] if warnings else "See prescriber."
                    drug_interactions.append(
                        DrugInteraction(
                            drug=drug,
                            warning=warning_text,
                            severity="MEDIUM",
                        )
                    )
        except Exception:
            pass

    clinics = None
    if "find_clinics" in tool_results:
        try:
            clinic_data = json.loads(tool_results["find_clinics"])
            clinics = [
                Clinic(
                    name=c.get("name", "Health Center"),
                    address=c.get("address", ""),
                    phone=c.get("phone"),
                    distance=c.get("distance"),
                    website=c.get("website"),
                )
                for c in clinic_data
            ]
        except Exception:
            pass

    stage = _determine_stage(clinical_summary, triage_obj, drug_interactions, clinics)

    return ChatResponse(
        message=clean_text,
        stage=stage,
        clinical_summary=clinical_summary,
        triage=triage_obj,
        drug_interactions=drug_interactions,
        clinics=clinics,
    )
