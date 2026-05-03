"""Food-as-medicine endpoints — symptom analysis and healing food recommendations."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.food_medicine import analyse_symptoms, SYMPTOM_DB
from app.services.nexus import nexus_service

router = APIRouter(prefix="/food-medicine", tags=["food-medicine"])


class SymptomRequest(BaseModel):
    symptoms: list[str]
    include_nexus: bool = True


class HealingFood(BaseModel):
    food: str
    reason: str
    evidence: str


class SymptomAnalysis(BaseModel):
    condition: str
    deficiencies: list[str]
    excesses: list[str]
    root_causes: list[str]
    healing_foods: list[HealingFood]
    avoid: list[str]
    protocol: str
    nexus_insight: str | None = None


@router.post("/analyse", response_model=list[SymptomAnalysis])
async def analyse(
    body: SymptomRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyse symptoms and return science-backed food medicine recommendations."""
    results = analyse_symptoms(body.symptoms)

    if body.include_nexus and results:
        conditions = ", ".join(r["condition"] for r in results)
        symptoms_str = ", ".join(body.symptoms)
        prompt = (
            f"The user reports these symptoms: {symptoms_str}. "
            f"Based on nutritional science, these map to: {conditions}. "
            f"Give a personalised, compassionate 3-paragraph response covering: "
            f"1) The likely root cause from a nutritional perspective, "
            f"2) The most important dietary changes to make immediately, "
            f"3) A realistic 30-day healing protocol. Be specific and evidence-based."
        )
        try:
            nexus_result = await nexus_service.chat(
                message=prompt,
                user_id=str(current_user.id),
                profile=getattr(current_user, "profile", None),
            )
            nexus_insight = nexus_result.get("response", "")
        except Exception:
            nexus_insight = None

        for r in results:
            r["nexus_insight"] = nexus_insight

    return results


@router.get("/conditions")
async def list_conditions():
    """List all conditions in the knowledge base."""
    return {
        "conditions": [
            {"key": k, "label": k.replace("_", " ").title()}
            for k in SYMPTOM_DB.keys()
        ]
    }


@router.get("/condition/{condition_key}")
async def get_condition(condition_key: str):
    """Get full detail for a specific condition."""
    if condition_key not in SYMPTOM_DB:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Condition not found")
    entry = SYMPTOM_DB[condition_key]
    return {"condition": condition_key.replace("_", " ").title(), **entry}
