# Nexus Nutrition & Wellness Training Plan

Goal: Make Nexus deeply expert in personalized nutrition, food-as-medicine, detox,
parasitic cleansing, and vitality — grounded in functional medicine and synthesized
research, with adaptive reasoning rather than static rules.

Each stage has a clear scope, test criteria, and a commit checkpoint.
Work through stages in order. Do not advance until the stage's tests pass.

---

## Stage 1 — Expand the Healing Foods Knowledge Base
**File:** `app/services/nutrition.py`
**Scope:** Grow `HEALING_FOODS` from 6 to 60+ entries with full schema.

### Tasks
- [ ] 1.1 Define expanded schema for each food/herb entry:
      `{properties, active_compounds, best_for, contraindications, dosing,
        bioavailability_notes, drug_interactions, evidence_tier, preparation,
        condition_synonyms}`
- [ ] 1.2 Add 20 medicinal herbs: wormwood, black walnut hull, clove, oregano oil,
      berberine, cat's claw, pau d'arco, olive leaf, neem, andrographis,
      artemisia, mimosa pudica, thyme, goldenseal, garlic (therapeutic dose),
      grapefruit seed extract, caprylic acid, uva ursi, barberry, sweet wormwood
- [ ] 1.3 Add 15 detox/liver foods: milk thistle, dandelion root, artichoke leaf,
      burdock root, NAC (food sources), beets, cruciferous vegetables, chlorella,
      spirulina, cilantro, Atlantic dulse, wild blueberries, lemon, apple cider
      vinegar, activated charcoal (context/timing)
- [ ] 1.4 Add 15 gut/microbiome foods: kefir, kimchi, sauerkraut, miso, tempeh,
      prebiotic fiber (chicory, Jerusalem artichoke, green banana), bone broth,
      L-glutamine sources, zinc carnosine foods, slippery elm, marshmallow root,
      aloe vera, colostrum, resistant starch, polyphenol-rich foods
- [ ] 1.5 Add 10 vitality/hormone foods: maca, ashwagandha (full monograph),
      rhodiola, lion's mane, reishi, cordyceps, shilajit, pine pollen,
      tribulus, moringa
- [ ] 1.6 Replace exact-match lookup with fuzzy/synonym matching using
      `condition_synonyms` field (e.g., "IBS" → "gut-health", "arthritis" → "joint-pain")
- [ ] 1.7 Write unit tests: condition lookup, synonym resolution, contraindication
      retrieval, drug interaction flags

**Test criteria:** `get_healing_foods("parasites")` returns ≥5 results with dosing.
`get_healing_foods("IBS")` resolves via synonym to gut-health entries.
All 60+ entries have non-empty `contraindications` and `evidence_tier`.

---

## Stage 2 — Add Missing Detox Protocols
**File:** `app/services/detox.py`
**Scope:** Add 4 missing protocols; deepen existing 3.

### Tasks
- [ ] 2.1 Add **Parasite Cleanse Protocol** (21-day):
      Phase 1 (days 1-7): Starve — eliminate sugar, refined carbs, alcohol, pork.
        Foods: pumpkin seeds, papaya seeds, raw garlic, coconut oil, pomegranate.
      Phase 2 (days 8-18): Kill — wormwood, black walnut hull, clove (the "trinity"),
        mimosa pudica seed, oregano oil, berberine, diatomaceous earth (food grade).
        Herxheimer management: binders (activated charcoal, bentonite clay), hydration.
      Phase 3 (days 19-21): Restore — probiotics, L-glutamine, zinc, bone broth.
      Include: dosing schedules, Herxheimer symptom guide, contraindications,
      moon-phase timing note (parasites are more active around full moon).
- [ ] 2.2 Add **Candida/SIBO Protocol** (30-day):
      Phase 1: Strict candida diet (no sugar, no yeast, no fermented foods initially).
      Phase 2: Antifungals — caprylic acid, oregano oil, berberine, pau d'arco,
        biofilm disruptors (NAC, serrapeptase, EDTA).
      Phase 3: Reintroduce fermented foods, rebuild microbiome diversity.
