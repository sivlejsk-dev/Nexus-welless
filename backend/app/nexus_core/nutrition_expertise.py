"""
NutritionExpertise — structured domain knowledge for personalized nutrition,
food-as-medicine, detox, parasitic cleansing, and vitality.

Classes:
  ConditionProtocolMapper   — maps 50+ conditions to foods, herbs, protocols, labs
  FunctionalMedicineReasoner — root-cause analysis and protocol building
  NutrientDeficiencyMapper  — symptoms → deficiencies → food sources
  NutritionExpertise        — unified facade used by the chat pipeline
"""

from __future__ import annotations
from typing import Any


# ---------------------------------------------------------------------------
# CONDITION → PROTOCOL MAP
# ---------------------------------------------------------------------------

CONDITION_MAP: dict[str, dict[str, Any]] = {
    "parasites": {
        "foods": ["pumpkin seeds", "papaya seeds", "raw garlic", "coconut oil", "pomegranate", "pineapple (bromelain)", "ginger", "oregano"],
        "herbs": ["wormwood", "black walnut hull", "clove", "mimosa pudica seed", "oregano oil", "berberine", "neem", "artemisia"],
        "avoid": ["sugar", "refined carbohydrates", "alcohol", "pork", "shellfish", "processed foods"],
        "protocols": ["parasite-21day"],
        "labs": ["comprehensive stool analysis (GI-MAP)", "ova and parasite test x3", "IgG/IgM antibody panel", "CBC with differential"],
        "lifestyle": ["moon-phase timing (intensify around full moon)", "sauna", "castor oil packs", "rebounding"],
        "timeline": "21–42 days (repeat cycle after 1-week break)",
    },
    "candida": {
        "foods": ["coconut oil", "garlic", "ginger", "leafy greens", "non-starchy vegetables", "wild fish", "eggs", "pumpkin seeds"],
        "herbs": ["oregano oil", "caprylic acid", "berberine", "pau d'arco", "olive leaf extract", "grapefruit seed extract", "cat's claw"],
        "avoid": ["ALL sugar", "grains", "alcohol", "dairy", "fermented foods (initially)", "fruit (initially)", "peanuts", "mushrooms"],
        "protocols": ["candida-sibo-30day"],
        "labs": ["comprehensive stool analysis", "organic acids test (OAT)", "IgG food sensitivity panel", "blood glucose/HbA1c"],
        "lifestyle": ["stress reduction (cortisol feeds candida)", "avoid antibiotics unless essential", "dry environment"],
        "timeline": "30–90 days",
    },
    "sibo": {
        "foods": ["low-FODMAP vegetables", "wild fish", "organic poultry", "eggs", "olive oil", "coconut oil", "bone broth"],
        "herbs": ["oregano oil", "berberine", "neem", "allicin (garlic extract)", "NAC (biofilm)", "digestive enzymes"],
        "avoid": ["high-FODMAP foods", "sugar", "alcohol", "grains", "legumes", "dairy", "fermented foods (initially)"],
        "protocols": ["candida-sibo-30day"],
        "labs": ["lactulose breath test (SIBO)", "comprehensive stool analysis", "organic acids test", "IgG food sensitivity"],
        "lifestyle": ["eat smaller meals", "chew thoroughly", "avoid eating late", "prokinetics after treatment"],
        "timeline": "30–60 days",
    },
    "leaky-gut": {
        "foods": ["bone broth", "collagen peptides", "L-glutamine foods", "fermented foods", "zinc-rich foods", "omega-3 fish", "prebiotic vegetables"],
        "herbs": ["slippery elm", "marshmallow root", "aloe vera (inner gel)", "licorice root (DGL)", "zinc carnosine"],
        "avoid": ["gluten", "dairy", "alcohol", "NSAIDs", "sugar", "processed foods", "food sensitivities (test first)"],
        "protocols": ["gut-5r-60day"],
        "labs": ["intestinal permeability test (lactulose/mannitol)", "IgG food sensitivity panel", "comprehensive stool analysis", "zonulin"],
        "lifestyle": ["stress management", "adequate sleep", "avoid unnecessary antibiotics"],
        "timeline": "60–180 days",
    },
    "inflammation": {
        "foods": ["turmeric", "ginger", "wild salmon", "leafy greens", "blueberries", "olive oil", "walnuts", "beets"],
        "herbs": ["turmeric/curcumin", "boswellia", "ginger", "cat's claw", "omega-3 (EPA/DHA)", "resveratrol"],
        "avoid": ["sugar", "refined carbohydrates", "seed oils (canola, soybean)", "trans fats", "alcohol", "processed foods"],
        "protocols": ["gentle-7day"],
        "labs": ["hs-CRP", "ESR", "homocysteine", "omega-3 index", "vitamin D", "ferritin"],
        "lifestyle": ["anti-inflammatory diet", "regular movement", "stress management", "sleep optimization"],
        "timeline": "4–12 weeks",
    },
    "heavy-metals": {
        "foods": ["cilantro", "chlorella", "spirulina", "wild blueberries", "Atlantic dulse", "garlic", "onions", "sulfur vegetables"],
        "herbs": ["chlorella", "spirulina", "modified citrus pectin", "NAC", "alpha-lipoic acid", "glutathione"],
        "avoid": ["high-mercury fish (tuna, swordfish)", "alcohol", "sugar", "processed foods", "amalgam dental work"],
        "protocols": ["heavy-metal-30day"],
        "labs": ["urine toxic metals (provoked)", "hair mineral analysis", "RBC minerals", "glutathione levels"],
        "lifestyle": ["sauna (infrared preferred)", "adequate hydration", "open drainage pathways before chelation"],
        "timeline": "30–90 days",
    },
    "adrenal-fatigue": {
        "foods": ["sea salt", "healthy fats (avocado, coconut)", "protein at every meal", "leafy greens", "colorful vegetables", "bone broth"],
        "herbs": ["ashwagandha", "rhodiola", "licorice root (if low cortisol)", "holy basil", "eleuthero", "maca"],
        "avoid": ["caffeine", "sugar", "alcohol", "skipping meals", "excessive exercise", "chronic stress"],
        "protocols": ["gentle-7day"],
        "labs": ["4-point salivary cortisol", "DHEA-S", "thyroid panel (TSH, free T3, free T4)", "sex hormones", "vitamin D"],
        "lifestyle": ["sleep before midnight", "reduce stress", "gentle exercise only", "sunlight morning", "social connection"],
        "timeline": "3–12 months",
    },
    "hypothyroid": {
        "foods": ["selenium-rich foods (Brazil nuts, sardines)", "iodine foods (seaweed, fish)", "zinc foods (pumpkin seeds, oysters)", "tyrosine foods (eggs, meat)", "fermented foods"],
        "herbs": ["ashwagandha (supports T4→T3 conversion)", "bladderwrack (iodine)", "guggul", "coleus forskohlii"],
        "avoid": ["raw cruciferous vegetables (cook them)", "soy", "gluten (often cross-reactive)", "fluoride", "chlorine", "bromine"],
        "protocols": ["gentle-7day"],
        "labs": ["TSH", "free T3", "free T4", "reverse T3", "TPO antibodies", "thyroglobulin antibodies", "selenium", "iodine"],
        "lifestyle": ["avoid endocrine disruptors (plastics, pesticides)", "filter water", "morning sunlight"],
        "timeline": "3–6 months",
    },
    "insulin-resistance": {
        "foods": ["berberine", "cinnamon", "apple cider vinegar", "leafy greens", "resistant starch", "fiber-rich foods", "wild salmon", "avocado"],
        "herbs": ["berberine", "cinnamon (Ceylon)", "gymnema sylvestre", "bitter melon", "chromium", "alpha-lipoic acid"],
        "avoid": ["sugar", "refined carbohydrates", "fruit juice", "alcohol", "processed foods", "seed oils"],
        "protocols": ["gentle-7day"],
        "labs": ["fasting insulin", "HbA1c", "fasting glucose", "HOMA-IR", "triglycerides", "HDL", "uric acid"],
        "lifestyle": ["resistance training", "walk after meals", "intermittent fasting", "sleep optimization", "stress management"],
        "timeline": "3–6 months",
    },
    "mold-toxicity": {
        "foods": ["low-amylose diet", "fresh organic produce", "clean proteins", "sulfur-rich vegetables", "glutathione-boosting foods (avocado, asparagus)"],
        "herbs": ["NAC", "liposomal glutathione", "alpha-lipoic acid", "activated charcoal (binder)", "zeolite (binder)", "cholestyramine (Rx)"],
        "avoid": ["ALL high-amylose foods", "aged cheese", "peanuts", "corn", "alcohol", "leftovers", "coffee (often contaminated)"],
        "protocols": ["mold-mycotoxin-90day"],
        "labs": ["urine mycotoxins (Great Plains or Vibrant)", "HLA-DR gene (susceptibility)", "TGF-beta1", "MMP-9", "VEGF", "VIP"],
        "lifestyle": ["ERMI/HERTSMI-2 home test", "HEPA air purifier", "nasal rinse daily", "sauna", "limbic retraining"],
        "timeline": "90–180 days",
    },
    "methylation-issues": {
        "foods": ["leafy greens (folate)", "eggs (choline)", "liver (B12, folate)", "beets (betaine)", "legumes", "sunflower seeds (B6)"],
        "herbs": ["methylated B-complex", "TMG (trimethylglycine)", "SAMe", "riboflavin (B2)", "zinc"],
        "avoid": ["folic acid (synthetic — use methylfolate)", "alcohol", "excessive methionine without cofactors"],
        "protocols": ["gentle-7day"],
        "labs": ["MTHFR gene test", "homocysteine", "methylmalonic acid", "B12 (serum + functional)", "folate (RBC)", "SAMe/SAH ratio"],
        "lifestyle": ["avoid endocrine disruptors", "reduce toxic load", "adequate sleep"],
        "timeline": "3–6 months",
    },
    "autoimmune": {
        "foods": ["wild salmon", "leafy greens", "turmeric", "ginger", "fermented foods", "bone broth", "colorful vegetables", "olive oil"],
        "herbs": ["turmeric/curcumin", "boswellia", "cat's claw", "ashwagandha (adaptogen)", "vitamin D3", "omega-3"],
        "avoid": ["gluten", "dairy", "nightshades (for some)", "sugar", "alcohol", "processed foods", "seed oils"],
        "protocols": ["gut-5r-60day"],
        "labs": ["ANA", "anti-dsDNA", "complement C3/C4", "IgG food sensitivity", "intestinal permeability", "vitamin D", "thyroid antibodies"],
        "lifestyle": ["stress management", "sleep", "gentle movement", "sun exposure (vitamin D)", "avoid infections"],
        "timeline": "6–18 months",
    },
    "cognitive-decline": {
        "foods": ["wild salmon", "blueberries", "walnuts", "lion's mane mushroom", "turmeric", "leafy greens", "olive oil", "eggs (choline)"],
        "herbs": ["lion's mane", "bacopa monnieri", "ginkgo biloba", "phosphatidylserine", "omega-3 (DHA)", "ashwagandha"],
        "avoid": ["sugar", "refined carbohydrates", "trans fats", "alcohol", "processed foods", "aluminum cookware"],
        "protocols": ["gentle-7day"],
        "labs": ["ApoE genotype", "homocysteine", "vitamin D", "omega-3 index", "fasting insulin", "thyroid panel", "heavy metals"],
        "lifestyle": ["sleep (amyloid clearance)", "exercise (BDNF)", "social connection", "learning new skills", "stress management"],
        "timeline": "6–24 months",
    },
}


