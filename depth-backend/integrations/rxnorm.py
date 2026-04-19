import httpx

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


async def get_rxcui(drug_name: str) -> str | None:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                f"{RXNORM_BASE}/rxcui.json",
                params={"name": drug_name},
            )
            resp.raise_for_status()
            data = resp.json()
            rxcui = data.get("idGroup", {}).get("rxnormId", [])
            return rxcui[0] if rxcui else None
        except Exception:
            return None


async def normalize_drug_names(medications: list[str]) -> dict[str, str | None]:
    results = {}
    for med in medications:
        results[med] = await get_rxcui(med)
    return results
