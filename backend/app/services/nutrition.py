"""Nutrition service — USDA FoodData Central integration + food-as-medicine logic."""

from typing import Any

import httpx

from app.core.config import settings

# ── Healing food database (seed data, expandable) ─────────────────────────────
HEALING_FOODS: dict[str, dict[str, Any]] = {
    "turmeric": {
        "properties": ["anti-inflammatory", "antioxidant", "liver-support"],
        "active_compound": "curcumin",
        "best_for": ["inflammation", "joint-pain", "gut-health"],
        "preparation": "Combine with black pepper and healthy fat to enhance absorption.",
    },
    "ginger": {
        "properties": ["anti-nausea", "anti-inflammatory", "digestive"],
        "active_compound": "gingerol",
        "best_for": ["nausea", "digestion", "circulation"],
        "preparation": "Fresh ginger tea or added raw to smoothies.",
    },
    "blueberries": {
        "properties": ["antioxidant", "brain-health", "anti-aging"],
        "active_compound": "anthocyanins",
        "best_for": ["cognitive-function", "oxidative-stress", "heart-health"],
        "preparation": "Raw, frozen, or in smoothies. Avoid cooking to preserve anthocyanins.",
    },
    "leafy-greens": {
        "properties": ["alkalizing", "mineral-rich", "detoxifying"],
        "active_compound": "chlorophyll, folate, magnesium",
        "best_for": ["detox", "energy", "bone-health"],
        "preparation": "Lightly steamed or raw. Rotate varieties weekly.",
    },
    "fermented-foods": {
        "properties": ["probiotic", "gut-microbiome", "immune-support"],
        "active_compound": "live cultures",
        "best_for": ["gut-health", "immunity", "mental-health"],
        "preparation": "Unpasteurized kimchi, sauerkraut, kefir, or miso.",
    },
    "adaptogens": {
        "properties": ["stress-modulating", "adrenal-support", "energy"],
        "active_compound": "withanolides (ashwagandha), ginsenosides (ginseng)",
        "best_for": ["stress", "fatigue", "hormonal-balance"],
        "preparation": "As tincture, powder in smoothies, or capsule form.",
    },
}

DETOX_FOODS: list[str] = [
    "cilantro", "chlorella", "spirulina", "dandelion-root",
    "milk-thistle", "beets", "garlic", "lemon", "artichoke",
]

ANTI_INFLAMMATORY_PROTOCOL: list[dict[str, Any]] = [
    {"meal": "Breakfast", "foods": ["golden milk oatmeal", "blueberries", "walnuts"], "notes": "Add 1 tsp turmeric + pinch black pepper"},
    {"meal": "Lunch", "foods": ["wild salmon", "leafy greens salad", "olive oil dressing"], "notes": "Omega-3s reduce systemic inflammation"},
    {"meal": "Dinner", "foods": ["lentil soup", "roasted vegetables", "ginger tea"], "notes": "Plant protein + fiber supports gut lining"},
    {"meal": "Snacks", "foods": ["celery + almond butter", "green smoothie"], "notes": "Avoid processed sugar entirely"},
]


class NutritionService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.usda_api_base_url,
            timeout=30.0,
        )

    async def search_foods(self, query: str, page_size: int = 10) -> list[dict[str, Any]]:
        """Search USDA FoodData Central."""
        params = {
            "query": query,
            "pageSize": page_size,
            "api_key": settings.usda_api_key or "DEMO_KEY",
        }
        try:
            resp = await self._client.get("/foods/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("foods", [])
        except httpx.HTTPError:
            # Return mock data when API key not configured
            return _mock_food_search(query)

    async def get_food_details(self, fdc_id: int) -> dict[str, Any]:
        """Fetch full nutrient profile for a food item."""
        params = {"api_key": settings.usda_api_key or "DEMO_KEY"}
        try:
            resp = await self._client.get(f"/food/{fdc_id}", params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError:
            return {"fdc_id": fdc_id, "description": "Food details unavailable", "foodNutrients": []}

    def get_healing_foods(self, condition: str) -> list[dict[str, Any]]:
        """Return foods recommended for a specific health condition."""
        results = []
        for name, data in HEALING_FOODS.items():
            if condition.lower() in [b.lower() for b in data["best_for"]]:
                results.append({"name": name, **data})
        return results or list({"name": k, **v} for k, v in list(HEALING_FOODS.items())[:3])

    def get_meal_plan(self, focus: str = "anti-inflammatory", days: int = 7) -> list[dict[str, Any]]:
        """Generate a structured meal plan."""
        return [
            {
                "day": d + 1,
                "meals": ANTI_INFLAMMATORY_PROTOCOL,
                "total_calories": 1800 + (d % 3) * 50,
                "macros": {"protein_g": 85, "carbs_g": 220, "fat_g": 65, "fiber_g": 35},
                "healing_focus": focus,
            }
            for d in range(days)
        ]

    async def close(self) -> None:
        await self._client.aclose()


def _mock_food_search(query: str) -> list[dict[str, Any]]:
    return [
        {
            "fdcId": 1001,
            "description": f"{query.title()} (mock result)",
            "brandOwner": None,
            "foodCategory": "Whole Foods",
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 52, "unitName": "kcal"},
                {"nutrientName": "Protein", "value": 0.7, "unitName": "g"},
                {"nutrientName": "Fiber", "value": 2.4, "unitName": "g"},
            ],
        }
    ]


nutrition_service = NutritionService()