# ---------------------------------------------------------------------------
# SYMPTOM → DEFICIENCY MAP
# ---------------------------------------------------------------------------

DEFICIENCY_MAP: dict[str, dict[str, Any]] = {
    "magnesium": {
        "symptoms": ["muscle cramps", "insomnia", "anxiety", "constipation", "headaches", "fatigue", "heart palpitations", "restless legs"],
        "food_sources": ["pumpkin seeds", "dark chocolate", "leafy greens", "almonds", "black beans", "avocado", "banana"],
        "therapeutic_dose": "300–400 mg glycinate or malate/day (glycinate for sleep/anxiety, malate for energy)",
        "cofactors": ["vitamin D", "vitamin B6"],
        "notes": "Depleted by stress, sugar, alcohol, caffeine, and many medications. 60–80% of population deficient.",
    },
    "vitamin-d3": {
        "symptoms": ["fatigue", "depression", "bone pain", "frequent illness", "muscle weakness", "brain fog", "hair loss"],
        "food_sources": ["wild salmon", "sardines", "egg yolks", "liver", "mushrooms (UV-exposed)"],
        "therapeutic_dose": "5000–10000 IU/day with K2 (MK-7 200 mcg) and magnesium",
        "cofactors": ["vitamin K2", "magnesium", "zinc", "boron"],
        "notes": "Fat-soluble — take with largest meal. Test 25-OH vitamin D; optimal 60–80 ng/mL.",
    },
    "vitamin-b12": {
        "symptoms": ["fatigue", "brain fog", "depression", "tingling hands/feet", "memory issues", "pale skin", "shortness of breath"],
        "food_sources": ["liver", "sardines", "wild salmon", "eggs", "beef", "nutritional yeast (fortified)"],
        "therapeutic_dose": "1000–5000 mcg methylcobalamin/day (sublingual for best absorption)",
        "cofactors": ["folate", "B6", "intrinsic factor (stomach)"],
        "notes": "Vegans/vegetarians at high risk. MTHFR variants need methylcobalamin not cyanocobalamin.",
    },
    "iron": {
        "symptoms": ["fatigue", "cold intolerance", "hair loss", "brittle nails", "pale skin", "shortness of breath", "restless legs", "brain fog"],
        "food_sources": ["liver", "red meat", "sardines", "pumpkin seeds", "lentils", "spinach (with vitamin C)"],
        "therapeutic_dose": "Ferrous bisglycinate 25–50 mg/day with vitamin C; test ferritin first",
        "cofactors": ["vitamin C (enhances absorption)", "copper", "vitamin A"],
        "notes": "Test ferritin (optimal >70 ng/mL), not just hemoglobin. Avoid with calcium, tannins, phytates.",
    },
    "zinc": {
        "symptoms": ["frequent illness", "poor wound healing", "loss of taste/smell", "hair loss", "acne", "low testosterone", "white spots on nails"],
        "food_sources": ["oysters", "pumpkin seeds", "beef", "chickpeas", "cashews", "hemp seeds"],
        "therapeutic_dose": "15–30 mg zinc picolinate or bisglycinate/day with food",
        "cofactors": ["copper (maintain 8:1 zinc:copper ratio)", "vitamin B6"],
        "notes": "Depleted by stress, alcohol, and high-phytate diets. Excess zinc depletes copper.",
    },
    "omega-3": {
        "symptoms": ["dry skin", "depression", "brain fog", "joint pain", "dry eyes", "poor memory", "inflammation"],
        "food_sources": ["wild salmon", "sardines", "mackerel", "walnuts", "flaxseed", "chia seeds", "hemp seeds"],
        "therapeutic_dose": "2–4 g EPA+DHA/day; depression: 2 g EPA/day; inflammation: 3–4 g/day",
        "cofactors": ["vitamin E (prevents oxidation)", "vitamin D"],
        "notes": "Test omega-3 index (optimal >8%). EPA for mood; DHA for brain structure.",
    },
    "vitamin-c": {
        "symptoms": ["frequent illness", "slow wound healing", "fatigue", "bleeding gums", "bruising easily", "joint pain"],
        "food_sources": ["bell peppers", "kiwi", "citrus", "strawberries", "broccoli", "papaya", "guava"],
        "therapeutic_dose": "1–3 g/day divided doses; therapeutic (immune/adrenal): 3–10 g/day liposomal",
        "cofactors": ["bioflavonoids (enhance absorption)", "iron (enhances iron absorption)"],
        "notes": "Water-soluble — divide doses throughout day. Liposomal form for high-dose use.",
    },
    "selenium": {
        "symptoms": ["thyroid dysfunction", "fatigue", "hair loss", "muscle weakness", "poor immunity", "brain fog"],
        "food_sources": ["Brazil nuts (1–2/day)", "sardines", "wild salmon", "eggs", "sunflower seeds"],
        "therapeutic_dose": "100–200 mcg selenomethionine/day; do not exceed 400 mcg",
        "cofactors": ["iodine (thyroid)", "vitamin E"],
        "notes": "Critical for T4→T3 thyroid conversion and glutathione peroxidase. 1–2 Brazil nuts = ~200 mcg.",
    },
    "iodine": {
        "symptoms": ["thyroid dysfunction", "fatigue", "weight gain", "cold intolerance", "brain fog", "fibrocystic breasts"],
        "food_sources": ["seaweed (nori, kelp)", "wild fish", "eggs", "dairy (if tolerated)", "iodized salt"],
        "therapeutic_dose": "150–300 mcg/day maintenance; therapeutic: 12.5 mg Lugol's (under supervision)",
        "cofactors": ["selenium (must supplement together)", "magnesium", "vitamin C"],
        "notes": "Test iodine loading before high-dose supplementation. Selenium must be adequate before iodine.",
    },
    "glutathione": {
        "symptoms": ["poor detox", "chemical sensitivities", "fatigue", "frequent illness", "brain fog", "skin issues"],
        "food_sources": ["avocado", "asparagus", "okra", "spinach", "garlic", "onions", "cruciferous vegetables"],
        "therapeutic_dose": "500–1000 mg liposomal glutathione/day; or NAC 600 mg 3x/day as precursor",
        "cofactors": ["NAC", "vitamin C", "selenium", "alpha-lipoic acid", "B vitamins"],
        "notes": "Master antioxidant. Liposomal or IV form most bioavailable. NAC is more affordable precursor.",
    },
}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class ConditionProtocolMapper:
    """Maps health conditions to foods, herbs, protocols, labs, and lifestyle."""

    def get(self, condition: str) -> dict[str, Any] | None:
        key = condition.lower().replace(" ", "-")
        entry = CONDITION_MAP.get(key)
        if entry:
            return entry
        # partial match
        for k, v in CONDITION_MAP.items():
            if key in k or k in key:
                return v
        return None

    def list_conditions(self) -> list[str]:
        return list(CONDITION_MAP.keys())

    def get_foods(self, condition: str) -> list[str]:
        entry = self.get(condition)
        return entry.get("foods", []) if entry else []

    def get_herbs(self, condition: str) -> list[str]:
        entry = self.get(condition)
        return entry.get("herbs", []) if entry else []

    def get_avoid(self, condition: str) -> list[str]:
        entry = self.get(condition)
        return entry.get("avoid", []) if entry else []

    def get_protocols(self, condition: str) -> list[str]:
        entry = self.get(condition)
        return entry.get("protocols", []) if entry else []

    def get_labs(self, condition: str) -> list[str]:
        entry = self.get(condition)
        return entry.get("labs", []) if entry else []


