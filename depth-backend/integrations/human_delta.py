import os
import asyncio
import httpx

HD_BASE_URL = "https://api.humandelta.com/v1"
HD_SOURCES = [
    {"url": "https://medlineplus.gov/druginformation.html", "name": "MedlinePlus Drugs", "maxPages": 100},
    {"url": "https://www.cdc.gov/niosh/topics/emres/chemsyn.html", "name": "CDC Symptoms", "maxPages": 50},
    {"url": "https://open.fda.gov/apis/", "name": "OpenFDA Docs", "maxPages": 50},
    {"url": "https://findahealthcenter.hrsa.gov/", "name": "HRSA Clinics", "maxPages": 30},
]

_index_ids: list[str] = []


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ.get('HD_API_KEY', '')}"}


async def index_sources() -> None:
    api_key = os.environ.get("HD_API_KEY", "")
    if not api_key:
        print("[HumanDelta] HD_API_KEY not set — skipping indexing")
        return

    async with httpx.AsyncClient(timeout=300) as client:
        for source in HD_SOURCES:
            try:
                resp = await client.post(
                    f"{HD_BASE_URL}/indexes",
                    json={"url": source["url"], "name": source["name"], "max_pages": source["maxPages"]},
                    headers=_headers(),
                )
                resp.raise_for_status()
                job = resp.json()
                job_id = job.get("id") or job.get("job_id")
                if job_id:
                    await _wait_for_index(client, job_id)
                    _index_ids.append(job_id)
                print(f"[HumanDelta] Indexed: {source['name']}")
            except Exception as e:
                print(f"[HumanDelta] Failed to index {source['name']}: {e}")


async def _wait_for_index(client: httpx.AsyncClient, job_id: str, max_wait: int = 120) -> None:
    for _ in range(max_wait // 5):
        await asyncio.sleep(5)
        try:
            resp = await client.get(f"{HD_BASE_URL}/indexes/{job_id}", headers=_headers())
            data = resp.json()
            status = data.get("status", "")
            if status in ("completed", "ready", "done"):
                return
            if status in ("failed", "error"):
                raise RuntimeError(f"Index job {job_id} failed")
        except httpx.HTTPError:
            pass


async def search(query: str, limit: int = 5) -> list[dict]:
    api_key = os.environ.get("HD_API_KEY", "")
    if not api_key:
        return []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{HD_BASE_URL}/search",
                json={"query": query, "limit": limit},
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", data) if isinstance(data, dict) else data
        except Exception as e:
            print(f"[HumanDelta] Search failed: {e}")
            return []
