"""Tests for the NutritionExpertise module (Stage 3)."""

import pytest
from app.nexus_core.nutrition_expertise import (
    nutrition_expertise, condition_mapper, deficiency_mapper, fm_reasoner,
    CONDITION_MAP, DEFICIENCY_MAP,
)


# ── ConditionProtocolMapper ───────────────────────────────────────────────────

def test_condition_map_has_minimum_entries():
    assert len(CONDITION_MAP) >= 10


def test_all_conditions_have_required_fields():
    required = {"foods", "herbs", "avoid", "protocols", "labs", "lifestyle", "timeline"}
    for name, entry in CONDITION_MAP.items():
        missing = required - set(entry.keys())
        assert not missing, f"{name} missing: {missing}"


def test_get_parasites_condition():
    entry = condition_mapper.get("parasites")
    assert entry is not None
    assert "wormwood" in entry["herbs"]
    assert "sugar" in entry["avoid"]
    assert "parasite-21day" in entry["protocols"]


def test_get_candida_condition():
    entry = condition_mapper.get("candida")
    assert entry is not None
    assert "oregano oil" in entry["herbs"]
    assert "candida-sibo-30day" in entry["protocols"]


def test_partial_match():
    entry = condition_mapper.get("leaky gut")
    assert entry is not None
    assert "gut-5r-60day" in entry["protocols"]


def test_get_foods():
    foods = condition_mapper.get_foods("inflammation")
    assert len(foods) >= 3
    assert any("turmeric" in f or "salmon" in f for f in foods)


def test_get_labs_parasites():
    labs = condition_mapper.get_labs("parasites")
    assert len(labs) >= 2
    assert any("stool" in lab.lower() for lab in labs)


# ── NutrientDeficiencyMapper ──────────────────────────────────────────────────

def test_deficiency_map_has_minimum_entries():
    assert len(DEFICIENCY_MAP) >= 8


def test_assess_fatigue_brain_fog():
    results = deficiency_mapper.assess(["fatigue", "brain fog", "depression"])
    assert len(results) >= 2
    deficiencies = [r["deficiency"] for r in results]
    assert any(d in deficiencies for d in ["magnesium", "vitamin-d3", "vitamin-b12", "iron"])


def test_assess_muscle_cramps_insomnia():
    results = deficiency_mapper.assess(["muscle cramps", "insomnia", "anxiety"])
    assert results[0]["deficiency"] == "magnesium"


def test_assess_returns_sorted_by_score():
    results = deficiency_mapper.assess(["fatigue", "brain fog", "muscle cramps", "insomnia", "anxiety"])
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_get_food_sources_magnesium():
    sources = deficiency_mapper.get_food_sources("magnesium")
    assert len(sources) >= 3
    assert any("pumpkin" in s or "leafy" in s or "dark chocolate" in s for s in sources)


def test_get_therapeutic_dose_vitamin_d3():
    dose = deficiency_mapper.get_therapeutic_dose("vitamin-d3")
    assert "IU" in dose
    assert "K2" in dose


# ── FunctionalMedicineReasoner ────────────────────────────────────────────────

def test_assess_root_cause_candida_symptoms():
    causes = fm_reasoner.assess_root_cause(["sugar cravings", "brain fog", "fatigue", "bloating", "vaginal yeast"])
    assert len(causes) >= 1
    top = causes[0]["root_cause"]
    assert top == "candida"


def test_assess_root_cause_parasite_symptoms():
    causes = fm_reasoner.assess_root_cause(["anal itching", "teeth grinding", "fatigue", "bloating"])
    names = [c["root_cause"] for c in causes]
    assert "parasites" in names


def test_assess_root_cause_returns_confidence():
    causes = fm_reasoner.assess_root_cause(["fatigue", "brain fog"])
    for c in causes:
        assert 0 <= c["confidence"] <= 1
        assert "matching_symptoms" in c


def test_build_protocol_parasites():
    protocol = fm_reasoner.build_protocol("parasites", {"conditions": [], "medications": []})
    assert protocol["root_cause"] == "parasites"
    assert protocol["recommended_protocol"] == "parasite-21day"
    assert len(protocol["top_foods"]) >= 3
    assert len(protocol["herbs"]) >= 3


def test_check_interactions_warfarin():
    warnings = fm_reasoner.check_interactions(["turmeric", "ginger"], ["warfarin"], [])
    assert len(warnings) >= 1
    assert any("warfarin" in w.lower() for w in warnings)


def test_check_interactions_no_medications():
    warnings = fm_reasoner.check_interactions(["turmeric"], [], [])
    assert isinstance(warnings, list)


def test_prioritize_interventions_order():
    protocol = {
        "top_foods": ["pumpkin seeds", "garlic", "coconut oil"],
        "herbs": ["wormwood", "black walnut"],
        "avoid": ["sugar", "alcohol"],
    }
    ordered = fm_reasoner.prioritize_interventions(protocol)
    assert len(ordered) >= 3
    assert "FIRST" in ordered[0]
    assert "Remove" in ordered[0]


# ── NutritionExpertise facade ─────────────────────────────────────────────────

def test_get_domain_context_parasite_query():
    ctx = nutrition_expertise.get_domain_context(
        "I want to do a parasite cleanse",
        {"conditions": [], "medications": []}
    )
    assert "PARASITES" in ctx or "parasite" in ctx.lower()


def test_get_domain_context_user_condition():
    ctx = nutrition_expertise.get_domain_context(
        "What should I eat?",
        {"conditions": ["candida"], "medications": []}
    )
    assert "candida" in ctx.lower()


def test_get_domain_context_drug_interaction_warning():
    ctx = nutrition_expertise.get_domain_context(
        "Should I take turmeric?",
        {"conditions": [], "medications": ["warfarin"]}
    )
    assert "warfarin" in ctx.lower() or "INTERACTION" in ctx


def test_assess_symptoms_returns_structure():
    result = nutrition_expertise.assess_symptoms(["fatigue", "brain fog", "bloating", "sugar cravings"])
    assert "likely_root_causes" in result
    assert "possible_deficiencies" in result
    assert "recommended_labs" in result
    assert len(result["likely_root_causes"]) >= 1
