"""Tests for the meditation service recommendation and guide helpers."""

from app.services.meditation import meditation_service


def test_get_all_guides_returns_guides():
    guides = meditation_service.get_all_guides()
    assert isinstance(guides, list)
    assert len(guides) >= 10


def test_get_by_category_uses_category_map_order():
    guides = meditation_service.get_by_category("breathwork")
    assert guides
    assert guides[0]["id"] == "breathwork-box-beginner"
    assert all(g["category"] == "breathwork" for g in guides)


def test_get_by_level_filters_correctly():
    advanced = meditation_service.get_by_level("advanced")
    assert advanced
    assert all(g["level"] == "advanced" for g in advanced)


def test_get_voice_segments_returns_structure():
    segments = meditation_service.get_voice_segments("breathwork-box-beginner")
    assert isinstance(segments, list)
    assert segments[0]["text"].startswith("Welcome")


def test_recommend_for_profile_includes_relevant_guide_ids():
    profile = {"health_goals": ["sleep", "stress"], "mental_state": "anxious"}
    recommendations = meditation_service.recommend_for_profile(profile)
    ids = {g["id"] for g in recommendations}
    assert "breathwork-478-intermediate" in ids
    assert "mantra-loving-kindness-intermediate" in ids
    assert "bodyscan-yoga-nidra-advanced" in ids or "mantra-om-beginner" in ids