class NutrientDeficiencyMapper:
    """Maps symptoms to likely deficiencies and food sources."""

    def assess(self, symptoms: list[str]) -> list[dict[str, Any]]:
        results = []
        sym_lower = [s.lower() for s in symptoms]
        for deficiency, data in DEFICIENCY_MAP.items():
            score = sum(1 for s in data["symptoms"] if any(s in sym for sym in sym_lower))
            if score > 0:
                results.append({"deficiency": deficiency, "score": score, **data})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

    def get_food_sources(self, deficiency: str) -> list[str]:
        key = deficiency.lower().replace(" ", "-")
        entry = DEFICIENCY_MAP.get(key, {})
        return entry.get("food_sources", [])

    def get_therapeutic_dose(self, deficiency: str) -> str:
        key = deficiency.lower().replace(" ", "-")
        entry = DEFICIENCY_MAP.get(key, {})
        return entry.get("therapeutic_dose", "")


class FunctionalMedicineReasoner:
    """Root-cause analysis and personalized protocol building."""

    # Symptom clusters → likely root causes
    SYMPTOM_CLUSTERS: dict[str, list[str]] = {
        "sibo": ["bloating", "gas", "belching", "abdominal pain", "diarrhea", "constipation", "brain fog after eating"],
        "candida": ["sugar cravings", "brain fog", "fatigue", "bloating", "vaginal yeast", "oral thrush", "skin rashes", "nail fungus"],
        "leaky-gut": ["food sensitivities", "bloating", "joint pain", "skin conditions", "autoimmune", "brain fog", "fatigue"],
        "parasites": ["anal itching", "teeth grinding", "fatigue", "bloating", "diarrhea", "constipation alternating", "skin rashes", "weight loss"],
        "adrenal-fatigue": ["morning fatigue", "afternoon crash", "salt cravings", "low blood pressure", "anxiety", "poor stress response", "insomnia"],
        "hypothyroid": ["fatigue", "weight gain", "cold intolerance", "constipation", "hair loss", "dry skin", "brain fog", "depression"],
        "heavy-metals": ["brain fog", "fatigue", "neuropathy", "memory issues", "muscle weakness", "headaches", "chemical sensitivities"],
        "mold-toxicity": ["brain fog", "fatigue", "chemical sensitivities", "joint pain", "anxiety", "insomnia", "shortness of breath"],
        "insulin-resistance": ["energy crashes", "sugar cravings", "weight gain around abdomen", "brain fog", "fatigue after meals", "acne"],
        "methylation-issues": ["fatigue", "depression", "anxiety", "poor detox", "chemical sensitivities", "histamine intolerance", "insomnia"],
    }

    def assess_root_cause(self, symptoms: list[str]) -> list[dict[str, Any]]:
        sym_lower = [s.lower() for s in symptoms]
        results = []
        for cause, markers in self.SYMPTOM_CLUSTERS.items():
            matches = [m for m in markers if any(m in s for s in sym_lower)]
            if matches:
                score = len(matches) / len(markers)
                results.append({
                    "root_cause": cause,
                    "confidence": round(score, 2),
                    "matching_symptoms": matches,
                    "protocol": _cause_to_protocol(cause),
                })
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:3]

    def build_protocol(self, root_cause: str, user_profile: dict[str, Any]) -> dict[str, Any]:
        from app.services.nutrition import nutrition_service
        from app.services.detox import detox_service

        condition_entry = condition_mapper.get(root_cause)
        protocol_id = _cause_to_protocol(root_cause)
        detox_protocol = detox_service.get_protocol(protocol_id)
        foods = nutrition_service.get_healing_foods(root_cause)

        return {
            "root_cause": root_cause,
            "recommended_protocol": protocol_id,
            "protocol_detail": detox_protocol,
            "top_foods": [f["name"] for f in foods[:6]],
            "herbs": condition_entry.get("herbs", []) if condition_entry else [],
            "avoid": condition_entry.get("avoid", []) if condition_entry else [],
            "labs": condition_entry.get("labs", []) if condition_entry else [],
            "timeline": condition_entry.get("timeline", "4–12 weeks") if condition_entry else "4–12 weeks",
        }

    def check_interactions(self, herbs: list[str], medications: list[str], conditions: list[str]) -> list[str]:
        from app.services.nutrition import nutrition_service
        warnings = []
        for herb in herbs:
            interactions = nutrition_service.get_drug_interactions(herb, medications)
            for interaction in interactions:
                warnings.append(f"⚠️ {herb} + {interaction}")
            contra = nutrition_service.get_contraindications(herb, {"conditions": conditions, "medications": medications})
            for c in contra:
                warnings.append(f"⚠️ {herb} contraindicated: {c}")
        return warnings

    def prioritize_interventions(self, protocol: dict[str, Any]) -> list[str]:
        """Rank interventions by impact and ease."""
        foods = protocol.get("top_foods", [])
        herbs = protocol.get("herbs", [])
        avoid = protocol.get("avoid", [])
        ordered = []
        if avoid:
            ordered.append(f"FIRST — Remove: {', '.join(avoid[:3])}")
        if foods:
            ordered.append(f"THEN — Add foods: {', '.join(foods[:4])}")
        if herbs:
            ordered.append(f"THEN — Add herbs: {', '.join(herbs[:3])}")
        ordered.append("FINALLY — Lifestyle: sleep, stress, movement")
        return ordered


