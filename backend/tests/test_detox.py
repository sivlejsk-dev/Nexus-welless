"""Tests for expanded detox protocols (Stage 2)."""

import pytest
from app.services.detox import DETOX_PROTOCOLS, detox_service


def test_seven_protocols_exist():
    ids = [p["id"] for p in DETOX_PROTOCOLS]
    assert "gentle-7day" in ids
    assert "liver-21day" in ids
    assert "heavy-metal-30day" in ids
    assert "parasite-21day" in ids
    assert "candida-sibo-30day" in ids
    assert "gut-5r-60day" in ids
    assert "mold-mycotoxin-90day" in ids


def test_all_protocols_have_required_fields():
    required = {"id", "name", "description", "duration_days", "intensity",
                "contraindications", "supplements", "phases"}
    for p in DETOX_PROTOCOLS:
        missing = required - set(p.keys())
        assert not missing, f"{p['id']} missing: {missing}"


def test_all_phases_have_required_fields():
    required = {"phase", "days", "name", "focus", "eat", "avoid",
                "practices", "expected_symptoms"}
    for p in DETOX_PROTOCOLS:
        for phase in p["phases"]:
            missing = required - set(phase.keys())
            assert not missing, f"{p['id']} phase {phase.get('phase')} missing: {missing}"


def test_parasite_protocol_has_herxheimer_management():
    p = detox_service.get_protocol("parasite-21day")
    assert p is not None
    assert "herxheimer_management" in p
    assert "moon_phase_note" in p


def test_parasite_protocol_phases():
    p = detox_service.get_protocol("parasite-21day")
    assert len(p["phases"]) == 3
    phase_names = [ph["name"] for ph in p["phases"]]
    assert "Starve & Prepare" in phase_names
    assert "Active Kill Phase" in phase_names
    assert "Restore & Rebuild" in phase_names


def test_parasite_protocol_contains_trinity():
    p = detox_service.get_protocol("parasite-21day")
    supp_text = " ".join(p["supplements"]).lower()
    assert "wormwood" in supp_text
    assert "black walnut" in supp_text
    assert "clove" in supp_text


def test_candida_protocol_has_biofilm_disruptors():
    p = detox_service.get_protocol("candida-sibo-30day")
    supp_text = " ".join(p["supplements"]).lower()
    assert "nac" in supp_text or "serrapeptase" in supp_text


def test_gut_5r_has_five_phases():
    p = detox_service.get_protocol("gut-5r-60day")
    assert len(p["phases"]) == 5
    names = [ph["name"] for ph in p["phases"]]
    assert "Remove" in names
    assert "Replace" in names
    assert "Reinoculate" in names
    assert "Repair" in names
    assert "Rebalance" in names


def test_mold_protocol_has_critical_first_step():
    p = detox_service.get_protocol("mold-mycotoxin-90day")
    assert "critical_first_step" in p
    assert "mold exposure" in p["critical_first_step"].lower()


def test_get_day_guidance_parasite_phase2():
    g = detox_service.get_day_guidance("parasite-21day", 10)
    assert g is not None
    assert g["phase"] == "Active Kill Phase"
    assert "herxheimer_management" in g


def test_get_day_guidance_gut_5r_repair_phase():
    g = detox_service.get_day_guidance("gut-5r-60day", 50)
    assert g is not None
    assert g["phase"] == "Repair"
    assert any("glutamine" in s.lower() for s in g["supplements"])


def test_get_day_guidance_out_of_range():
    g = detox_service.get_day_guidance("gentle-7day", 99)
    assert g is None


def test_recommend_candida():
    r = detox_service.recommend_protocol({"conditions": ["candida"], "medications": []})
    assert r["id"] == "candida-sibo-30day"


def test_recommend_parasites():
    r = detox_service.recommend_protocol({"conditions": ["parasites"], "medications": []})
    assert r["id"] == "parasite-21day"


def test_recommend_mold():
    r = detox_service.recommend_protocol({"conditions": ["mold toxicity"], "medications": []})
    assert r["id"] == "mold-mycotoxin-90day"


def test_recommend_leaky_gut():
    r = detox_service.recommend_protocol({"conditions": ["leaky gut"], "medications": []})
    assert r["id"] == "gut-5r-60day"


def test_contraindication_blocks_intensive_for_pregnancy():
    r = detox_service.recommend_protocol({"conditions": ["pregnancy"], "medications": []})
    assert r["id"] == "gentle-7day"


def test_check_contraindications_pregnancy():
    flagged = detox_service.check_contraindications("parasite-21day",
                                                     {"conditions": ["pregnancy"], "medications": []})
    assert len(flagged) >= 1
    assert any("pregnancy" in f.lower() for f in flagged)


def test_check_contraindications_clean_profile():
    flagged = detox_service.check_contraindications("gentle-7day",
                                                     {"conditions": ["fatigue"], "medications": []})
    assert flagged == []
