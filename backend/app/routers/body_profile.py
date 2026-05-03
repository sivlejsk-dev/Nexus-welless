"""Physical and psychological profile endpoints."""
from __future__ import annotations
import math
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.nexus import nexus_service

router = APIRouter(prefix="/body-profile", tags=["body-profile"])

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class PhysicalProfile(BaseModel):
    # Body measurements
    height_cm: float | None = None
    weight_kg: float | None = None
    age: int | None = None
    biological_sex: str | None = None  # male/female/other
    body_fat_pct: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    # Vitals
    resting_heart_rate: int | None = None
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    fasting_glucose: float | None = None
    # Activity
    activity_level: str | None = None  # sedentary/light/moderate/active/athlete
    exercise_days_per_week: int | None = None
    sleep_hours: float | None = None
    # Lifestyle
    smoker: bool | None = None
    alcohol_units_per_week: int | None = None
    water_litres_per_day: float | None = None
    # Medical
    medications: list[str] = Field(default_factory=list)
    diagnosed_conditions: list[str] = Field(default_factory=list)
    family_history: list[str] = Field(default_factory=list)
    # Diet
    diet_type: str | None = None
    meal_frequency: int | None = None
    intermittent_fasting: bool | None = None


class PsychProfile(BaseModel):
    # Big Five personality (1-10 scale)
    openness: int | None = Field(None, ge=1, le=10)
    conscientiousness: int | None = Field(None, ge=1, le=10)
    extraversion: int | None = Field(None, ge=1, le=10)
    agreeableness: int | None = Field(None, ge=1, le=10)
    neuroticism: int | None = Field(None, ge=1, le=10)
    # Mental health
    stress_level: int | None = Field(None, ge=1, le=10)
    anxiety_level: int | None = Field(None, ge=1, le=10)
    mood_stability: int | None = Field(None, ge=1, le=10)
    motivation_level: int | None = Field(None, ge=1, le=10)
    self_esteem: int | None = Field(None, ge=1, le=10)
    # Lifestyle psychology
    mindfulness_practice: bool | None = None
    social_connection: int | None = Field(None, ge=1, le=10)
    purpose_clarity: int | None = Field(None, ge=1, le=10)
    trauma_history: bool | None = None
    therapy_current: bool | None = None
    # Cognitive
    cognitive_load: int | None = Field(None, ge=1, le=10)
    creativity_level: int | None = Field(None, ge=1, le=10)
    # Goals
    primary_mental_goal: str | None = None
    biggest_mental_challenge: str | None = None


class FullProfileRequest(BaseModel):
    physical: PhysicalProfile
    psychological: PsychProfile


# ── Calculation helpers ───────────────────────────────────────────────────────

def _bmi(weight_kg: float, height_cm: float) -> float:
    return round(weight_kg / ((height_cm / 100) ** 2), 1)

