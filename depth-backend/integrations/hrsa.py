import os
import httpx

HRSA_BASE = "https://data.hrsa.gov/HDWAPI3_External/api/v1"


async def find_clinics(zip_code: str, radius: int = 10) -> list[dict]:
    token = os.environ.get("HRSA_TOKEN", "")
    if not token:
        print("[HRSA] HRSA_TOKEN not set — using fallback")
        return _fallback(zip_code)

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{HRSA_BASE}/GetHealthCentersByArea",
                params={"ZipCode": zip_code, "Token": token},
            )
            resp.raise_for_status()
            data = resp.json()
            centers = data.get("HCC", [])

            clinics = []
            for c in centers[:3]:
                clinics.append({
                    "name": c.get("SITE_NM", "Health Center"),
                    "address": _format_address(c),
                    "phone": c.get("SITE_PHONE_NUM") or None,
                    "distance": c.get("Distance"),
                    "website": c.get("SITE_URL") or None,
                })

            return clinics if clinics else _fallback(zip_code)

        except Exception as e:
            print(f"[HRSA] Clinic lookup failed: {e}")
            return _fallback(zip_code)


def _format_address(c: dict) -> str:
    parts = [
        c.get("SITE_ADDRESS", ""),
        c.get("SITE_CITY", ""),
        c.get("SITE_STATE_ABBR", ""),
        c.get("SITE_ZIP_CD", ""),
    ]
    return ", ".join(p for p in parts if p)


def _fallback(zip_code: str) -> list[dict]:
    return [
        {
            "name": "Find a Health Center Near You",
            "address": f"Search for sliding-scale clinics near {zip_code}",
            "phone": None,
            "distance": None,
            "website": f"https://findahealthcenter.hrsa.gov/?zip={zip_code}",
        }
    ]
