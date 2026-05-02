"""Nutrition endpoints — food search, healing foods, meal plans, Nexus recommendations."""

import json

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.wellness import MealPlan, NutritionRecommendation
from app.services.nexus import nexus_service
from app.services.nutrition import nutrition_service

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/search")
async def search_foods(
    q: str = Query(..., min_length=2, description="Food name or ingredient"),
    limit: int = Query(10, ge=1, le=50),
):
    """Search the USDA FoodData Central database."""
    results = await nutrition_service.search_foods(q, page_size=limit)
    return {"query": q, "results": results, "count": len(results)}


@router.get("/food/{fdc_id}")
async def get_food(fdc_id: int):
    """Full nutrient profile for a specific food item."""
    return await nutrition_service.get_food_details(fdc_id)


@router.get("/healing-foods")
async def healing_foods(
    condition: str = Query(..., description="Health condition, e.g. inflammation, gut-health"),
):
    """Return foods recommended for a specific health condition."""
    foods = nutrition_service.get_healing_foods(condition)
    return {"condition": condition, "foods": foods}


@router.get("/meal-plan", response_model=list[MealPlan])
async def get_meal_plan(
    focus: str = Query("anti-inflammatory"),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized meal plan."""
    return nutrition_service.get_meal_plan(focus=focus, days=days)


@router.get("/recommendation", response_model=NutritionRecommendation)
async def get_recommendation(
    condition: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Nexus AI-powered food-as-medicine recommendation."""
    profile = current_user.profile
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_goals": json.loads(profile.health_goals or "[]"),
            "dietary_preferences": json.loads(profile.dietary_preferences or "[]"),
            "allergies": json.loads(profile.allergies or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
            "sun_sign": profile.sun_sign,
        }

    healing_foods = nutrition_service.get_healing_foods(condition)

    nexus_result = await nexus_service.personalized_recommendation(
        module="nutrition",
        user_profile=profile_dict,
        context={"condition": condition, "available_foods": [f["name"] for f in healing_foods]},
    )

    return NutritionRecommendation(
        condition=condition,
        foods=healing_foods,
        avoid=["refined sugar", "seed oils", "ultra-processed foods", "alcohol"],
        rationale=f"Foods selected for their evidence-based benefits for {condition}.",
        nexus_insight=nexus_result.get("recommendation"),
    )
