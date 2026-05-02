"""
Knowledge seeder — populates ChromaDB with curated nutrition/wellness facts
at startup under the shared DOMAIN_USER_ID so all users benefit.

Idempotent: checks a sentinel key before re-embedding. Safe to call on every
server start.

Knowledge is organised into 5 categories stored in the knowledge collection:
  - pubmed_facts      : RCT / meta-analysis findings
  - herb_monographs   : mechanism, dose, caution per herb
  - protocol_steps    : phase-by-phase protocol guidance
  - food_condition    : food → condition → benefit → dose → timing
  - contraindications : herb/food + drug/condition interaction warnings
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.vector_memory import VectorMemoryService

logger = logging.getLogger(__name__)

# Shared user ID — knowledge stored here is retrieved for every user
# Must be a valid ChromaDB collection name (alphanumeric + hyphens, no leading underscores)
DOMAIN_USER_ID = "nexus-domain-knowledge"

# Sentinel fact — if present, seeding already ran
_SENTINEL = "NEXUS_DOMAIN_KNOWLEDGE_SEEDED_v1"


# ---------------------------------------------------------------------------
# Knowledge corpus
# ---------------------------------------------------------------------------

PUBMED_FACTS: list[str] = [
    "[EVIDENCE: meta-analysis] Curcumin (turmeric) reduces CRP and IL-6 markers of inflammation comparably to NSAIDs at 500–2000 mg/day. Bioavailability requires piperine (black pepper) or phosphatidylcholine complex. PMID: 26007179",
    "[EVIDENCE: RCT] Berberine 500 mg 3x/day reduces HbA1c by 0.9% and fasting glucose by 20%, comparable to metformin, via AMPK activation. PMID: 18397984",
    "[EVIDENCE: meta-analysis] Omega-3 EPA+DHA at 2–4 g/day reduces triglycerides by 25–30% and systemic inflammation (hs-CRP). DHA is primary structural brain fat; EPA is primary anti-inflammatory. PMID: 17493949",
    "[EVIDENCE: RCT] Magnesium glycinate 300–400 mg/day improves sleep quality, reduces anxiety, and lowers cortisol. 60–80% of Western populations are deficient. PMID: 23853635",
    "[EVIDENCE: RCT] Vitamin D3 5000 IU/day with K2 (MK-7) raises serum 25-OH-D to optimal 60–80 ng/mL. K2 directs calcium to bones, not arteries. PMID: 20194580",
    "[EVIDENCE: RCT] NAC (N-acetyl cysteine) 600 mg 3x/day raises glutathione by 30–35%, supports liver Phase II detox, and disrupts bacterial biofilms. PMID: 15333514",
    "[EVIDENCE: RCT] Ashwagandha KSM-66 300 mg 2x/day reduces cortisol by 27.9%, anxiety by 56.5%, and improves thyroid T3/T4 conversion. PMID: 23439798",
    "[EVIDENCE: RCT] Lion's mane mushroom 1000 mg/day stimulates NGF (nerve growth factor), improving mild cognitive impairment scores after 16 weeks. PMID: 18844328",
    "[EVIDENCE: RCT] Probiotics (Lactobacillus + Bifidobacterium, 50B CFU) reduce IBS symptoms by 42% and improve gut barrier function. PMID: 19220890",
    "[EVIDENCE: meta-analysis] Intermittent fasting (16:8) reduces fasting insulin by 20–31%, body weight by 0.8–13%, and inflammatory markers. PMID: 27810402",
    "[EVIDENCE: RCT] Rhodiola rosea 200–400 mg/day reduces mental fatigue, burnout symptoms, and cortisol awakening response. PMID: 19016404",
    "[EVIDENCE: observational] Wild blueberries (2 cups/day) improve cognitive function, reduce oxidative stress, and lower blood pressure via anthocyanins. PMID: 20047325",
    "[EVIDENCE: RCT] L-glutamine 5 g 3x/day on empty stomach reduces intestinal permeability (leaky gut) and improves IBS symptoms within 8 weeks. PMID: 29276734",
    "[EVIDENCE: RCT] Zinc carnosine 75 mg/day repairs gastric mucosa, reduces H. pylori colonization, and improves gut barrier integrity. PMID: 16635908",
    "[EVIDENCE: meta-analysis] Silymarin (milk thistle) 420 mg/day reduces liver enzymes (ALT, AST) and supports hepatocyte regeneration in NAFLD. PMID: 15486262",
    "[EVIDENCE: RCT] Resistant starch 15–30 g/day increases butyrate-producing bacteria, improves insulin sensitivity, and reduces colorectal cancer risk. PMID: 22797568",
    "[EVIDENCE: RCT] Fermented foods (kimchi, kefir, sauerkraut) consumed daily for 10 weeks increase microbiome diversity and reduce inflammatory markers. PMID: 34256014",
    "[EVIDENCE: observational] Mediterranean diet adherence reduces all-cause mortality by 9%, cardiovascular events by 10%, and cognitive decline by 13%. PMID: 18541598",
    "[EVIDENCE: RCT] Bone broth (collagen peptides 10 g/day) reduces joint pain by 20%, improves skin elasticity, and supports gut lining repair. PMID: 18416885",
    "[EVIDENCE: RCT] Artemisinin (wormwood derivative) demonstrates antiparasitic efficacy against Plasmodium, Giardia, and intestinal helminths. PMID: 15109480",
]

HERB_MONOGRAPHS: list[str] = [
    "[HERB: wormwood] [CONDITION: parasites] [MECHANISM: artemisinin disrupts parasite mitochondrial function and generates reactive oxygen species] [DOSE: 200–400 mg 3x/day, max 4 weeks] [CAUTION: pregnancy, epilepsy, kidney disease, thujone toxicity with alcohol]",
    "[HERB: black walnut hull] [CONDITION: parasites] [MECHANISM: juglone (naphthoquinone) disrupts parasite electron transport chain; tannins create hostile gut environment] [DOSE: tincture 2 mL 3x/day or 500 mg capsule 2x/day] [CAUTION: pregnancy, nut allergy, kidney disease]",
    "[HERB: clove] [CONDITION: parasites] [MECHANISM: eugenol kills parasite eggs — critical third component of antiparasitic trinity; also antifungal and analgesic] [DOSE: 500 mg ground clove 3x/day] [CAUTION: pregnancy high doses, bleeding disorders]",
    "[HERB: oregano oil] [CONDITION: candida, SIBO, parasites] [MECHANISM: carvacrol and thymol disrupt fungal/bacterial cell membranes and inhibit biofilm formation] [DOSE: 200 mg emulsified (70%+ carvacrol) 3x/day] [CAUTION: pregnancy, iron deficiency, Lamiaceae allergy]",
    "[HERB: berberine] [CONDITION: candida, SIBO, blood sugar, parasites] [MECHANISM: activates AMPK pathway (same as metformin); disrupts fungal ergosterol synthesis; antimicrobial against gram-positive and gram-negative bacteria] [DOSE: 500 mg 3x/day with meals] [CAUTION: pregnancy, neonates, hypoglycemia]",
    "[HERB: mimosa pudica seed] [CONDITION: parasites] [MECHANISM: gel-forming mucilage physically traps parasites and biofilm; acts as gut scrubber] [DOSE: 1 g on empty stomach 2x/day] [CAUTION: pregnancy, slows medication absorption]",
    "[HERB: milk thistle] [CONDITION: liver support, detox] [MECHANISM: silymarin stabilizes hepatocyte membranes, inhibits toxin uptake, stimulates protein synthesis for liver regeneration, antioxidant] [DOSE: 420 mg silymarin/day (70–80% standardized)] [CAUTION: Asteraceae allergy, hormone-sensitive cancers]",
    "[HERB: dandelion root] [CONDITION: liver support, digestion] [MECHANISM: taraxacin stimulates bile production; inulin feeds beneficial gut bacteria; diuretic effect supports kidney elimination] [DOSE: 2–8 g dried root/day or 4–8 mL tincture 3x/day] [CAUTION: gallstones, bile duct obstruction, diuretic medications]",
    "[HERB: ashwagandha] [CONDITION: stress, adrenal fatigue, thyroid] [MECHANISM: withanolides modulate HPA axis, reduce cortisol, support T4→T3 thyroid conversion, increase DHEA] [DOSE: 300–600 mg KSM-66 2x/day] [CAUTION: pregnancy, Hashimoto's thyroiditis, hyperthyroidism, nightshade sensitivity]",
    "[HERB: rhodiola] [CONDITION: fatigue, cognitive function, depression] [MECHANISM: rosavins and salidroside modulate serotonin, dopamine, and norepinephrine; reduce cortisol awakening response] [DOSE: 200–600 mg (3% rosavins, 1% salidroside) in morning] [CAUTION: bipolar disorder, pregnancy, MAOIs, SSRIs]",
    "[HERB: lion's mane] [CONDITION: cognitive function, nerve repair, gut health] [MECHANISM: hericenones and erinacines stimulate NGF (nerve growth factor) synthesis; beta-glucans modulate immune function] [DOSE: 1000 mg dual-extract 2x/day] [CAUTION: mushroom allergy, autoimmune disease]",
    "[HERB: pau d'arco] [CONDITION: candida, parasites, immunity] [MECHANISM: lapachol and beta-lapachone inhibit fungal respiration and DNA synthesis; immunomodulatory polysaccharides] [DOSE: 500 mg 3x/day or 3 cups tea/day] [CAUTION: pregnancy, bleeding disorders, warfarin]",
    "[HERB: NAC] [CONDITION: liver support, detox, SIBO, biofilm] [MECHANISM: precursor to glutathione (master antioxidant); disrupts bacterial biofilm matrix; supports Phase II liver detox via cysteine] [DOSE: 600 mg 3x/day; take with vitamin C] [CAUTION: asthma (may trigger bronchospasm), bleeding disorders]",
    "[HERB: chlorella] [CONDITION: heavy metals, detox, immunity] [MECHANISM: broken cell wall binds mercury, lead, cadmium in gut via chlorophyll and CGF; prevents reabsorption] [DOSE: 3–10 g/day broken cell wall form] [CAUTION: iodine sensitivity, autoimmune thyroid, warfarin]",
    "[HERB: berberine] [CONDITION: insulin resistance] [MECHANISM: activates AMPK, increases insulin receptor expression, reduces hepatic glucose production, improves insulin sensitivity] [DOSE: 500 mg 3x/day with meals; dihydroberberine 5x more bioavailable] [CAUTION: pregnancy, hypoglycemia, metformin interaction]",
]

PROTOCOL_STEPS: list[str] = [
    "[PROTOCOL: parasite-21day] [PHASE: 1 Starve] [ACTION: eliminate sugar, refined carbs, alcohol, pork; eat pumpkin seeds 1 cup/day on empty stomach, raw garlic 3-4 cloves/day, coconut oil 2-3 tbsp/day] [RATIONALE: remove parasite food sources; pumpkin seeds contain cucurbitacin which paralyzes parasites]",
    "[PROTOCOL: parasite-21day] [PHASE: 2 Kill] [ACTION: wormwood 400mg + black walnut hull tincture 2mL + clove 500mg all 3x/day; add mimosa pudica seed 1g 2x/day on empty stomach; use activated charcoal 1g between meals as binder] [RATIONALE: herbal trinity kills adult parasites, eggs, and larvae; binders prevent toxin reabsorption]",
    "[PROTOCOL: parasite-21day] [PHASE: 3 Restore] [ACTION: high-potency probiotics 50B CFU, L-glutamine 5g 3x/day, zinc carnosine 75mg/day, slippery elm 400mg 3x/day] [RATIONALE: rebuild gut microbiome and repair intestinal lining damaged by parasites]",
    "[PROTOCOL: parasite-21day] [HERXHEIMER MANAGEMENT] [ACTION: if die-off symptoms severe (fatigue, headache, skin breakouts), pause herbs 24-48 hours, increase binders, epsom salt bath, rest, 3L water/day] [RATIONALE: Herxheimer reaction = toxins from dying parasites; binders adsorb and eliminate]",
    "[PROTOCOL: parasite-21day] [MOON PHASE TIMING] [ACTION: intensify protocol (double dose) 3 days before and after full moon] [RATIONALE: parasites are more active and reproduce around full moon; intensifying during this window maximizes kill efficacy]",
    "[PROTOCOL: candida-sibo-30day] [PHASE: 1 Elimination] [ACTION: strict candida diet — no sugar, no grains, no alcohol, no dairy, no fermented foods initially; add NAC 600mg 3x/day and serrapeptase 120,000 IU on empty stomach for biofilm disruption] [RATIONALE: starve candida/SIBO; disrupt protective biofilm before antifungals]",
    "[PROTOCOL: candida-sibo-30day] [PHASE: 2 Antifungal] [ACTION: oregano oil 200mg 3x/day + caprylic acid 1000mg 3x/day + berberine 500mg 3x/day + pau d'arco tea 3 cups/day + Saccharomyces boulardii 5B CFU 2x/day] [RATIONALE: multi-pronged antifungal attack prevents resistance; S. boulardii is antifungal probiotic]",
    "[PROTOCOL: gut-5r-60day] [PHASE: Remove] [ACTION: elimination diet removing gluten, dairy, eggs, soy, corn, peanuts, sugar, alcohol; antimicrobial herbs if infection present] [RATIONALE: remove all gut irritants and pathogens before attempting to heal]",
    "[PROTOCOL: gut-5r-60day] [PHASE: Replace] [ACTION: HCl with pepsin if low stomach acid; full-spectrum digestive enzymes with every meal; ox bile if fat malabsorption] [RATIONALE: restore digestive capacity — most gut issues involve insufficient stomach acid and enzymes]",
    "[PROTOCOL: gut-5r-60day] [PHASE: Repair] [ACTION: L-glutamine 5g 3x/day on empty stomach + zinc carnosine 75mg/day + collagen peptides 10-20g/day + slippery elm 400mg 3x/day + vitamin D3 5000 IU/day] [RATIONALE: L-glutamine is primary fuel for enterocytes; zinc carnosine repairs gastric mucosa]",
    "[PROTOCOL: heavy-metal-30day] [PHASE: 1 Binding Preparation] [ACTION: open drainage pathways first — ensure daily bowel movements, adequate hydration (3L/day), sauna 3x/week; add high-fiber foods and chlorella 3g/day] [RATIONALE: CRITICAL — never mobilize metals without open drainage; redistribution causes severe symptoms]",
    "[PROTOCOL: heavy-metal-30day] [PHASE: 2 Active Chelation] [ACTION: cilantro smoothies daily + chlorella 5-10g/day + wild blueberries + Atlantic dulse; sauna daily; castor oil packs] [RATIONALE: cilantro mobilizes metals from tissues; chlorella binds them in gut; must use together]",
    "[PROTOCOL: mold-mycotoxin-90day] [CRITICAL FIRST STEP] [ACTION: test home with ERMI or HERTSMI-2 before starting protocol; remove from mold exposure completely] [RATIONALE: no protocol works with ongoing mold exposure; this is non-negotiable]",
    "[PROTOCOL: liver-21day] [PHASE: 1 Elimination] [ACTION: remove all liver stressors — alcohol, caffeine, sugar, processed foods, seed oils; add cruciferous vegetables, beets, artichokes, lemon water, turmeric] [RATIONALE: Phase I liver detox (cytochrome P450) requires cofactors from cruciferous vegetables]",
    "[PROTOCOL: liver-21day] [PHASE: 2 Regeneration] [ACTION: eggs, wild salmon, organic liver, beets, leafy greens; add NAC 600mg 3x/day, milk thistle 420mg/day, alpha-lipoic acid 300mg 2x/day] [RATIONALE: Phase II liver detox (conjugation) requires sulfur amino acids from eggs and meat]",
]

FOOD_CONDITION_FACTS: list[str] = [
    "[CONDITION: parasites] [FOOD: pumpkin seeds] [BENEFIT: cucurbitacin paralyzes parasites without killing host cells] [DOSE: 1 cup raw on empty stomach] [TIMING: morning before breakfast for 7 days]",
    "[CONDITION: parasites] [FOOD: papaya seeds] [BENEFIT: benzyl isothiocyanate and papain enzyme destroy parasite eggs and larvae] [DOSE: 1 tablespoon fresh seeds] [TIMING: morning on empty stomach]",
    "[CONDITION: parasites] [FOOD: raw garlic] [BENEFIT: allicin is potent antiparasitic, antifungal, and antibacterial] [DOSE: 3-4 raw cloves/day] [TIMING: crushed and left 10 minutes before eating to activate allicin]",
    "[CONDITION: candida] [FOOD: coconut oil] [BENEFIT: caprylic acid (C8) disrupts candida cell membrane; lauric acid is antifungal] [DOSE: 2-3 tablespoons/day] [TIMING: with meals or in cooking]",
    "[CONDITION: leaky gut] [FOOD: bone broth] [BENEFIT: glycine and glutamine directly feed enterocytes; collagen repairs tight junctions] [DOSE: 2-3 cups/day] [TIMING: between meals for maximum gut contact]",
    "[CONDITION: leaky gut] [FOOD: L-glutamine] [BENEFIT: primary fuel for intestinal epithelial cells; reduces intestinal permeability] [DOSE: 5g 3x/day] [TIMING: on empty stomach — 30 minutes before meals]",
    "[CONDITION: liver support] [FOOD: beets] [BENEFIT: betaine supports methylation and Phase II liver detox; betalains are potent antioxidants] [DOSE: 1-2 medium beets or 250mL juice/day] [TIMING: morning for nitric oxide boost]",
    "[CONDITION: heavy metals] [FOOD: cilantro] [BENEFIT: mobilizes heavy metals from tissues and organs] [DOSE: 1/4-1/2 cup fresh daily] [TIMING: always pair with chlorella or activated charcoal as binder]",
    "[CONDITION: heavy metals] [FOOD: chlorella] [BENEFIT: broken cell wall binds mercury, lead, cadmium in gut; prevents reabsorption] [DOSE: 3-10g/day broken cell wall] [TIMING: take with or after cilantro; away from medications]",
    "[CONDITION: inflammation] [FOOD: turmeric] [BENEFIT: curcumin inhibits NF-kB inflammatory pathway; reduces CRP and IL-6] [DOSE: 500-2000mg curcumin/day] [TIMING: with black pepper and fat at any meal]",
    "[CONDITION: cognitive function] [FOOD: wild blueberries] [BENEFIT: anthocyanins cross blood-brain barrier; reduce neuroinflammation; improve memory and processing speed] [DOSE: 1-2 cups/day] [TIMING: raw or frozen; avoid cooking]",
    "[CONDITION: blood sugar] [FOOD: berberine] [BENEFIT: activates AMPK pathway; reduces fasting glucose by 20%; comparable to metformin] [DOSE: 500mg 3x/day] [TIMING: with meals to reduce GI side effects]",
    "[CONDITION: adrenal fatigue] [FOOD: ashwagandha] [BENEFIT: withanolides reduce cortisol by 27.9%; support adrenal function and HPA axis regulation] [DOSE: 300-600mg KSM-66 2x/day] [TIMING: morning and evening; evening dose supports sleep]",
    "[CONDITION: gut health] [FOOD: fermented foods] [BENEFIT: live cultures increase microbiome diversity; produce SCFAs; strengthen gut barrier] [DOSE: 1-3 servings/day] [TIMING: introduce slowly — 1 tbsp/day initially]",
    "[CONDITION: detox] [FOOD: activated charcoal] [BENEFIT: non-selective binder; adsorbs toxins, mycotoxins, and die-off byproducts in gut] [DOSE: 500-1000mg between meals] [TIMING: 2+ hours away from ALL medications and supplements]",
    "[CONDITION: methylation] [FOOD: leafy greens] [BENEFIT: folate (natural form) supports methylation cycle; magnesium is cofactor for 300+ enzymatic reactions] [DOSE: 2-3 cups raw or 1 cup cooked/day] [TIMING: with fat for fat-soluble vitamin absorption]",
    "[CONDITION: thyroid support] [FOOD: Brazil nuts] [BENEFIT: 1-2 Brazil nuts = ~200mcg selenium; selenium is essential for T4→T3 conversion and thyroid peroxidase] [DOSE: 1-2 nuts/day] [TIMING: daily; do not exceed 400mcg selenium total]",
    "[CONDITION: sleep] [FOOD: magnesium glycinate] [BENEFIT: activates GABA receptors; reduces cortisol; supports melatonin synthesis] [DOSE: 300-400mg] [TIMING: 30-60 minutes before bed]",
    "[CONDITION: immunity] [FOOD: elderberry] [BENEFIT: anthocyanins inhibit viral replication; stimulate cytokine production; reduce cold/flu duration by 2-4 days] [DOSE: 15mL syrup 4x/day during illness] [TIMING: at first sign of illness; not for long-term daily use in autoimmune]",
    "[CONDITION: heart health] [FOOD: wild salmon] [BENEFIT: EPA+DHA reduce triglycerides 25-30%; reduce platelet aggregation; anti-inflammatory] [DOSE: 2-3 servings/week or 2-4g EPA+DHA supplement/day] [TIMING: with meals; avoid frying]",
]

CONTRAINDICATION_FACTS: list[str] = [
    "[CAUTION] Wormwood interacts with: anticoagulants (potentiates bleeding risk), seizure medications (thujone lowers seizure threshold), alcohol (thujone toxicity). SEVERITY: moderate-severe. Do not use in pregnancy, epilepsy, or kidney disease.",
    "[CAUTION] Berberine interacts with: metformin (additive blood sugar lowering — monitor closely), cyclosporine (increases drug levels), CYP3A4 substrates (many drugs). SEVERITY: moderate. Avoid in pregnancy and neonates (jaundice risk).",
    "[CAUTION] Turmeric/curcumin interacts with: warfarin (potentiates anticoagulation), antiplatelet drugs (additive), chemotherapy (consult oncologist). SEVERITY: moderate. Avoid therapeutic doses with gallstones or bile duct obstruction.",
    "[CAUTION] Grapefruit seed extract EXTENSIVELY inhibits CYP3A4 enzyme: interacts with statins, calcium channel blockers, immunosuppressants, many psychiatric medications, and dozens of other drugs. SEVERITY: severe. Check all medications before use.",
    "[CAUTION] Ashwagandha interacts with: thyroid medications (may increase T3/T4 — monitor levels), immunosuppressants, sedatives (additive), diabetes medications. SEVERITY: moderate. Contraindicated in Hashimoto's thyroiditis and hyperthyroidism.",
    "[CAUTION] Rhodiola interacts with: MAOIs (serotonin syndrome risk), SSRIs (serotonin syndrome risk), stimulants (additive). SEVERITY: moderate-severe. Contraindicated in bipolar disorder (may trigger mania).",
    "[CAUTION] Pau d'arco interacts with: warfarin (anticoagulant effect), antiplatelet drugs. SEVERITY: moderate. Contraindicated in pregnancy and bleeding disorders.",
    "[CAUTION] Chlorella interacts with: warfarin (vitamin K content — keep intake consistent), immunosuppressants. SEVERITY: mild-moderate. Avoid in iodine sensitivity and autoimmune thyroid disease.",
    "[CAUTION] NAC interacts with: nitroglycerin (severe hypotension), activated charcoal (reduces NAC absorption — separate by 2+ hours). SEVERITY: moderate. May trigger bronchospasm in asthma.",
    "[CAUTION] Activated charcoal adsorbs ALL oral medications and supplements. SEVERITY: severe for medication users. Always separate by 2+ hours from any medication. Do not use with intestinal obstruction or constipation.",
    "[CAUTION] Oregano oil interacts with: blood thinners (antiplatelet effect), lithium (reduces excretion), iron supplements (reduces absorption — separate by 2 hours). SEVERITY: mild-moderate. Contraindicated in pregnancy.",
    "[CAUTION] High-dose vitamin D3 (>10,000 IU/day) can cause hypercalcemia. Always co-supplement with K2 (MK-7 200mcg) to direct calcium to bones. Monitor 25-OH-D levels; optimal 60-80 ng/mL. SEVERITY: moderate at very high doses.",
    "[CAUTION] Licorice root (not DGL) raises blood pressure and causes potassium loss with long-term use. Contraindicated in hypertension, heart disease, kidney disease, and with diuretics. DGL (deglycyrrhizinated) form is safe for gut use. SEVERITY: moderate.",
    "[CAUTION] Elderberry may overstimulate immune system in autoimmune conditions. Avoid long-term daily use in lupus, rheumatoid arthritis, MS, or other autoimmune diseases. Short-term use during acute illness is generally safe. SEVERITY: mild-moderate.",
    "[CAUTION] Mimosa pudica seed slows absorption of all oral medications. Separate by 2+ hours from any medication. Drink extra water (risk of intestinal obstruction if dehydrated). SEVERITY: mild.",
]


class KnowledgeSeeder:
    """Seeds ChromaDB with curated domain knowledge at startup."""

    def __init__(self, vm: "VectorMemoryService | None" = None) -> None:
        self._vm = vm

    def _get_vm(self) -> "VectorMemoryService":
        if self._vm is not None:
            return self._vm
        from app.services.vector_memory import vector_memory
        return vector_memory

    def is_seeded(self) -> bool:
        vm = self._get_vm()
        results = vm.search_knowledge(DOMAIN_USER_ID, _SENTINEL, n_results=1)
        return len(results) > 0 and results[0]["similarity"] > 0.95

    def seed_all(self) -> dict[str, int]:
        """Seed all knowledge categories. Returns counts per category."""
        if self.is_seeded():
            logger.info("Domain knowledge already seeded — skipping")
            return {"skipped": True}

        vm = self._get_vm()
        counts: dict[str, int] = {}

        # Sentinel
        vm.store_knowledge(DOMAIN_USER_ID, _SENTINEL, domain="meta", source="seeder")

        # PubMed facts
        for fact in PUBMED_FACTS:
            vm.store_knowledge(DOMAIN_USER_ID, fact, domain="nutrition", source="pubmed")
        counts["pubmed_facts"] = len(PUBMED_FACTS)

        # Herb monographs
        for mono in HERB_MONOGRAPHS:
            vm.store_knowledge(DOMAIN_USER_ID, mono, domain="herbs", source="monograph")
        counts["herb_monographs"] = len(HERB_MONOGRAPHS)

        # Protocol steps
        for step in PROTOCOL_STEPS:
            vm.store_knowledge(DOMAIN_USER_ID, step, domain="protocols", source="protocol")
        counts["protocol_steps"] = len(PROTOCOL_STEPS)

        # Food-condition facts
        for fact in FOOD_CONDITION_FACTS:
            vm.store_knowledge(DOMAIN_USER_ID, fact, domain="food-medicine", source="food_condition")
        counts["food_condition_facts"] = len(FOOD_CONDITION_FACTS)

        # Contraindications
        for fact in CONTRAINDICATION_FACTS:
            vm.store_knowledge(DOMAIN_USER_ID, fact, domain="safety", source="contraindication")
        counts["contraindication_facts"] = len(CONTRAINDICATION_FACTS)

        total = sum(counts.values())
        logger.info("Domain knowledge seeded: %d facts across %d categories", total, len(counts))
        return counts


# Singleton
knowledge_seeder = KnowledgeSeeder()