- [ ] 2.3 Add **Gut 5R Reset Protocol** (60-day):
      Remove (pathogens, irritants), Replace (enzymes, HCl), Reinoculate (probiotics),
      Repair (L-glutamine, zinc carnosine, collagen), Rebalance (lifestyle).
- [ ] 2.4 Add **Mold/Mycotoxin Detox Protocol** (90-day):
      Binders: cholestyramine (Rx), activated charcoal, bentonite clay, zeolite.
      Supports: glutathione, NAC, liposomal vitamin C, VIP nasal spray.
      Diet: low-amylose, mold-free foods.
- [ ] 2.5 Add dosing schedules and Herxheimer management to existing 3 protocols
- [ ] 2.6 Deepen `recommend_protocol()` to use full user profile:
      conditions, contraindications, current medications, severity score
- [ ] 2.7 Write unit tests: protocol retrieval, day guidance, recommendation logic,
      contraindication enforcement

**Test criteria:** `get_protocol("parasite-21day")` returns all 3 phases with dosing.
`recommend_protocol({"conditions": ["candida"]})` returns candida protocol.
Contraindication check blocks pregnancy from intensive protocols.

---

## Stage 3 — Build `NutritionExpertise` Module
**File:** `app/nexus_core/nutrition_expertise.py` (new file)
**Scope:** Mirror `expertise.py` (AstrologyExpertise) for nutrition/wellness domain.

### Tasks
- [ ] 3.1 Create `HealingFoodExpertise` class:
      - `get_food_monograph(name)` — full herb/food profile
      - `get_foods_for_condition(condition)` — ranked by evidence tier
      - `get_contraindications(food, user_profile)` — personalized safety check
      - `get_drug_interactions(food, medications)` — flag known interactions
      - `get_bioavailability_stack(food)` — cofactors that enhance absorption
        (e.g., curcumin + piperine + fat; vitamin D + K2 + magnesium)
- [ ] 3.2 Create `ConditionProtocolMapper` class:
      - Maps 50+ conditions to recommended foods, herbs, protocols, and labs
      - Conditions: inflammation, leaky gut, SIBO, candida, parasites, heavy metals,
        liver congestion, adrenal fatigue, thyroid dysfunction, hormonal imbalance,
        blood sugar dysregulation, cardiovascular risk, cognitive decline, insomnia,
        anxiety, depression, autoimmune, skin conditions, weight resistance
      - Each condition entry: `{foods, herbs, avoid, protocols, labs, lifestyle, timeline}`
- [ ] 3.3 Create `FunctionalMedicineReasoner` class:
      - `assess_root_cause(symptoms)` — maps symptom clusters to likely root causes
      - `build_protocol(root_cause, user_profile)` — generates personalized protocol
      - `check_interactions(protocol, medications, conditions)` — safety validation
      - `prioritize_interventions(protocol)` — ranks by impact and ease
- [ ] 3.4 Create `NutrientDeficiencyMapper`:
      - Maps symptoms to likely deficiencies (fatigue → B12/iron/D3/thyroid)
      - Maps deficiencies to food sources and therapeutic doses
      - Includes cofactor chains (magnesium needed for 300+ enzymatic reactions)
- [ ] 3.5 Write unit tests for all 4 classes

**Test criteria:** `get_foods_for_condition("parasites")` returns ranked list with
evidence tiers. `assess_root_cause(["bloating", "fatigue", "brain fog"])` returns
["SIBO", "candida", "leaky gut"] as top candidates. `get_bioavailability_stack("curcumin")`
returns ["piperine", "fat", "heat"].

---

## Stage 4 — Seed the ChromaDB Knowledge Base
**File:** `app/services/knowledge_seeder.py` (new file)
**Scope:** Populate ChromaDB with ~500 curated facts at startup using a shared
`__nexus_domain__` user ID so all users benefit from the same knowledge base.

