"""Schemas for wellness profile, meditation, detox, nutrition, and astrology."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


# ── Wellness Profile ──────────────────────────────────────────────────────────

class WellnessProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    birth_time: str | None = None          # "HH:MM"
    birth_location: str | None = None
    birth_lat: float | None = None
    birth_lon: float | None = None
    timezone: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    dietary_preferences: list[str] | None = None
    health_goals: list[str] | None = None
    allergies: list[str] | None = None
    conditions: list[str] | None = None


class WellnessProfileOut(WellnessProfileUpdate):
    sun_sign: str | None = None
    moon_sign: str | None = None
    rising_sign: str | None = None

    model_config = {"from_attributes": True}


# ── Meditation ────────────────────────────────────────────────────────────────

class MeditationGuide(BaseModel):
    id: str
    title: str
    description: str
    duration_minutes: int
    category: str          # breathwork | body-scan | visualization | mantra | sleep
    level: str             # beginner | intermediate | advanced
    tags: list[str] = []
    audio_url: str | None = None
    background_music: str | None = None
    voice_guidance: dict[str, Any] | None = None
    thumbnail_url: str | None = None
    script: list[str] | None = None


class MeditationSessionCreate(BaseModel):
    guide_id: str
    duration_seconds: int
    completed: bool = False
    mood_before: int | None = Field(None, ge=1, le=10)
    mood_after: int | None = Field(None, ge=1, le=10)
    notes: str | None = None


class MeditationSessionOut(MeditationSessionCreate):
    id: str
    started_at: str

    model_config = {"from_attributes": True}


# ── Nutrition ─────────────────────────────────────────────────────────────────

class FoodSearchResult(BaseModel):
    fdc_id: int
    description: str
    brand_owner: str | None = None
    food_category: str | None = None
    nutrients: list[dict[str, Any]] = []


class MealPlan(BaseModel):
    day: int
    meals: list[dict[str, Any]]
    total_calories: float
    macros: dict[str, float]
    healing_focus: str | None = None   # e.g. "anti-inflammatory", "gut-health"


class NutritionRecommendation(BaseModel):
    condition: str
    foods: list[dict[str, Any]]
    avoid: list[str]
    rationale: str
    nexus_insight: str | None = None


# ── Detox ─────────────────────────────────────────────────────────────────────

class DetoxProtocol(BaseModel):
    id: str
    name: str
    description: str
    duration_days: int
    intensity: str          # gentle | moderate | intensive
    phases: list[dict[str, Any]]
    contraindications: list[str] = []
    supplements: list[str] = []


class DetoxLogCreate(BaseModel):
    protocol_id: str
    day_number: int = Field(ge=1)
    symptoms: list[str] = []
    energy_level: int | None = Field(None, ge=1, le=10)
    notes: str | None = None


class DetoxLogOut(DetoxLogCreate):
    id: str
    logged_at: str

    model_config = {"from_attributes": True}


# ── Astrology ─────────────────────────────────────────────────────────────────

class BirthChartRequest(BaseModel):
    date_of_birth: date
    birth_time: str          # "HH:MM"
    birth_lat: float
    birth_lon: float
    timezone: str


class PlanetPosition(BaseModel):
    planet: str
    sign: str
    degree: float
    house: int | None = None
    retrograde: bool = False


class BirthChart(BaseModel):
    sun: PlanetPosition
    moon: PlanetPosition
    rising: PlanetPosition
    planets: list[PlanetPosition]
    houses: list[dict[str, Any]]
    aspects: list[dict[str, Any]]
    nexus_interpretation: str | None = None


class DailyHoroscope(BaseModel):
    sign: str
    date: str
    general: str
    love: str
    career: str
    health: str
    lucky_number: int
    lucky_color: str
    nexus_insight: str | None = None


# ── Nexus AI ──────────────────────────────────────────────────────────────────

class NexusRecommendationRequest(BaseModel):
    module: str    # nutrition | meditation | detox | astrology | general
    context: dict[str, Any] = {}
    user_message: str | None = None


class NexusRecommendationResponse(BaseModel):
    module: str
    recommendation: str
    action_items: list[str] = []
    references: list[str] = []
    confidence: float | None = None
