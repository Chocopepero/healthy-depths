import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from agent.conversation import router as chat_router
from integrations import hrsa, openfda, human_delta
from models.schemas import InteractionRequest, InteractionResponse, DrugInteraction


app = FastAPI(title="Depth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.post("/api/interactions", response_model=InteractionResponse)
async def check_interactions(request: InteractionRequest):
    data = await openfda.check_interactions(request.medications)
    interactions = []
    for drug, info in data.items():
        reactions = info.get("top_reactions", [])
        warnings = info.get("label_warnings", [])
        if reactions or warnings:
            warning_text = "; ".join(reactions[:3]) if reactions else (warnings[0] if warnings else "See prescriber.")
            interactions.append(
                DrugInteraction(drug=drug, warning=warning_text, severity="MEDIUM")
            )

    summary = (
        f"Checked {len(request.medications)} medication(s). "
        f"Found {len(interactions)} with notable events."
    )
    return InteractionResponse(interactions=interactions, summary=summary)


@app.get("/api/clinics")
async def get_clinics(zip: str = Query(..., description="ZIP code"), radius: int = 10):
    clinics = await hrsa.find_clinics(zip, radius)
    return {"clinics": clinics}


@app.get("/health")
def health():
    return {"status": "ok"}
