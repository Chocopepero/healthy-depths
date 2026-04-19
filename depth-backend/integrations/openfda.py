import httpx
from integrations.rxnorm import normalize_drug_names

OPENFDA_BASE = "https://api.fda.gov/drug"


async def fetch_adverse_events(drug_name: str, limit: int = 5) -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{OPENFDA_BASE}/event.json",
                params={
                    "search": f'patient.drug.medicinalproduct:"{drug_name}"',
                    "limit": limit,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except Exception:
            return []


async def fetch_label_interactions(drug_name: str) -> list[str]:
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{OPENFDA_BASE}/label.json",
                params={
                    "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
                    "limit": 1,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return []
            label = results[0]
            interactions = label.get("drug_interactions", [])
            warnings = label.get("warnings", [])
            return interactions + warnings
        except Exception:
            return []


async def check_interactions(medications: list[str]) -> dict:
    normalized = await normalize_drug_names(medications)
    interaction_data = {}

    for med in medications:
        events = await fetch_adverse_events(med)
        label_warnings = await fetch_label_interactions(med)

        serious_reactions = []
        for event in events:
            for reaction in event.get("patient", {}).get("reaction", []):
                reaction_name = reaction.get("reactionmeddrapt", "")
                if reaction_name:
                    serious_reactions.append(reaction_name)

        interaction_data[med] = {
            "rxcui": normalized.get(med),
            "top_reactions": list(set(serious_reactions[:10])),
            "label_warnings": label_warnings[:3],
        }

    return interaction_data
