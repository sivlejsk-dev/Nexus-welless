"""
Tests for the vector memory / RAG layer (Task 1.4).

Uses a temporary ChromaDB directory so tests are fully isolated.
"""

import tempfile
import pytest

import app.services.rag as rag_mod
from app.services.vector_memory import VectorMemoryService
from app.services.rag import RAGService, _extract_facts


@pytest.fixture()
def isolated_rag():
    """Return a RAGService wired to a fresh in-memory-like ChromaDB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vm = VectorMemoryService(persist_dir=tmpdir)
        rag = RAGService()
        # Patch module-level singleton so RAGService uses our isolated store
        original = rag_mod.vector_memory
        rag_mod.vector_memory = vm
        yield rag, vm
        rag_mod.vector_memory = original


# ── VectorMemoryService ───────────────────────────────────────────────────────

def test_store_and_retrieve_conversation(isolated_rag):
    rag, vm = isolated_rag
    uid = "u1"

    tid = vm.store_conversation_turn(
        uid,
        "What foods reduce inflammation?",
        "Turmeric, ginger, and wild salmon are top anti-inflammatory foods.",
        domain="nutrition",
        intent="question",
    )
    assert tid is not None

    stats = vm.get_stats(uid)
    assert stats["conversation_turns"] == 1
    assert stats["knowledge_items"] == 0


def test_store_and_retrieve_knowledge(isolated_rag):
    rag, vm = isolated_rag
    uid = "u2"

    kid = vm.store_knowledge(uid, "User is vegetarian and avoids gluten", domain="nutrition")
    assert kid is not None

    results = vm.search_knowledge(uid, "vegetarian diet", n_results=3)
    assert len(results) == 1
    assert results[0]["similarity"] > 0.5


def test_semantic_search_ranks_relevant_first(isolated_rag):
    rag, vm = isolated_rag
    uid = "u3"

    vm.store_conversation_turn(uid, "Tell me about Saturn return",
        "Saturn return at age 29-30 marks a major life transition.", domain="astrology")
    vm.store_conversation_turn(uid, "What is intermittent fasting?",
        "Intermittent fasting restricts eating to a specific window.", domain="nutrition")
    vm.store_conversation_turn(uid, "How does turmeric help inflammation?",
        "Curcumin in turmeric inhibits NF-kB inflammatory pathways.", domain="nutrition")

    results = vm.search_conversations(uid, "anti-inflammatory foods", n_results=3)
    assert len(results) >= 1
    # The turmeric/inflammation turn should rank highest
    assert "turmeric" in results[0]["document"].lower() or "inflam" in results[0]["document"].lower()


def test_upsert_idempotent(isolated_rag):
    rag, vm = isolated_rag
    uid = "u4"

    # Store the same turn twice — count should remain 1
    for _ in range(2):
        vm.store_conversation_turn(uid, "Same message", "Same response", domain="general")

    assert vm.get_stats(uid)["conversation_turns"] == 1


def test_domain_filter(isolated_rag):
    rag, vm = isolated_rag
    uid = "u5"

    vm.store_conversation_turn(uid, "What is my moon sign?",
        "Your moon sign governs emotional responses.", domain="astrology")
    vm.store_conversation_turn(uid, "Best protein sources?",
        "Legumes, eggs, and wild fish are excellent protein sources.", domain="nutrition")

    astro_results = vm.search_conversations(uid, "moon sign astrology", n_results=5, domain_filter="astrology")
    assert all(r["metadata"]["domain"] == "astrology" for r in astro_results)


def test_delete_user_data(isolated_rag):
    rag, vm = isolated_rag
    uid = "u6"

    vm.store_conversation_turn(uid, "Hello", "Hi there!", domain="general")
    vm.store_knowledge(uid, "User prefers morning workouts", domain="general")

    vm.delete_user_data(uid)

    # After deletion, new collections are empty
    assert vm.get_stats(uid)["conversation_turns"] == 0
    assert vm.get_stats(uid)["knowledge_items"] == 0


# ── RAGService ────────────────────────────────────────────────────────────────

def test_retrieve_context_empty_store(isolated_rag):
    rag, vm = isolated_rag
    ctx = rag.retrieve_context("new_user", "anything")
    assert ctx == ""


def test_retrieve_context_returns_block(isolated_rag):
    rag, vm = isolated_rag
    uid = "u7"

    vm.store_conversation_turn(uid,
        "I struggle with high cortisol and poor sleep",
        "Ashwagandha and magnesium glycinate before bed can lower cortisol significantly.",
        domain="nutrition")

    ctx = rag.retrieve_context(uid, "supplements for stress and sleep", domain="nutrition")
    assert "[Relevant memory" in ctx
    assert "cortisol" in ctx.lower() or "ashwagandha" in ctx.lower()


def test_store_turn_and_extract_knowledge(isolated_rag):
    rag, vm = isolated_rag
    uid = "u8"

    turn_id = rag.store_turn(uid, "I am vegan and I avoid processed sugar",
        "Great — a whole-food plant-based diet is excellent for longevity.",
        domain="nutrition", intent="statement")
    assert turn_id is not None

    kids = rag.extract_and_store_knowledge(uid,
        "I am vegan and I avoid processed sugar",
        "Great — a whole-food plant-based diet is excellent for longevity.",
        domain="nutrition")
    # Should extract at least the user-stated fact
    assert len(kids) >= 1

    stats = rag.get_memory_stats(uid)
    assert stats["conversation_turns"] == 1
    assert stats["knowledge_items"] >= 1


# ── Knowledge extraction heuristics ──────────────────────────────────────────

def test_extract_facts_user_statements():
    facts = _extract_facts(
        "I am vegetarian and I have been doing intermittent fasting for 3 months",
        "Omega-3 from algae oil is ideal for vegetarians.",
        "nutrition",
    )
    assert any("vegetarian" in f.lower() for f in facts)


def test_extract_facts_domain_keywords():
    facts = _extract_facts(
        "Tell me about options trading",
        "Delta measures the rate of change of an option's price relative to the underlying asset.",
        "finance",
    )
    assert any("delta" in f.lower() or "option" in f.lower() for f in facts)


def test_extract_facts_deduplication():
    # Same user statement repeated — should only appear once
    facts = _extract_facts(
        "I have high cortisol. I have high cortisol levels.",
        "Cortisol is a stress hormone.",
        "nutrition",
    )
    keys = [f.lower()[:60] for f in facts]
    assert len(keys) == len(set(keys))


def test_extract_facts_cap():
    # Should never return more than 6 facts
    long_msg = " ".join([
        "I am vegan. I have diabetes. I practice yoga. I avoid gluten.",
        "I take magnesium. I do intermittent fasting. I avoid caffeine.",
    ])
    facts = _extract_facts(long_msg, "Turmeric and omega-3 help with inflammation.", "nutrition")
    assert len(facts) <= 6
