"""Tests for the expanded healing foods knowledge base (Stage 1)."""

import pytest
from app.services.nutrition import HEALING_FOODS, nutrition_service


def test_minimum_entry_count():
    assert len(HEALING_FOODS) >= 40


def test_all_entries_have_required_fields():
    required = {"properties", "active_compounds", "best_for", "condition_synonyms",
                "contraindications", "dosing", "bioavailability_notes",
                "drug_interactions", "evidence_tier", "preparation"}
    for name, entry in HEALING_FOODS.items():
        missing = required - set(entry.keys())
        assert not missing, f"{name} missing fields: {missing}"


def test_all_entries_have_contraindications():
    for name, entry in HEALING_FOODS.items():
        assert entry["contraindications"], f"{name} has empty contraindications"


def test_all_entries_have_valid_evidence_tier():
    valid = {"RCT", "meta-analysis", "observational", "traditional"}
    for name, entry in HEALING_FOODS.items():
        assert entry["evidence_tier"] in valid, f"{name} has invalid tier: {entry['evidence_tier']}"


def test_parasite_lookup_returns_antiparasitic_herbs():
    results = nutrition_service.get_healing_foods("parasites")
    names = [r["name"] for r in results]
    assert len(results) >= 5
    assert "wormwood" in names
    assert "black-walnut-hull" in names
    assert "clove" in names


def test_synonym_resolution_ibs_to_gut_health():
    results = nutrition_service.get_healing_foods("ibs")
    assert len(results) >= 3
    names = [r["name"] for r in results]
    assert any(n in names for n in ["ginger", "slippery-elm", "l-glutamine", "aloe-vera"])


def test_synonym_resolution_arthritis_to_joint_pain():
    results = nutrition_service.get_healing_foods("arthritis")
    names = [r["name"] for r in results]
    assert len(results) >= 2
    assert any(n in names for n in ["turmeric", "ginger", "cat's-claw"])


def test_synonym_resolution_fatty_liver():
    results = nutrition_service.get_healing_foods("fatty-liver")
    names = [r["name"] for r in results]
    assert len(results) >= 3
    assert any(n in names for n in ["milk-thistle", "dandelion-root", "artichoke-leaf", "beets"])


def test_results_sorted_by_evidence_tier():
    results = nutrition_service.get_healing_foods("inflammation")
    tiers = [r.get("evidence_tier") for r in results]
    tier_rank = {"RCT": 0, "meta-analysis": 1, "observational": 2, "traditional": 3}
    ranks = [tier_rank.get(t, 4) for t in tiers]
    assert ranks == sorted(ranks), "Results not sorted by evidence tier"


def test_get_food_monograph_exact():
    mono = nutrition_service.get_food_monograph("turmeric")
    assert mono is not None
    assert mono["name"] == "turmeric"
    assert "curcumin" in mono["active_compounds"]
    assert "piperine" in mono["bioavailability_notes"]


def test_get_food_monograph_fuzzy():
    mono = nutrition_service.get_food_monograph("walnut")
    assert mono is not None
    assert "walnut" in mono["name"]


def test_get_food_monograph_missing():
    mono = nutrition_service.get_food_monograph("unicorn-root")
    assert mono is None


def test_get_bioavailability_stack_turmeric():
    stack = nutrition_service.get_bioavailability_stack("turmeric")
    assert "piperine" in stack.lower() or "black pepper" in stack.lower()


def test_get_bioavailability_stack_missing():
    stack = nutrition_service.get_bioavailability_stack("nonexistent-herb")
    assert stack == ""


def test_get_contraindications_pregnancy():
    profile = {"conditions": ["pregnancy"], "medications": []}
    contra = nutrition_service.get_contraindications("wormwood", profile)
    assert any("pregnancy" in c.lower() for c in contra)


def test_get_drug_interactions_warfarin():
    interactions = nutrition_service.get_drug_interactions("turmeric", ["warfarin"])
    assert len(interactions) >= 1
    assert any("warfarin" in i.lower() for i in interactions)


def test_get_drug_interactions_no_match():
    interactions = nutrition_service.get_drug_interactions("turmeric", ["penicillin"])
    assert interactions == []


def test_get_meal_plan_structure():
    plan = nutrition_service.get_meal_plan(focus="detox", days=3)
    assert len(plan) == 3
    for day in plan:
        assert "day" in day
        assert "meals" in day
        assert "healing_focus" in day
        assert day["healing_focus"] == "detox"


def test_candida_lookup():
    results = nutrition_service.get_healing_foods("candida")
    names = [r["name"] for r in results]
    assert len(results) >= 4
    assert any(n in names for n in ["oregano-oil", "berberine", "pau-darco", "olive-leaf-extract"])


def test_liver_support_lookup():
    results = nutrition_service.get_healing_foods("liver-support")
    names = [r["name"] for r in results]
    assert len(results) >= 4
    assert "milk-thistle" in names


def test_stress_lookup_with_synonym():
    results = nutrition_service.get_healing_foods("adrenal-fatigue")
    names = [r["name"] for r in results]
    assert len(results) >= 2
    assert any(n in names for n in ["ashwagandha", "rhodiola", "reishi"])
