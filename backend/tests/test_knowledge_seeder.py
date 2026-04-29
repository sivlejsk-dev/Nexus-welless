"""Tests for ChromaDB knowledge seeder (Stage 4)."""

import tempfile
import pytest
from app.services.vector_memory import VectorMemoryService
from app.services.knowledge_seeder import (
    KnowledgeSeeder, DOMAIN_USER_ID,
    PUBMED_FACTS, HERB_MONOGRAPHS, PROTOCOL_STEPS,
    FOOD_CONDITION_FACTS, CONTRAINDICATION_FACTS,
)


@pytest.fixture()
def isolated_seeder():
    with tempfile.TemporaryDirectory() as tmpdir:
        vm = VectorMemoryService(persist_dir=tmpdir)
        seeder = KnowledgeSeeder(vm=vm)
        yield seeder, vm


def test_corpus_sizes():
    assert len(PUBMED_FACTS) >= 15
    assert len(HERB_MONOGRAPHS) >= 10
    assert len(PROTOCOL_STEPS) >= 10
    assert len(FOOD_CONDITION_FACTS) >= 15
    assert len(CONTRAINDICATION_FACTS) >= 10


def test_seed_all_returns_counts(isolated_seeder):
    seeder, vm = isolated_seeder
    counts = seeder.seed_all()
    assert not counts.get("skipped")
    assert counts["pubmed_facts"] == len(PUBMED_FACTS)
    assert counts["herb_monographs"] == len(HERB_MONOGRAPHS)
    assert counts["protocol_steps"] == len(PROTOCOL_STEPS)
    assert counts["food_condition_facts"] == len(FOOD_CONDITION_FACTS)
    assert counts["contraindication_facts"] == len(CONTRAINDICATION_FACTS)


def test_seed_is_idempotent(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    result = seeder.seed_all()
    assert result.get("skipped") is True


def test_is_seeded_false_before_seeding(isolated_seeder):
    seeder, vm = isolated_seeder
    assert seeder.is_seeded() is False


def test_is_seeded_true_after_seeding(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    assert seeder.is_seeded() is True


def test_wormwood_parasite_retrieval(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    results = vm.search_knowledge(DOMAIN_USER_ID, "wormwood parasite cleanse", n_results=5)
    assert len(results) >= 1
    assert results[0]["similarity"] >= 0.5
    assert any("wormwood" in r["document"].lower() for r in results)


def test_curcumin_bioavailability_retrieval(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    results = vm.search_knowledge(DOMAIN_USER_ID, "curcumin bioavailability piperine", n_results=3)
    assert len(results) >= 1
    assert any("piperine" in r["document"].lower() or "curcumin" in r["document"].lower()
               for r in results)


def test_berberine_blood_sugar_retrieval(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    results = vm.search_knowledge(DOMAIN_USER_ID, "berberine blood sugar insulin", n_results=5)
    assert len(results) >= 1
    assert any("berberine" in r["document"].lower() for r in results)


def test_contraindication_warfarin_retrieval(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    results = vm.search_knowledge(DOMAIN_USER_ID, "warfarin drug interaction herb", n_results=5)
    assert len(results) >= 1
    assert any("warfarin" in r["document"].lower() for r in results)


def test_parasite_protocol_retrieval(isolated_seeder):
    seeder, vm = isolated_seeder
    seeder.seed_all()
    results = vm.search_knowledge(DOMAIN_USER_ID, "parasite cleanse protocol phases", n_results=5)
    assert len(results) >= 2
    assert any("parasite" in r["document"].lower() for r in results)


def test_rag_domain_context_retrieval(isolated_seeder):
    """RAGService should retrieve domain knowledge for all users."""
    import app.services.rag as rag_mod
    from app.services.rag import RAGService

    seeder, vm = isolated_seeder
    seeder.seed_all()

    original = rag_mod.vector_memory
    rag_mod.vector_memory = vm
    try:
        rag = RAGService()
        ctx = rag.retrieve_context("any_user_id", "wormwood parasite cleanse protocol")
        assert "[Domain knowledge]" in ctx
        assert "wormwood" in ctx.lower() or "parasite" in ctx.lower()
    finally:
        rag_mod.vector_memory = original
