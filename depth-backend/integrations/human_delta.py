import asyncio
import os

_hd = None


def _get_client():
    global _hd
    if _hd is None:
        from humandelta import HumanDelta
        _hd = HumanDelta(api_key=os.environ["HD_API_KEY"])
    return _hd


async def search(query: str, limit: int = 5) -> list[dict]:
    if not os.environ.get("HD_API_KEY"):
        return []
    try:
        results = await asyncio.to_thread(_get_client().search, query, top_k=limit)
        return [
            {
                "text": r.text,
                "source_url": r.source_url,
                "page_title": r.page_title,
                "score": r.score,
            }
            for r in results
        ]
    except Exception as e:
        print(f"[HumanDelta] Search failed: {e}")
        return []