### Tasks
- [ ] 4.1 Create `KnowledgeSeeder` class with `seed_all()` method
- [ ] 4.2 Curate and embed **PubMed-grounded nutrition facts** (150 entries):
      Format: `"[EVIDENCE: RCT/meta-analysis/observational] [FINDING]. Source: [PMID/journal]"`
      Topics: curcumin anti-inflammatory mechanisms, berberine vs metformin,
      omega-3 EPA/DHA dosing, magnesium glycinate for sleep, zinc for immunity,
      vitamin D3 + K2 synergy, NAC for liver/glutathione, probiotics for IBS,
      resistant starch for microbiome, polyphenols for gut diversity
- [ ] 4.3 Curate and embed **herb monographs** (100 entries):
      Format: `"[HERB: name] [CONDITION: target] [MECHANISM: how it works] [DOSE: therapeutic range] [CAUTION: contraindications]"`
      Herbs: all 20 from Stage 1.2 + 10 adaptogens + 10 nervines
- [ ] 4.4 Curate and embed **functional medicine protocols** (100 entries):
      Format: `"[PROTOCOL: name] [PHASE: n] [ACTION: what to do] [RATIONALE: why]"`
      Protocols: all from Stage 2 + 5R gut reset + methylation support + adrenal recovery
- [ ] 4.5 Curate and embed **food-condition mappings** (100 entries):
      Format: `"[CONDITION: name] [FOOD: name] [BENEFIT: specific effect] [DOSE: amount/frequency] [TIMING: when to consume]"`
- [ ] 4.6 Curate and embed **contraindications and interactions** (50 entries):
      Format: `"[CAUTION] [HERB/FOOD] interacts with [DRUG/CONDITION]: [MECHANISM] [SEVERITY: mild/moderate/severe]"`
- [ ] 4.7 Add `seed_on_startup()` call in `app/main.py` — idempotent (checks if
      already seeded via a sentinel key before re-embedding)
- [ ] 4.8 Write tests: seeder runs without error, sentinel prevents double-seeding,
      semantic search returns relevant results for test queries

**Test criteria:** After seeding, `vector_memory.search_knowledge("__nexus_domain__", "wormwood parasite")` returns ≥3 results with similarity > 0.6. `search_knowledge("__nexus_domain__", "curcumin bioavailability")` returns piperine/fat cofactor entry.

---

## Stage 5 — Expand RAG Knowledge Extraction
**File:** `app/services/rag.py`
**Scope:** Expand `_AI_FACT_PATTERNS` and `_USER_FACT_PATTERNS` so every conversation
auto-seeds the user's personal knowledge base with nutrition/wellness facts.

### Tasks
- [ ] 5.1 Expand `_AI_FACT_PATTERNS` to capture:
      - Antiparasitic herbs: wormwood, black walnut, clove, mimosa pudica, berberine,
        oregano oil, artemisia, neem, pau d'arco, grapefruit seed extract
      - Detox agents: chlorella, spirulina, cilantro, activated charcoal, bentonite clay,
        NAC, glutathione, milk thistle, dandelion, burdock
      - Gut/microbiome: SIBO, candida, leaky gut, dysbiosis, biofilm, Herxheimer,
        L-glutamine, zinc carnosine, slippery elm, colostrum
      - Adaptogens: ashwagandha, rhodiola, lion's mane, reishi, cordyceps, maca
      - Nutrients: magnesium glycinate, vitamin D3, K2, B12, methylfolate, zinc,
        selenium, iodine, iron, ferritin, CoQ10, alpha-lipoic acid
      - Functional medicine: methylation, Phase I/II liver detox, HPA axis,
        adrenal fatigue, thyroid T3/T4/TSH, insulin resistance, leaky gut
