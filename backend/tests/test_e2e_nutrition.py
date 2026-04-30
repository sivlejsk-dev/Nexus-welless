"""
Stage 9 — End-to-end pipeline validation for nutrition/wellness queries.

Tests the full system prompt construction pipeline without requiring a live
LLM key. Validates:
  - Correct domain detection
  - Reasoning engine activation for complex queries
  - NutritionExpertise context injection
  - Contraindication enforcement
  - RAG domain knowledge retrieval (with seeded store)
"""

import tempfile
import pytest

from app.services.conversation import classify_domain
from app.services.reasoning import is_complex_query, reasoning_service
from app.nexus_core.nutrition_expertise import nutrition_expertise, fm_reasoner
from app.services.nutrition import nutrition_service
from app.services.detox import detox_service
from app.services.knowledge_seeder import KnowledgeSeeder
from app.services.vector_memory import VectorMemoryService
import app.services.rag as rag_mod
from app.services.rag import RAGService


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def seeded_rag():
    """Provide a RAGService backed by a seeded ChromaDB store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vm = VectorMemoryService(persist_dir=tmpdir)
        seeder = KnowledgeSeeder(vm=vm)
        seeder.seed_all()
        original = rag_mod.vector_memory
        rag_mod.vector_memory = vm
        yield RAGService()
        rag_mod.vector_memory = original


# ── Domain detection ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("query,expected_domain", [
    ("I want to do a parasite cleanse", "detox"),
    ("What foods help with candida?", "nutrition"),
    ("Design a SIBO protocol for me", "nutrition"),
    ("What should I eat to support my liver during a detox?", "nutrition"),
    ("I think I have candida. What kills it?", "nutrition"),
    ("What herbs are safe for someone on warfarin?", "nutrition"),
    ("How do I manage Herxheimer reactions?", "detox"),
    ("What foods raise glutathione naturally?", "nutrition"),
    ("Design a 7-day gut healing protocol for leaky gut", "nutrition"),
    ("What supplements support methylation for MTHFR?", "nutrition"),
    ("What's the best anti-inflammatory diet for autoimmune disease?", "nutrition"),
    ("How do I balance blood sugar naturally?", "nutrition"),
    ("What adaptogens help with adrenal fatigue?", "nutrition"),
    ("What foods support thyroid function?", "nutrition"),
    ("Tell me about my Saturn return", "astrology"),
    ("What is an iron condor options strategy?", "finance"),
])
def test_domain_detection(query, expected_domain):
    detected = classify_domain(query)
    assert detected == expected_domain, f"Query: '{query}' → got '{detected}', expected '{expected_domain}'"


# ── Reasoning engine activation ───────────────────────────────────────────────

@pytest.mark.parametrize("query,should_trigger", [
    ("I want to do a parasite cleanse", True),
    ("Design a candida protocol for me", True),
    ("What is SIBO?", True),  # SIBO is a complex medical condition — reasoning warranted
    ("How do I manage Herxheimer reactions during a parasite cleanse?", True),
    ("What supplements support methylation for someone with MTHFR?", True),
    ("What's the best anti-inflammatory diet for autoimmune disease?", True),
    ("I want to do a 30-day vitality reset — where do I start?", True),
    ("What should I eat for breakfast?", False),
    ("What is turmeric?", False),
    ("Design a heavy metal detox protocol", True),
    ("What is the root cause of my fatigue and brain fog?", True),
    ("What is an iron condor?", True),  # iron condor is a complex options strategy
    ("How do I build an iron condor options strategy?", True),
])
def test_reasoning_triggers(query, should_trigger):
    result = is_complex_query(query)
    assert result == should_trigger, f"Query: '{query}' → is_complex={result}, expected {should_trigger}"


# ── NutritionExpertise context injection ──────────────────────────────────────

def test_parasite_query_injects_foods():
    ctx = nutrition_expertise.get_domain_context(
        "I want to do a parasite cleanse", {}
    )
    assert ctx != ""
    assert any(food in ctx.lower() for food in ["pumpkin", "garlic", "wormwood", "clove"])


def test_candida_query_injects_antifungals():
    ctx = nutrition_expertise.get_domain_context("I think I have candida", {})
    assert ctx != ""
    assert any(herb in ctx.lower() for herb in ["oregano", "berberine", "caprylic", "coconut"])


def test_leaky_gut_query_injects_repair_foods():
    ctx = nutrition_expertise.get_domain_context("I have leaky gut", {})
    assert ctx != ""
    assert any(food in ctx.lower() for food in ["bone broth", "glutamine", "collagen", "slippery"])


def test_user_condition_injected_into_context():
    ctx = nutrition_expertise.get_domain_context(
        "What should I eat?",
        {"conditions": ["candida"], "medications": []}
    )
    assert "candida" in ctx.lower()


def test_warfarin_interaction_flagged():
    ctx = nutrition_expertise.get_domain_context(
        "Should I take turmeric?",
        {"conditions": [], "medications": ["warfarin"]}
    )
    assert "warfarin" in ctx.lower() or "INTERACTION" in ctx


def test_no_nutrition_context_for_astrology():
    ctx = nutrition_expertise.get_domain_context(
        "Tell me about my Saturn return and moon sign",
        {"conditions": [], "medications": []}
    )
    # Should be empty — no nutrition keywords
    assert ctx == ""


# ── Root cause analysis ───────────────────────────────────────────────────────

def test_chronic_fatigue_bloating_brain_fog():
    result = nutrition_expertise.assess_symptoms(
        ["chronic fatigue", "bloating", "brain fog", "sugar cravings"]
    )
    causes = [r["root_cause"] for r in result["likely_root_causes"]]
    assert len(causes) >= 1
    assert any(c in causes for c in ["candida", "sibo", "leaky-gut", "insulin-resistance"])


def test_parasite_symptom_cluster():
    result = nutrition_expertise.assess_symptoms(
        ["anal itching", "teeth grinding", "fatigue", "bloating", "diarrhea"]
    )
    causes = [r["root_cause"] for r in result["likely_root_causes"]]
    assert "parasites" in causes


def test_adrenal_symptom_cluster():
    result = nutrition_expertise.assess_symptoms(
        ["morning fatigue", "afternoon crash", "salt cravings", "anxiety", "poor stress response"]
    )
    causes = [r["root_cause"] for r in result["likely_root_causes"]]
    assert "adrenal-fatigue" in causes


def test_deficiency_assessment_fatigue():
    result = nutrition_expertise.assess_symptoms(["fatigue", "brain fog", "depression"])
    deficiencies = [d["deficiency"] for d in result["possible_deficiencies"]]
    assert len(deficiencies) >= 1
    assert any(d in deficiencies for d in ["magnesium", "vitamin-d3", "vitamin-b12", "iron"])


# ── Protocol recommendation ───────────────────────────────────────────────────

def test_parasite_protocol_recommended():
    r = detox_service.recommend_protocol({"conditions": ["parasites"], "medications": []})
    assert r["id"] == "parasite-21day"
    assert len(r["phases"]) == 3


def test_candida_protocol_recommended():
    r = detox_service.recommend_protocol({"conditions": ["candida"], "medications": []})
    assert r["id"] == "candida-sibo-30day"


def test_leaky_gut_protocol_recommended():
    r = detox_service.recommend_protocol({"conditions": ["leaky gut"], "medications": []})
    assert r["id"] == "gut-5r-60day"


def test_pregnancy_gets_gentle_protocol():
    r = detox_service.recommend_protocol({"conditions": ["pregnancy"], "medications": []})
    assert r["id"] == "gentle-7day"


# ── Food lookups ──────────────────────────────────────────────────────────────

def test_glutathione_foods():
    results = nutrition_service.get_healing_foods("liver-support")
    names = [r["name"] for r in results]
    assert any(n in names for n in ["milk-thistle", "nac", "dandelion-root"])


def test_heavy_metal_foods():
    results = nutrition_service.get_healing_foods("heavy-metals")
    names = [r["name"] for r in results]
    assert "chlorella" in names
    assert "cilantro" in names


def test_blood_sugar_foods():
    results = nutrition_service.get_healing_foods("blood-sugar")
    names = [r["name"] for r in results]
    assert "berberine" in names


def test_sleep_foods():
    results = nutrition_service.get_healing_foods("sleep")
    names = [r["name"] for r in results]
    assert any(n in names for n in ["ashwagandha", "walnuts", "reishi"])


# ── RAG domain knowledge retrieval ───────────────────────────────────────────

def test_rag_retrieves_parasite_knowledge(seeded_rag):
    ctx = seeded_rag.retrieve_context("test-user", "parasite cleanse wormwood protocol")
    assert "[Domain knowledge]" in ctx
    assert "wormwood" in ctx.lower() or "parasite" in ctx.lower()


def test_rag_retrieves_berberine_knowledge(seeded_rag):
    ctx = seeded_rag.retrieve_context("test-user", "berberine blood sugar insulin resistance")
    assert "[Domain knowledge]" in ctx
    assert "berberine" in ctx.lower()


def test_rag_retrieves_contraindication_knowledge(seeded_rag):
    ctx = seeded_rag.retrieve_context("test-user", "warfarin herb drug interaction")
    assert "[Domain knowledge]" in ctx
    assert "warfarin" in ctx.lower()


def test_rag_retrieves_gut_protocol_knowledge(seeded_rag):
    ctx = seeded_rag.retrieve_context("test-user", "leaky gut 5R protocol repair")
    assert "[Domain knowledge]" in ctx


# ── Nutrition reasoning context ───────────────────────────────────────────────

def test_nutrition_reasoning_context_with_medications():
    ctx = reasoning_service.build_nutrition_reasoning_context(
        "I want to do a parasite cleanse",
        {"conditions": ["fatigue"], "medications": ["warfarin"], "dietary_preferences": ["vegan"]}
    )
    assert "warfarin" in ctx
    assert "INTERACTION" in ctx.upper() or "interaction" in ctx.lower()
    assert "vegan" in ctx.lower()


def test_nutrition_reasoning_context_empty_for_simple_query():
    ctx = reasoning_service.build_nutrition_reasoning_context(
        "What is turmeric?",
        {"conditions": [], "medications": []}
    )
    assert ctx == ""


# ── System prompt content ─────────────────────────────────────────────────────

def test_system_prompt_contains_functional_medicine_principles():
    from app.services.nexus import SYSTEM_PROMPT
    assert "Phase I" in SYSTEM_PROMPT
    assert "Phase II" in SYSTEM_PROMPT
    assert "Herxheimer" in SYSTEM_PROMPT
    assert any(kw in SYSTEM_PROMPT.lower() for kw in ["bioindividuality", "personalize", "one-size-fits-all"])
    assert "root cause" in SYSTEM_PROMPT.lower()
    assert "antiparasitic trinity" in SYSTEM_PROMPT.lower()