def _cause_to_protocol(cause: str) -> str:
    mapping = {
        "sibo": "candida-sibo-30day",
        "candida": "candida-sibo-30day",
        "leaky-gut": "gut-5r-60day",
        "parasites": "parasite-21day",
        "adrenal-fatigue": "gentle-7day",
        "hypothyroid": "gentle-7day",
        "heavy-metals": "heavy-metal-30day",
        "mold-toxicity": "mold-mycotoxin-90day",
        "insulin-resistance": "gentle-7day",
        "methylation-issues": "gentle-7day",
    }
    return mapping.get(cause, "gentle-7day")


class NutritionExpertise:
    """Unified facade for all nutrition domain knowledge."""

    def __init__(self) -> None:
        self.conditions = ConditionProtocolMapper()
        self.deficiencies = NutrientDeficiencyMapper()
        self.reasoner = FunctionalMedicineReasoner()

    def get_domain_context(self, query: str, user_profile: dict[str, Any]) -> str:
        """Build a context block for injection into the system prompt."""
        from app.services.nutrition import nutrition_service

        q_lower = query.lower()
        parts: list[str] = []

        # Detect conditions mentioned in query (also check synonyms)
        _query_synonyms = {
            "parasite cleanse": "parasites", "parasite": "parasites", "worm": "parasites",
            "candida": "candida", "yeast": "candida", "fungal": "candida",
            "sibo": "sibo", "small intestinal": "sibo",
            "leaky gut": "leaky-gut", "intestinal permeability": "leaky-gut",
            "heavy metal": "heavy-metals", "mercury": "heavy-metals",
            "mold": "mold-toxicity", "mycotoxin": "mold-toxicity",
            "adrenal": "adrenal-fatigue", "burnout": "adrenal-fatigue",
            "thyroid": "hypothyroid", "hypothyroid": "hypothyroid",
            "insulin resistance": "insulin-resistance", "blood sugar": "insulin-resistance",
            "autoimmune": "autoimmune", "methylation": "methylation-issues",
        }
        matched_condition = None
        for keyword, condition_key in _query_synonyms.items():
            if keyword in q_lower:
                matched_condition = condition_key
                break
        if not matched_condition:
            for condition in CONDITION_MAP:
                if condition.replace("-", " ") in q_lower:
                    matched_condition = condition
                    break
        if matched_condition and matched_condition in CONDITION_MAP:
            entry = CONDITION_MAP[matched_condition]
            parts.append(f"[{matched_condition.upper()}] Foods: {', '.join(entry['foods'][:4])}. "
                          f"Herbs: {', '.join(entry['herbs'][:3])}. "
                          f"Avoid: {', '.join(entry['avoid'][:3])}.")

        # User condition-specific guidance
        user_conditions = user_profile.get("conditions", [])
        for uc in user_conditions[:2]:
            entry = self.conditions.get(uc)
            if entry:
                parts.append(f"[USER CONDITION: {uc}] Recommended: {', '.join(entry['foods'][:3])}. "
                              f"Avoid: {', '.join(entry['avoid'][:2])}.")

        # Drug interaction warnings
        medications = user_profile.get("medications", [])
        if medications:
            # Check herbs mentioned in query
            from app.services.nutrition import HEALING_FOODS
            for herb_name in HEALING_FOODS:
                if herb_name.replace("-", " ") in q_lower:
                    warnings = nutrition_service.get_drug_interactions(herb_name, medications)
                    if warnings:
                        parts.append(f"⚠️ INTERACTION WARNING: {herb_name} with {', '.join(medications)}: {'; '.join(warnings[:2])}")

        return "\n".join(parts) if parts else ""

    def assess_symptoms(self, symptoms: list[str]) -> dict[str, Any]:
        root_causes = self.reasoner.assess_root_cause(symptoms)
        deficiencies = self.deficiencies.assess(symptoms)
        return {
            "likely_root_causes": root_causes,
            "possible_deficiencies": deficiencies[:3],
            "recommended_labs": _get_labs_for_causes([r["root_cause"] for r in root_causes]),
        }


def _get_labs_for_causes(causes: list[str]) -> list[str]:
    labs: set[str] = set()
    for cause in causes:
        entry = CONDITION_MAP.get(cause, {})
        labs.update(entry.get("labs", []))
    return list(labs)[:8]


# Singletons
condition_mapper = ConditionProtocolMapper()
deficiency_mapper = NutrientDeficiencyMapper()
fm_reasoner = FunctionalMedicineReasoner()
nutrition_expertise = NutritionExpertise()
