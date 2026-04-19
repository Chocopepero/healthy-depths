import httpx

HRSA_BASE = "https://findahealthcenter.hrsa.gov/api/v1"


async def find_clinics(zip_code: str, radius: int = 10) -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{HRSA_BASE}/health-centers",
                params={"zip": zip_code, "radius": radius},
            )
            resp.raise_for_status()
            data = resp.json()
            centers = data if isinstance(data, list) else data.get("results", data.get("healthCenters", []))

            clinics = []
            for c in centers[:3]:
                clinics.append({
                    "name": c.get("name", c.get("siteName", "Health Center")),
                    "address": _format_address(c),
                    "phone": c.get("phone", c.get("phoneNumber", "")),
                    "distance": c.get("distance"),
                    "website": c.get("website", c.get("siteWebAddress")),
                })
            return clinics
        except Exception as e:
            print(f"[HRSA] Clinic lookup failed: {e}")
            return []


def _format_address(center: dict) -> str:
    parts = [
        center.get("address", center.get("siteAddress", "")),
        center.get("city", center.get("siteCity", "")),
        center.get("state", center.get("siteState", "")),
        center.get("zip", center.get("siteZipCode", "")),
    ]
    return ", ".join(p for p in parts if p)
