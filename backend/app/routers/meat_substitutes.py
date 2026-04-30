"""Meat substitute endpoints — plant-based alternatives, recipes, and techniques."""

from fastapi import APIRouter, Query
from app.services.meat_substitutes import meat_substitute_service

router = APIRouter(prefix="/meat-substitutes", tags=["meat-substitutes"])


@router.get("/bases")
async def list_bases():
    """All plant-based protein bases with texture, prep, and nutrition info."""
    return meat_substitute_service.get_all_bases()


@router.get("/bases/{base_id}")
async def get_base(base_id: str):
    base = meat_substitute_service.get_base(base_id)
    if not base:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Base ingredient not found")
    return base


@router.get("/recipes")
async def list_recipes(craving: str | None = Query(None, description="e.g. bacon, burger, tuna, steak")):
    """All recipes, optionally filtered by meat craving."""
    if craving:
        return meat_substitute_service.find_by_craving(craving)
    return meat_substitute_service.get_all_recipes()


@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    recipe = meat_substitute_service.get_recipe(recipe_id)
    if not recipe:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/for/{meat_type}")
async def substitutes_for_meat(meat_type: str):
    """Get ranked plant-based substitutes for a specific meat (beef, chicken, bacon, fish, etc.)."""
    return {
        "meat_type": meat_type,
        "substitutes": meat_substitute_service.get_substitutes_for_meat(meat_type),
        "recipes": meat_substitute_service.find_by_craving(meat_type)["recipes"],
    }


@router.get("/techniques")
async def get_techniques():
    """Texture and flavor techniques that make plant proteins taste like meat."""
    return meat_substitute_service.get_techniques()


@router.get("/nutrition-comparison")
async def nutrition_comparison():
    """Side-by-side nutritional comparison of meat vs plant substitutes."""
    return meat_substitute_service.get_nutritional_comparison()