- [ ] 5.2 Expand `_USER_FACT_PATTERNS` to capture:
      - Supplement statements: "I take [supplement]", "I've been on [herb]"
      - Condition statements: "I have [condition]", "I've been diagnosed with"
      - Dietary patterns: "I follow [diet]", "I avoid [food]", "I'm sensitive to"
      - Symptom reports: "I experience [symptom]", "I struggle with"
- [ ] 5.3 Add `_extract_protocol_facts()` — when AI response contains a protocol
      recommendation, extract and store the key steps as individual knowledge items
- [ ] 5.4 Update `retrieve_context()` to also query the `__nexus_domain__` shared
      collection and merge results with user-specific results (domain knowledge
      retrieved for everyone, personal facts retrieved per-user)
- [ ] 5.5 Write tests: pattern extraction for all new herb/nutrient terms,
      shared collection retrieval, merged context building

**Test criteria:** `_extract_facts("I take berberine for blood sugar", "Berberine activates AMPK pathway similar to metformin", "nutrition")` returns ≥2 facts. Shared domain knowledge retrieved alongside personal facts in `retrieve_context()`.

---

## Stage 6 — Deepen the System Prompt & Module Prompts
**Files:** `app/services/nexus.py`, `app/services/nutrition.py`
**Scope:** Inject functional medicine philosophy and domain expertise into the LLM's
base instructions so every response reflects deep nutritional knowledge.

### Tasks
- [ ] 6.1 Expand `SYSTEM_PROMPT` with functional medicine principles:
      - Food-as-medicine philosophy (Hippocrates → modern functional medicine)
      - Detox physiology: Phase I (cytochrome P450) and Phase II (conjugation)
        liver detox pathways; what supports each phase
      - Gut-brain-immune axis: how gut health drives systemic outcomes
      - Bioindividuality: genetic SNPs (MTHFR, COMT, VDR), blood type, microbiome
        uniqueness mean one-size-fits-all advice is insufficient
      - Herxheimer awareness: die-off reactions are expected and manageable
      - Evidence hierarchy: RCT > meta-analysis > observational > traditional use
      - Safety-first: always flag contraindications, drug interactions, when to
        refer to a practitioner
- [ ] 6.2 Expand `_build_module_prompt()` for nutrition module:
      - Include user's conditions, medications, dietary restrictions
      - Specify output format: food + mechanism + dose + timing + preparation
      - Request evidence tier for each recommendation
- [ ] 6.3 Expand `_build_module_prompt()` for detox module:
      - Include phase of detox, current symptoms, contraindications
      - Request Herxheimer management guidance when relevant
      - Include binder timing relative to chelation agents
- [ ] 6.4 Add `_build_module_prompt()` for new "parasite" and "microbiome" modules
- [ ] 6.5 Write tests: system prompt contains functional medicine keywords,
      module prompts include user profile data, detox prompt includes Herxheimer note

**Test criteria:** `SYSTEM_PROMPT` contains "Phase I", "Phase II", "bioindividuality",
"Herxheimer". Nutrition module prompt for a user with "candida" condition includes
antifungal food guidance.

---

## Stage 7 — Expand Reasoning Engine Triggers
**File:** `app/services/reasoning.py`
**Scope:** Ensure the structured multi-framework reasoning engine activates for
complex nutrition/detox/parasite queries.

### Tasks
- [ ] 7.1 Add to `COMPLEX_TRIGGERS` (or equivalent threshold logic):
      `"parasite cleanse"`, `"candida"`, `"SIBO"`, `"leaky gut"`, `"microbiome"`,
      `"food sensitivity"`, `"detox reaction"`, `"Herxheimer"`, `"heavy metal"`,
      `"mold toxicity"`, `"adrenal fatigue"`, `"thyroid"`, `"methylation"`,
      `"hormone balance"`, `"blood sugar"`, `"insulin resistance"`, `"autoimmune"`,
      `"root cause"`, `"protocol"`, `"supplement stack"`
