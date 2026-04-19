"""
Run once to index medical sources into Human Delta.
  python setup_indexes.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from humandelta import HumanDelta

SOURCES = [
    {"url": "https://medlineplus.gov/druginformation.html", "name": "MedlinePlus Drugs", "max_pages": 100},
    {"url": "https://www.cdc.gov/niosh/topics/emres/chemsyn.html", "name": "CDC Symptoms", "max_pages": 50},
    {"url": "https://open.fda.gov/apis/", "name": "OpenFDA Docs", "max_pages": 50},
    {"url": "https://findahealthcenter.hrsa.gov/", "name": "HRSA Clinics", "max_pages": 30},
]

hd = HumanDelta(api_key=os.environ["HD_API_KEY"])

existing = {job.name for job in hd.indexes.list()}

for source in SOURCES:
    if source["name"] in existing:
        print(f"[skip] Already indexed: {source['name']}")
        continue
    print(f"[index] Starting: {source['name']} ...")
    job = hd.indexes.create(source["url"], max_pages=source["max_pages"], name=source["name"])
    job.wait(interval=5, timeout=600)
    print(f"[done]  {source['name']} — status: {job.status}")

print("\nAll sources ready.")
