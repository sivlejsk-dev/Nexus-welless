"""Detox protocol library and progress tracking logic."""

from typing import Any

DETOX_PROTOCOLS: list[dict[str, Any]] = [
    {
        "id": "gentle-7day",
        "name": "7-Day Gentle Cleanse",
        "description": "A whole-foods reset that eliminates common inflammatory triggers while supporting liver and gut function.",
        "duration_days": 7,
        "intensity": "gentle",
        "contraindications": ["pregnancy", "eating-disorders", "underweight"],
        "supplements": ["milk thistle", "probiotics", "magnesium glycinate", "vitamin C"],
        "phases": [
            {
                "phase": 1,
                "days": "1-2",
                "name": "Preparation",
                "focus": "Eliminate caffeine, alcohol, sugar, gluten, and dairy",
                "eat": ["fruits", "vegetables", "brown rice", "lentils", "herbal teas"],
                "avoid": ["coffee", "alcohol", "processed foods", "refined sugar"],
                "practices": ["dry brushing", "10-min morning walk", "journaling"],
                "expected_symptoms": ["mild headache", "fatigue", "cravings"],
            },
            {
                "phase": 2,
                "days": "3-5",
                "name": "Deep Cleanse",
                "focus": "Maximize liver and lymphatic support",
                "eat": ["leafy greens", "beets", "lemon water", "garlic", "cilantro", "dandelion tea"],
                "avoid": ["all animal products", "oils except flaxseed"],
                "practices": ["epsom salt bath", "rebounding", "castor oil pack"],
                "expected_symptoms": ["increased energy by day 4", "clearer skin", "improved sleep"],
            },
            {
                "phase": 3,
                "days": "6-7",
                "name": "Reintegration",
                "focus": "Slowly reintroduce foods and assess reactions",
                "eat": ["wild fish", "eggs", "fermented foods", "healthy fats"],
                "avoid": ["gluten", "dairy", "alcohol"],
                "practices": ["food journal", "gratitude practice", "gentle yoga"],
                "expected_symptoms": ["clarity", "lightness", "improved digestion"],
            },
        ],
    },
    {
        "id": "liver-21day",
        "name": "21-Day Liver Reset",
        "description": "A structured protocol targeting liver regeneration, bile flow optimization, and metabolic reset.",
        "duration_days": 21,
        "intensity": "moderate",
        "contraindications": ["pregnancy", "liver-disease-advanced", "medications-requiring-food"],
        "supplements": ["NAC", "alpha-lipoic acid", "milk thistle", "B-complex", "zinc"],
        "phases": [
            {
                "phase": 1,
                "days": "1-7",
                "name": "Elimination",
                "focus": "Remove all liver stressors",
                "eat": ["cruciferous vegetables", "beets", "artichokes", "lemon", "turmeric"],
                "avoid": ["alcohol", "caffeine", "sugar", "processed foods", "seed oils"],
                "practices": ["morning lemon water", "castor oil packs", "infrared sauna"],
                "expected_symptoms": ["detox headaches", "fatigue", "emotional releases"],
            },
            {
                "phase": 2,
                "days": "8-14",
                "name": "Regeneration",
                "focus": "Provide liver-building nutrients",
                "eat": ["eggs", "wild salmon", "liver (organic)", "beets", "leafy greens"],
                "avoid": ["alcohol", "sugar", "processed foods"],
                "practices": ["coffee enema (optional)", "rebounding", "breathwork"],
                "expected_symptoms": ["increased energy", "better sleep", "weight loss"],
            },
            {
                "phase": 3,
                "days": "15-21",
                "name": "Optimization",
                "focus": "Establish sustainable liver-supportive habits",
                "eat": ["Mediterranean-style diet", "bitter greens", "fermented foods"],
                "avoid": ["alcohol", "refined sugar"],
                "practices": ["daily movement", "stress management", "sleep optimization"],
                "expected_symptoms": ["mental clarity", "stable energy", "improved skin"],
            },
        ],
    },
    {
        "id": "heavy-metal-30day",
        "name": "30-Day Heavy Metal Detox",
        "description": "Targeted protocol for mobilizing and safely eliminating heavy metals using food-based chelators.",
        "duration_days": 30,
        "intensity": "intensive",
        "contraindications": ["pregnancy", "kidney-disease", "amalgam-fillings-recent-removal"],
        "supplements": ["chlorella", "spirulina", "modified citrus pectin", "DMSA (medical supervision)", "glutathione"],
        "phases": [
            {
                "phase": 1,
                "days": "1-10",
                "name": "Binding Preparation",
                "focus": "Prepare elimination pathways before mobilizing metals",
                "eat": ["high-fiber foods", "cilantro", "garlic", "onions", "sulfur-rich vegetables"],
                "avoid": ["fish high in mercury", "alcohol", "sugar"],
                "practices": ["sauna", "epsom salt baths", "adequate hydration (3L/day)"],
                "expected_symptoms": ["fatigue", "brain fog (temporary)", "digestive changes"],
            },
            {
                "phase": 2,
                "days": "11-25",
                "name": "Active Chelation",
                "focus": "Mobilize and bind heavy metals",
                "eat": ["cilantro smoothies", "chlorella", "wild blueberries", "Atlantic dulse"],
                "avoid": ["all fish", "alcohol", "sugar", "processed foods"],
                "practices": ["daily sauna", "rebounding", "castor oil packs"],
                "expected_symptoms": ["possible symptom flare (metals mobilizing)", "improved cognition after week 3"],
            },
            {
                "phase": 3,
                "days": "26-30",
                "name": "Restoration",
                "focus": "Replenish minerals displaced during chelation",
                "eat": ["mineral-rich foods", "bone broth", "sea vegetables", "organ meats"],
                "avoid": ["alcohol", "sugar"],
                "practices": ["mineral baths", "grounding/earthing", "sleep prioritization"],
                "expected_symptoms": ["significant energy improvement", "mental clarity", "reduced inflammation"],
            },
        ],
    },
]


class DetoxService:
    def get_all_protocols(self) -> list[dict[str, Any]]:
        return DETOX_PROTOCOLS

    def get_protocol(self, protocol_id: str) -> dict[str, Any] | None:
        return next((p for p in DETOX_PROTOCOLS if p["id"] == protocol_id), None)

    def get_day_guidance(self, protocol_id: str, day: int) -> dict[str, Any] | None:
        protocol = self.get_protocol(protocol_id)
        if not protocol:
            return None

        for phase in protocol["phases"]:
            start, end = map(int, phase["days"].split("-"))
            if start <= day <= end:
                return {
                    "protocol": protocol["name"],
                    "day": day,
                    "phase": phase["name"],
                    "focus": phase["focus"],
                    "eat": phase["eat"],
                    "avoid": phase["avoid"],
                    "practices": phase["practices"],
                    "expected_symptoms": phase["expected_symptoms"],
                    "supplements": protocol["supplements"],
                }
        return None

    def recommend_protocol(self, profile: dict[str, Any]) -> dict[str, Any]:
        goals = [g.lower() for g in profile.get("health_goals", [])]
        conditions = [c.lower() for c in profile.get("conditions", [])]

        if any("heavy metal" in g or "metal" in g for g in goals + conditions):
            return self.get_protocol("heavy-metal-30day") or DETOX_PROTOCOLS[0]
        if any("liver" in g or "alcohol" in g for g in goals + conditions):
            return self.get_protocol("liver-21day") or DETOX_PROTOCOLS[0]
        return self.get_protocol("gentle-7day") or DETOX_PROTOCOLS[0]


detox_service = DetoxService()
