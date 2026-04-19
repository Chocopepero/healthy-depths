import time
from humandelta import HumanDelta

hd = HumanDelta(api_key="hd_live_bbca9259c152b3df4ade216990e6e44b6484bc32cc78b94b")

# 0, A-D already queued — start from E
seed_urls = [
    f"https://medlineplus.gov/druginfo/drug_{chr(c)}a.html"
    for c in range(ord("E"), ord("Z") + 1)
]

for url in seed_urls:
    try:
        label = url.split("_")[-1].replace(".html", "").upper()
        job = hd.indexes.create(url, max_pages=500, name=f"MedlinePlus Drugs — {label}")
        print(f"{job.id}  {job.status}  {url}")
    except Exception as e:
        print(f"ERROR  {url}: {e}")
    time.sleep(4)