- [ ] 7.2 Add nutrition-specific reasoning frameworks to the engine:
      - **Root Cause Analysis**: symptom → system → root cause → protocol
      - **Bioindividuality Assessment**: same symptom, different root causes per person
      - **Interaction Safety Check**: always run before recommending a protocol
      - **Phased Protocol Reasoning**: sequence matters (open drainage before killing)
- [ ] 7.3 Add `build_nutrition_reasoning_context(query, user_profile)` that injects:
      - User's known conditions and medications
      - Active detox phase (if any)
      - Known sensitivities and contraindications
      - Current supplement stack
- [ ] 7.4 Wire `build_nutrition_reasoning_context()` into `NexusService.chat()`
      when domain is "nutrition" or "detox"
- [ ] 7.5 Write tests: complex trigger detection for all new terms, reasoning
      context includes user profile data, safety check runs for drug interactions

**Test criteria:** `is_complex_query("I want to do a parasite cleanse")` returns True.
`is_complex_query("what should I eat for breakfast")` returns False.
Reasoning context for a user on warfarin includes herb-drug interaction warning.

---

## Stage 8 — Wire `NutritionExpertise` into the Chat Pipeline
**Files:** `app/services/nexus.py`, `app/services/conversation.py`
**Scope:** Inject `NutritionExpertise` domain context into the system prompt when
domain is detected as nutrition, detox, or parasite-related.

### Tasks
- [ ] 8.1 Instantiate `NutritionExpertise` singleton in `app/nexus_core/nutrition_expertise.py`
- [ ] 8.2 In `NexusService.chat()`, after domain detection:
      - If domain in `["nutrition", "detox", "parasite", "microbiome"]`:
        call `nutrition_expertise.get_domain_context(query, user_profile)`
        and inject into system prompt as a new layer between RAG and learning context
- [ ] 8.3 `get_domain_context()` should return:
      - Relevant condition→food mappings for the user's conditions
      - Active contraindications given user's medications
      - Recommended evidence-based protocol if query implies a protocol need
      - Bioavailability stacks for any foods/herbs mentioned in the query
- [ ] 8.4 Add `"parasite"` and `"microbiome"` to `DOMAIN_KEYWORDS` in `conversation.py`
- [ ] 8.5 Update engine version to `nexus-conversation-v1.5`
- [ ] 8.6 Write integration tests: chat pipeline injects nutrition expertise for
      nutrition queries, does not inject for astrology queries, contraindications
      appear in context for users with relevant medications

**Test criteria:** System prompt for a nutrition query contains condition-specific
food recommendations. System prompt for an astrology query does not contain
nutrition expertise block. User on blood thinners gets herb-drug interaction warning
in context before LLM call.

---

## Stage 9 — End-to-End Validation & Refinement
**Scope:** Validate the full pipeline with representative test cases. Refine
knowledge base entries based on response quality.

### Tasks
- [ ] 9.1 Run 20 representative test queries through the full pipeline (no LLM key
      required — validate system prompt construction and context injection):
      - "I have chronic fatigue, bloating, and brain fog — what's wrong with me?"
      - "Design a parasite cleanse for me. I'm on no medications."
      - "What foods should I eat to support my liver during a detox?"
      - "I think I have candida. What should I avoid and what kills it?"
      - "I have SIBO. What's the 5R protocol?"
      - "What herbs are safe for someone on warfarin?"
      - "How do I know if I have heavy metal toxicity?"
      - "What's the best anti-inflammatory diet for autoimmune disease?"
      - "I'm doing a heavy metal detox — what binders should I use and when?"
      - "What supplements support methylation for someone with MTHFR?"
      - "How do I manage Herxheimer reactions during a parasite cleanse?"
      - "What foods raise glutathione naturally?"
      - "Design a 7-day gut healing protocol for leaky gut."
      - "What's the difference between probiotics and prebiotics?"
      - "I have adrenal fatigue — what adaptogens should I take?"
      - "What foods support thyroid function?"
      - "How do I balance blood sugar naturally?"
      - "What's the best diet for someone with an autoimmune condition?"
      - "I want to do a 30-day vitality reset — where do I start?"
      - "What are the signs of a successful detox?"