def _bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Mifflin-St Jeor equation."""
    if sex == "female":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
    "active": 1.725, "athlete": 1.9,
}

def _tdee(bmr: float, activity: str) -> float:
    return round(bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.55))

def _whr(waist: float, hip: float) -> float:
    return round(waist / hip, 3)

def _body_score(physical: PhysicalProfile) -> dict[str, Any]:
    score = {}
    if physical.height_cm and physical.weight_kg:
        bmi = _bmi(physical.weight_kg, physical.height_cm)
        score["bmi"] = bmi
        score["bmi_category"] = (
            "Underweight" if bmi < 18.5 else
            "Normal" if bmi < 25 else
            "Overweight" if bmi < 30 else "Obese"
        )
    if physical.height_cm and physical.weight_kg and physical.age and physical.biological_sex:
        bmr = _bmr(physical.weight_kg, physical.height_cm, physical.age, physical.biological_sex)
        score["bmr_kcal"] = round(bmr)
        if physical.activity_level:
            score["tdee_kcal"] = _tdee(bmr, physical.activity_level)
    if physical.waist_cm and physical.hip_cm:
        whr = _whr(physical.waist_cm, physical.hip_cm)
        score["waist_hip_ratio"] = whr
        sex = physical.biological_sex or "male"
        if sex == "female":
            score["whr_risk"] = "Low" if whr < 0.80 else "Moderate" if whr < 0.85 else "High"
        else:
            score["whr_risk"] = "Low" if whr < 0.90 else "Moderate" if whr < 0.95 else "High"
    if physical.resting_heart_rate:
        hr = physical.resting_heart_rate
        score["heart_rate_category"] = (
            "Athlete" if hr < 50 else "Excellent" if hr < 60 else
            "Good" if hr < 70 else "Average" if hr < 80 else "High"
        )
    return score

def _psych_score(psych: PsychProfile) -> dict[str, Any]:
    scores = {}
    big5 = {k: getattr(psych, k) for k in ["openness","conscientiousness","extraversion","agreeableness","neuroticism"] if getattr(psych, k) is not None}
    if big5:
        scores["big_five"] = big5
        scores["resilience_index"] = round(
            ((big5.get("conscientiousness",5) + big5.get("agreeableness",5) + (10 - big5.get("neuroticism",5))) / 3), 1
        )
    mental = {k: getattr(psych, k) for k in ["stress_level","anxiety_level","mood_stability","motivation_level","self_esteem"] if getattr(psych, k) is not None}
    if mental:
        scores["mental_health_snapshot"] = mental
        avg = sum(mental.values()) / len(mental)
        scores["overall_mental_wellness"] = round(avg, 1)
    return scores


def _build_nexus_prompt(physical: PhysicalProfile, psych: PsychProfile, body_metrics: dict, psych_metrics: dict) -> str:
    lines = ["Analyse this person's complete physical and psychological profile and provide a detailed, personalised wellness assessment:\n"]
    if physical.age: lines.append(f"Age: {physical.age}, Sex: {physical.biological_sex}")
    if "bmi" in body_metrics: lines.append(f"BMI: {body_metrics['bmi']} ({body_metrics.get('bmi_category','')})")
    if "tdee_kcal" in body_metrics: lines.append(f"Daily calorie need (TDEE): {body_metrics['tdee_kcal']} kcal")
    if "waist_hip_ratio" in body_metrics: lines.append(f"Waist-hip ratio: {body_metrics['waist_hip_ratio']} ({body_metrics.get('whr_risk','')} risk)")
    if physical.resting_heart_rate: lines.append(f"Resting HR: {physical.resting_heart_rate} bpm ({body_metrics.get('heart_rate_category','')})")
    if physical.systolic_bp: lines.append(f"Blood pressure: {physical.systolic_bp}/{physical.diastolic_bp} mmHg")
    if physical.activity_level: lines.append(f"Activity: {physical.activity_level}, {physical.exercise_days_per_week} days/week")
    if physical.sleep_hours: lines.append(f"Sleep: {physical.sleep_hours} hours/night")
    if physical.smoker: lines.append("Smoker: Yes")
    if physical.alcohol_units_per_week: lines.append(f"Alcohol: {physical.alcohol_units_per_week} units/week")
    if physical.diagnosed_conditions: lines.append(f"Conditions: {', '.join(physical.diagnosed_conditions)}")
    if physical.medications: lines.append(f"Medications: {', '.join(physical.medications)}")
    if physical.diet_type: lines.append(f"Diet: {physical.diet_type}")
    if "overall_mental_wellness" in psych_metrics: lines.append(f"Mental wellness score: {psych_metrics['overall_mental_wellness']}/10")
    if psych.stress_level: lines.append(f"Stress: {psych.stress_level}/10, Anxiety: {psych.anxiety_level}/10")
    if psych.primary_mental_goal: lines.append(f"Primary mental goal: {psych.primary_mental_goal}")
    if psych.biggest_mental_challenge: lines.append(f"Biggest challenge: {psych.biggest_mental_challenge}")
    lines.append("\nProvide: 1) Top 3 health risks based on this data, 2) Personalised nutrition plan with specific foods and quantities, 3) Exercise prescription, 4) Mental wellness protocol, 5) 90-day transformation roadmap with monthly milestones. Be specific, evidence-based, and compassionate.")
    return "\n".join(lines)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/analyse")
async def analyse_full_profile(
    body: FullProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    body_metrics = _body_score(body.physical)
    psych_metrics = _psych_score(body.psychological)
    prompt = _build_nexus_prompt(body.physical, body.psychological, body_metrics, psych_metrics)

    nexus_insight = None
    try:
        result = await nexus_service.chat(
            message=prompt,
            user_id=str(current_user.id),
            profile=getattr(current_user, "profile", None),
        )
        nexus_insight = result.get("response")
    except Exception:
        pass

    return {
        "body_metrics": body_metrics,
        "psych_metrics": psych_metrics,
        "nexus_analysis": nexus_insight,
    }


@router.get("/questions")
async def get_profile_questions():
    """Return the structured question sets for the profile wizard."""
    return {
        "physical_sections": [
            {
                "id": "body",
                "title": "Body Measurements",
                "icon": "ruler",
                "fields": [
                    {"id": "height_cm", "label": "Height (cm)", "type": "number", "unit": "cm"},
                    {"id": "weight_kg", "label": "Weight (kg)", "type": "number", "unit": "kg"},
                    {"id": "age", "label": "Age", "type": "number"},
                    {"id": "biological_sex", "label": "Biological Sex", "type": "select", "options": ["male","female","other"]},
                    {"id": "body_fat_pct", "label": "Body Fat %", "type": "number", "unit": "%", "optional": True},
                    {"id": "waist_cm", "label": "Waist circumference (cm)", "type": "number", "unit": "cm", "optional": True},
                    {"id": "hip_cm", "label": "Hip circumference (cm)", "type": "number", "unit": "cm", "optional": True},
                ],
            },
            {
                "id": "vitals",
                "title": "Vital Signs",
                "icon": "heart",
                "fields": [
                    {"id": "resting_heart_rate", "label": "Resting Heart Rate (bpm)", "type": "number", "optional": True},
                    {"id": "systolic_bp", "label": "Systolic Blood Pressure", "type": "number", "optional": True},
                    {"id": "diastolic_bp", "label": "Diastolic Blood Pressure", "type": "number", "optional": True},
                    {"id": "fasting_glucose", "label": "Fasting Blood Glucose (mmol/L)", "type": "number", "optional": True},
                ],
            },
            {
                "id": "lifestyle",
                "title": "Lifestyle",
                "icon": "activity",
                "fields": [
                    {"id": "activity_level", "label": "Activity Level", "type": "select", "options": ["sedentary","light","moderate","active","athlete"]},
                    {"id": "exercise_days_per_week", "label": "Exercise days per week", "type": "number"},
                    {"id": "sleep_hours", "label": "Average sleep (hours)", "type": "number"},
                    {"id": "water_litres_per_day", "label": "Water intake (litres/day)", "type": "number"},
                    {"id": "smoker", "label": "Do you smoke?", "type": "boolean"},
                    {"id": "alcohol_units_per_week", "label": "Alcohol units per week", "type": "number"},
                ],
            },
            {
                "id": "medical",
                "title": "Medical History",
                "icon": "clipboard",
                "fields": [
                    {"id": "diagnosed_conditions", "label": "Diagnosed conditions", "type": "tags"},
                    {"id": "medications", "label": "Current medications", "type": "tags"},
                    {"id": "family_history", "label": "Family health history", "type": "tags"},
                    {"id": "diet_type", "label": "Diet type", "type": "select", "options": ["omnivore","vegetarian","vegan","paleo","keto","mediterranean","other"]},
                    {"id": "meal_frequency", "label": "Meals per day", "type": "number"},
                    {"id": "intermittent_fasting", "label": "Do you practice intermittent fasting?", "type": "boolean"},
                ],
            },
        ],
        "psychological_sections": [
            {
                "id": "personality",
                "title": "Personality Profile",
                "subtitle": "Rate yourself 1 (low) to 10 (high)",
                "icon": "brain",
                "fields": [
                    {"id": "openness", "label": "Openness to new experiences", "type": "slider", "description": "Curiosity, creativity, willingness to try new things"},
                    {"id": "conscientiousness", "label": "Conscientiousness", "type": "slider", "description": "Organisation, discipline, goal-directedness"},
                    {"id": "extraversion", "label": "Extraversion", "type": "slider", "description": "Sociability, assertiveness, positive emotions"},
                    {"id": "agreeableness", "label": "Agreeableness", "type": "slider", "description": "Compassion, cooperation, trust in others"},
                    {"id": "neuroticism", "label": "Emotional reactivity", "type": "slider", "description": "Tendency to experience negative emotions"},
                ],
            },
            {
                "id": "mental_health",
                "title": "Mental Wellness",
                "subtitle": "Rate your current state 1 (low) to 10 (high)",
                "icon": "heart",
                "fields": [
                    {"id": "stress_level", "label": "Current stress level", "type": "slider", "description": "1 = very calm, 10 = extremely stressed"},
                    {"id": "anxiety_level", "label": "Anxiety level", "type": "slider", "description": "1 = no anxiety, 10 = severe anxiety"},
                    {"id": "mood_stability", "label": "Mood stability", "type": "slider", "description": "1 = very unstable, 10 = very stable"},
                    {"id": "motivation_level", "label": "Motivation & drive", "type": "slider", "description": "1 = no motivation, 10 = highly motivated"},
                    {"id": "self_esteem", "label": "Self-esteem", "type": "slider", "description": "1 = very low, 10 = very high"},
                    {"id": "social_connection", "label": "Social connection", "type": "slider", "description": "1 = very isolated, 10 = deeply connected"},
                    {"id": "purpose_clarity", "label": "Sense of purpose", "type": "slider", "description": "1 = no direction, 10 = crystal clear purpose"},
                ],
            },
            {
                "id": "context",
                "title": "Context & Goals",
                "icon": "target",
                "fields": [
                    {"id": "mindfulness_practice", "label": "Do you have a mindfulness practice?", "type": "boolean"},
                    {"id": "therapy_current", "label": "Are you currently in therapy?", "type": "boolean"},
                    {"id": "trauma_history", "label": "Have you experienced significant trauma?", "type": "boolean"},
                    {"id": "primary_mental_goal", "label": "Primary mental health goal", "type": "text", "placeholder": "e.g. reduce anxiety, improve focus, build confidence"},
                    {"id": "biggest_mental_challenge", "label": "Biggest mental challenge right now", "type": "text", "placeholder": "e.g. overthinking, low energy, relationship stress"},
                ],
            },
        ],
    }