- [ ] 9.2 For each query, assert:
      - Correct domain detected
      - RAG context contains relevant entries (if seeded)
      - Reasoning engine activates for complex queries
      - Nutrition expertise block present in system prompt
      - No contraindicated recommendations for users with flagged conditions
- [ ] 9.3 Identify knowledge gaps from failed assertions → add missing entries to
      Stage 1–4 knowledge base and re-run
- [ ] 9.4 Tune `_MIN_SIMILARITY` threshold in `rag.py` based on retrieval quality
- [ ] 9.5 Tune `COMPLEX_TRIGGERS` based on false positive/negative rates
- [ ] 9.6 Document final knowledge base coverage: foods, herbs, conditions, protocols

**Test criteria:** All 20 queries produce correct domain detection. ≥15/20 queries
have relevant RAG context retrieved. All complex queries activate reasoning engine.
Zero contraindicated recommendations for test user profiles with known medications.

---

## Stage 10 — Commit, Document, and Create PR
**Scope:** Clean up, document, and ship.

### Tasks
- [ ] 10.1 Ensure all tests pass: `pytest tests/ -v` — 0 failures
- [ ] 10.2 Add `aiosqlite` and any new deps to `requirements.txt`
- [ ] 10.3 Update `SYSTEM_PROMPT` docstring to reflect new capabilities
- [ ] 10.4 Add `GET /nexus/nutrition/foods/{condition}` endpoint exposing the
      expanded healing foods database via API
- [ ] 10.5 Add `GET /nexus/nutrition/herb/{name}` endpoint for full herb monographs
- [ ] 10.6 Add `GET /nexus/detox/protocols` endpoint listing all protocols including new ones
- [ ] 10.7 Commit all changes with structured commit message
- [ ] 10.8 Create PR on `feature/nexus-wellness-platform`

---

## Implementation Order & Dependencies

```
Stage 1 (Healing Foods DB)
    ↓
Stage 2 (Detox Protocols)
    ↓
Stage 3 (NutritionExpertise module)  ←── depends on Stage 1 + 2 data
    ↓
Stage 4 (ChromaDB seeding)           ←── depends on Stage 1 + 2 + 3 content
    ↓
Stage 5 (RAG extraction expansion)   ←── depends on Stage 4 (shared collection)
    ↓
Stage 6 (System prompt deepening)    ←── depends on Stage 3 content
    ↓
Stage 7 (Reasoning triggers)         ←── depends on Stage 3 (reasoning frameworks)
    ↓
Stage 8 (Wire into chat pipeline)    ←── depends on Stages 3, 6, 7
    ↓
Stage 9 (End-to-end validation)      ←── depends on all above
    ↓
Stage 10 (Ship)
```

## Files Created / Modified Per Stage

| Stage | New Files | Modified Files |
|-------|-----------|----------------|
| 1 | — | `app/services/nutrition.py`, `tests/test_nutrition.py` |
| 2 | — | `app/services/detox.py`, `tests/test_detox.py` |
| 3 | `app/nexus_core/nutrition_expertise.py` | `tests/test_nutrition_expertise.py` |
| 4 | `app/services/knowledge_seeder.py` | `app/main.py`, `tests/test_knowledge_seeder.py` |
| 5 | — | `app/services/rag.py`, `tests/test_rag.py` |
| 6 | — | `app/services/nexus.py` |
| 7 | — | `app/services/reasoning.py`, `tests/test_reasoning.py` |
| 8 | — | `app/services/nexus.py`, `app/services/conversation.py` |
| 9 | `tests/test_e2e_nutrition.py` | — |
| 10 | — | `app/routers/nexus.py`, `requirements.txt` |
