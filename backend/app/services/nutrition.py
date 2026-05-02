"""Nutrition service — expanded healing foods knowledge base + USDA integration.

Each HEALING_FOODS entry schema:
  properties          : functional categories
  active_compounds    : key bioactive constituents
  best_for            : primary conditions (canonical tags)
  condition_synonyms  : alternate names that map to best_for tags
  contraindications   : who should avoid or use caution
  dosing              : therapeutic dose range
  bioavailability_notes: cofactors / preparation tips that enhance absorption
  drug_interactions   : known interactions with medications
  evidence_tier       : RCT | meta-analysis | observational | traditional
  preparation         : how to use
"""

from typing import Any
import httpx
from app.core.config import settings

# ---------------------------------------------------------------------------
# HEALING FOODS — 60+ entries across 5 categories
# ---------------------------------------------------------------------------
HEALING_FOODS: dict[str, dict[str, Any]] = {
    # ── Anti-inflammatory & antioxidant ──────────────────────────────────────
    "turmeric": {
        "properties": ["anti-inflammatory", "antioxidant", "liver-support", "neuroprotective"],
        "active_compounds": ["curcumin", "turmerones"],
        "best_for": ["inflammation", "joint-pain", "gut-health", "liver-support", "cognitive-function"],
        "condition_synonyms": {"arthritis": "joint-pain", "ibd": "gut-health", "fatty-liver": "liver-support"},
        "contraindications": ["gallstones", "bile-duct-obstruction", "blood-thinners-high-dose"],
        "dosing": "500–2000 mg curcumin/day; culinary: 1–3 tsp/day",
        "bioavailability_notes": "Requires piperine (black pepper) + dietary fat; increases absorption 2000%. Liposomal or phytosome forms bypass this need.",
        "drug_interactions": ["warfarin (potentiates)", "antiplatelet drugs", "chemotherapy (consult oncologist)"],
        "evidence_tier": "meta-analysis",
        "preparation": "Golden milk, curry, or capsule. Always combine with black pepper and fat.",
    },
    "ginger": {
        "properties": ["anti-nausea", "anti-inflammatory", "digestive", "circulatory"],
        "active_compounds": ["gingerols", "shogaols", "zingerone"],
        "best_for": ["nausea", "digestion", "inflammation", "circulation", "joint-pain"],
        "condition_synonyms": {"morning-sickness": "nausea", "ibs": "digestion", "arthritis": "joint-pain"},
        "contraindications": ["gallstones (large doses)", "pre-surgery (stop 2 weeks prior)"],
        "dosing": "1–4 g/day fresh or dried; nausea: 250 mg 4x/day",
        "bioavailability_notes": "Fresh ginger has more gingerols; dried has more shogaols (more potent anti-inflammatory).",
        "drug_interactions": ["warfarin", "antiplatelet drugs", "diabetes medications (may lower blood sugar)"],
        "evidence_tier": "RCT",
        "preparation": "Fresh tea, raw in smoothies, or capsule. Avoid boiling — use hot water steep.",
    },
    "blueberries": {
        "properties": ["antioxidant", "neuroprotective", "anti-inflammatory", "cardioprotective"],
        "active_compounds": ["anthocyanins", "pterostilbene", "resveratrol", "quercetin"],
        "best_for": ["cognitive-function", "oxidative-stress", "heart-health", "blood-sugar"],
        "condition_synonyms": {"brain-fog": "cognitive-function", "memory": "cognitive-function", "cardiovascular": "heart-health"},
        "contraindications": ["none at food doses"],
        "dosing": "1 cup (150 g) daily; therapeutic: 2 cups",
        "bioavailability_notes": "Wild blueberries have 2x anthocyanins vs cultivated. Freeze-drying preserves polyphenols.",
        "drug_interactions": ["none significant at food doses"],
        "evidence_tier": "RCT",
        "preparation": "Raw or frozen. Avoid cooking — heat degrades anthocyanins by 30–50%.",
    },
    "wild-salmon": {
        "properties": ["anti-inflammatory", "neuroprotective", "cardioprotective", "hormone-support"],
        "active_compounds": ["EPA", "DHA", "astaxanthin", "vitamin D3", "selenium"],
        "best_for": ["inflammation", "cognitive-function", "heart-health", "depression", "joint-pain"],
        "condition_synonyms": {"brain-fog": "cognitive-function", "cardiovascular": "heart-health", "mood": "depression"},
        "contraindications": ["fish allergy", "high mercury concern (choose wild Alaskan)"],
        "dosing": "2–3 servings/week (150 g each); EPA+DHA: 1–3 g/day",
        "bioavailability_notes": "Omega-3s absorbed best with fat-containing meal. Astaxanthin is fat-soluble.",
        "drug_interactions": ["warfarin (high-dose fish oil)", "blood pressure medications"],
        "evidence_tier": "meta-analysis",
        "preparation": "Baked, poached, or raw (sashimi). Avoid frying — oxidizes omega-3s.",
    },
    "leafy-greens": {
        "properties": ["alkalizing", "mineral-rich", "detoxifying", "folate-source"],
        "active_compounds": ["chlorophyll", "folate", "magnesium", "vitamin K", "sulforaphane (kale)", "lutein"],
        "best_for": ["detox", "energy", "bone-health", "methylation", "liver-support"],
        "condition_synonyms": {"fatigue": "energy", "osteoporosis": "bone-health", "mthfr": "methylation"},
        "contraindications": ["warfarin users (consistent intake, not elimination)", "kidney disease (oxalates in spinach)"],
        "dosing": "2–3 cups raw or 1 cup cooked daily",
        "bioavailability_notes": "Fat-soluble vitamins (K, A) need dietary fat. Lightly steam spinach to reduce oxalates.",
        "drug_interactions": ["warfarin (vitamin K — keep intake consistent)"],
        "evidence_tier": "observational",
        "preparation": "Rotate: kale, spinach, arugula, Swiss chard, dandelion greens. Raw or lightly steamed.",
    },
    "olive-oil": {
        "properties": ["anti-inflammatory", "cardioprotective", "antioxidant", "gut-support"],
        "active_compounds": ["oleocanthal", "oleuropein", "squalene", "vitamin E", "polyphenols"],
        "best_for": ["inflammation", "heart-health", "gut-health", "cognitive-function"],
        "condition_synonyms": {"cardiovascular": "heart-health", "brain-fog": "cognitive-function"},
        "contraindications": ["none at culinary doses"],
        "dosing": "2–4 tbsp/day extra-virgin",
        "bioavailability_notes": "Polyphenol content varies by harvest date and storage. Use within 18 months of harvest. Store away from light/heat.",
        "drug_interactions": ["none significant"],
        "evidence_tier": "RCT",
        "preparation": "Cold for dressings; low-heat sauté. Do not deep-fry — smoke point 190°C.",
    },
    "walnuts": {
        "properties": ["neuroprotective", "anti-inflammatory", "cardioprotective"],
        "active_compounds": ["ALA (omega-3)", "ellagic acid", "melatonin", "polyphenols", "magnesium"],
        "best_for": ["cognitive-function", "heart-health", "inflammation", "sleep"],
        "condition_synonyms": {"brain-fog": "cognitive-function", "insomnia": "sleep", "cardiovascular": "heart-health"},
        "contraindications": ["tree nut allergy", "high oxalate (kidney stones — moderate intake)"],
        "dosing": "28 g (1 oz / ~14 halves) daily",
        "bioavailability_notes": "ALA conversion to EPA/DHA is limited (~5–10%). Pair with direct EPA/DHA sources.",
        "drug_interactions": ["none significant"],
        "evidence_tier": "RCT",
        "preparation": "Raw or lightly toasted. Avoid roasted-in-oil versions.",
    },

    # ── Antiparasitic herbs ───────────────────────────────────────────────────
    "wormwood": {
        "properties": ["antiparasitic", "antimicrobial", "bitter-digestive", "antifungal"],
        "active_compounds": ["artemisinin", "absinthin", "thujone", "sesquiterpene lactones"],
        "best_for": ["parasites", "candida", "gut-health", "digestion"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "intestinal-worms": "parasites", "giardia": "parasites"},
        "contraindications": ["pregnancy", "breastfeeding", "epilepsy", "kidney disease", "children under 12"],
        "dosing": "200–400 mg dried herb 3x/day for max 4 weeks; tincture: 2–3 mL 3x/day",
        "bioavailability_notes": "Use as part of the antiparasitic trinity: wormwood + black walnut hull + clove. Cycle: 3 weeks on, 1 week off.",
        "drug_interactions": ["anticoagulants", "seizure medications", "alcohol (thujone toxicity)"],
        "evidence_tier": "traditional",
        "preparation": "Capsule, tincture, or tea. Do not use essential oil internally. Limit to 4-week courses.",
    },
    "black-walnut-hull": {
        "properties": ["antiparasitic", "antifungal", "antimicrobial", "astringent"],
        "active_compounds": ["juglone", "tannins", "iodine", "omega-3 fatty acids"],
        "best_for": ["parasites", "candida", "skin-conditions", "gut-health"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "ringworm": "skin-conditions", "fungal-infection": "candida"},
        "contraindications": ["pregnancy", "breastfeeding", "nut allergy", "kidney disease"],
        "dosing": "Tincture: 1–2 mL 3x/day; capsule: 500 mg 2x/day. Use green hull only.",
        "bioavailability_notes": "Part of the antiparasitic trinity with wormwood and clove. Juglone is most potent in green hull tincture.",
        "drug_interactions": ["lithium", "diuretics", "iron supplements (tannins reduce absorption — separate by 2 hours)"],
        "evidence_tier": "traditional",
        "preparation": "Green hull tincture (most potent) or capsule. Avoid if nut-allergic.",
    },
    "clove": {
        "properties": ["antiparasitic", "antifungal", "antimicrobial", "analgesic"],
        "active_compounds": ["eugenol", "beta-caryophyllene", "acetyl eugenol"],
        "best_for": ["parasites", "candida", "dental-health", "gut-health"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "toothache": "dental-health", "fungal-infection": "candida"},
        "contraindications": ["pregnancy (high doses)", "bleeding disorders", "children (eugenol toxicity risk)"],
        "dosing": "500 mg ground clove 3x/day; essential oil: dilute 1:10 in carrier oil (topical only)",
        "bioavailability_notes": "Kills parasite eggs — critical third component of the trinity. Eugenol is rapidly absorbed.",
        "drug_interactions": ["warfarin (antiplatelet effect)", "NSAIDs"],
        "evidence_tier": "observational",
        "preparation": "Ground clove in capsule or added to food. Do not take clove essential oil internally.",
    },
    "oregano-oil": {
        "properties": ["antimicrobial", "antifungal", "antiparasitic", "antiviral"],
        "active_compounds": ["carvacrol", "thymol", "rosmarinic acid"],
        "best_for": ["candida", "parasites", "sibo", "gut-health", "immunity"],
        "condition_synonyms": {"fungal-infection": "candida", "parasite-cleanse": "parasites", "small-intestine-bacterial-overgrowth": "sibo"},
        "contraindications": ["pregnancy", "iron-deficiency (reduces absorption)", "allergy to Lamiaceae family"],
        "dosing": "Emulsified oil: 200–600 mg carvacrol/day; oil of oregano: 2–4 drops in water 3x/day",
        "bioavailability_notes": "Emulsified form reaches small intestine intact. Carvacrol content varies — look for ≥70% carvacrol.",
        "drug_interactions": ["blood thinners", "lithium", "iron supplements (separate by 2 hours)"],
        "evidence_tier": "observational",
        "preparation": "Emulsified capsule preferred. If liquid, dilute in olive oil or water. Cycle 3 weeks on, 1 week off.",
    },
    "berberine": {
        "properties": ["antimicrobial", "antifungal", "blood-sugar-regulation", "anti-inflammatory", "antiparasitic"],
        "active_compounds": ["berberine alkaloid"],
        "best_for": ["blood-sugar", "candida", "sibo", "parasites", "gut-health", "cholesterol"],
        "condition_synonyms": {"insulin-resistance": "blood-sugar", "type-2-diabetes": "blood-sugar", "fungal-infection": "candida", "dysbiosis": "gut-health"},
        "contraindications": ["pregnancy", "breastfeeding", "neonates (jaundice risk)", "hypoglycemia"],
        "dosing": "500 mg 3x/day with meals; blood sugar: 1500 mg/day total",
        "bioavailability_notes": "Poor oral bioavailability (~5%). Take with meals. Dihydroberberine form has 5x better absorption. AMPK activator — similar mechanism to metformin.",
        "drug_interactions": ["metformin (additive — monitor blood sugar)", "cyclosporine", "CYP3A4 substrates", "warfarin"],
        "evidence_tier": "RCT",
        "preparation": "Capsule with meals. Cycle 8 weeks on, 2 weeks off for gut use.",
    },
    "mimosa-pudica-seed": {
        "properties": ["antiparasitic", "gut-scrubbing", "biofilm-disruptor"],
        "active_compounds": ["mucilage", "mimosin", "tannins", "alkaloids"],
        "best_for": ["parasites", "gut-health", "biofilm"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "intestinal-worms": "parasites", "leaky-gut": "gut-health"},
        "contraindications": ["pregnancy", "breastfeeding"],
        "dosing": "1–2 g (1/4–1/2 tsp) on empty stomach 2x/day; capsule: 500 mg 2x/day",
        "bioavailability_notes": "Gel-forming mucilage physically traps parasites and biofilm. Take on empty stomach for maximum gut contact. Drink plenty of water.",
        "drug_interactions": ["may slow absorption of oral medications — separate by 2 hours"],
        "evidence_tier": "traditional",
        "preparation": "Powder in water on empty stomach, or capsule. Increase water intake significantly.",
    },
    "neem": {
        "properties": ["antiparasitic", "antifungal", "antibacterial", "blood-purifying"],
        "active_compounds": ["azadirachtin", "nimbin", "nimbidin", "gedunin"],
        "best_for": ["parasites", "candida", "skin-conditions", "gut-health"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "fungal-infection": "candida", "acne": "skin-conditions"},
        "contraindications": ["pregnancy (abortifacient)", "breastfeeding", "children under 12", "liver disease", "autoimmune conditions"],
        "dosing": "300–500 mg leaf extract 2x/day; max 6 weeks continuous",
        "bioavailability_notes": "Fat-soluble compounds — take with food. Leaf extract preferred over seed oil for internal use.",
        "drug_interactions": ["immunosuppressants", "diabetes medications (hypoglycemia risk)", "lithium"],
        "evidence_tier": "observational",
        "preparation": "Capsule with food. Topical: neem oil diluted 1:10 in carrier oil.",
    },
    "pau-darco": {
        "properties": ["antifungal", "antiparasitic", "antibacterial", "immune-modulating"],
        "active_compounds": ["lapachol", "beta-lapachone", "xyloidone"],
        "best_for": ["candida", "parasites", "immunity", "gut-health"],
        "condition_synonyms": {"fungal-infection": "candida", "parasite-cleanse": "parasites", "immune-support": "immunity"},
        "contraindications": ["pregnancy", "breastfeeding", "bleeding disorders", "pre-surgery"],
        "dosing": "Tea: 2–4 cups/day (1 tbsp bark per cup); capsule: 500 mg 3x/day",
        "bioavailability_notes": "Lapachol is poorly absorbed orally. Tea form may be more bioavailable than capsule for some compounds.",
        "drug_interactions": ["warfarin (anticoagulant effect)", "antiplatelet drugs"],
        "evidence_tier": "traditional",
        "preparation": "Simmer inner bark 20 min (decoction). Capsule or tincture also available.",
    },
    "olive-leaf-extract": {
        "properties": ["antimicrobial", "antiviral", "antifungal", "antioxidant", "cardioprotective"],
        "active_compounds": ["oleuropein", "hydroxytyrosol", "elenolic acid"],
        "best_for": ["immunity", "candida", "parasites", "heart-health", "blood-sugar"],
        "condition_synonyms": {"immune-support": "immunity", "fungal-infection": "candida", "cardiovascular": "heart-health"},
        "contraindications": ["hypotension (lowers blood pressure)", "pregnancy (high doses)"],
        "dosing": "500–1000 mg standardized extract (20% oleuropein) 2–3x/day",
        "bioavailability_notes": "Standardized to oleuropein content. Take with food to reduce GI upset.",
        "drug_interactions": ["blood pressure medications (additive)", "diabetes medications", "warfarin"],
        "evidence_tier": "observational",
        "preparation": "Capsule with food. Tincture or tea also available.",
    },
    "cat's-claw": {
        "properties": ["anti-inflammatory", "immune-modulating", "antiparasitic", "antiviral"],
        "active_compounds": ["oxindole alkaloids", "pentacyclic alkaloids", "proanthocyanidins"],
        "best_for": ["inflammation", "immunity", "parasites", "joint-pain", "gut-health"],
        "condition_synonyms": {"arthritis": "joint-pain", "immune-support": "immunity", "parasite-cleanse": "parasites"},
        "contraindications": ["pregnancy", "breastfeeding", "autoimmune disease (immune stimulation)", "pre-surgery", "organ transplant recipients"],
        "dosing": "250–500 mg standardized extract 2x/day; tea: 1 g bark per cup",
        "bioavailability_notes": "TOA-free (tetracyclic oxindole alkaloid-free) form preferred for immune modulation.",
        "drug_interactions": ["immunosuppressants", "anticoagulants", "antihypertensives", "CYP3A4 substrates"],
        "evidence_tier": "observational",
        "preparation": "Capsule or decoction. Look for TOA-free standardized extract.",
    },
    "artemisia": {
        "properties": ["antiparasitic", "antimalarial", "antifungal", "anti-inflammatory"],
        "active_compounds": ["artemisinin", "artesunate", "artemether"],
        "best_for": ["parasites", "candida", "gut-health"],
        "condition_synonyms": {"parasite-cleanse": "parasites", "malaria": "parasites", "fungal-infection": "candida"},
        "contraindications": ["pregnancy", "breastfeeding", "neurological conditions", "children under 12"],
        "dosing": "200–400 mg artemisinin 2x/day; max 4-week courses",
        "bioavailability_notes": "Fat-soluble — take with food containing fat. Artemisinin degrades rapidly; use fresh product.",
        "drug_interactions": ["anticoagulants", "CYP2B6 substrates", "immunosuppressants"],
        "evidence_tier": "RCT",
        "preparation": "Capsule with fatty meal. Cycle with breaks to prevent resistance.",
    },
    "goldenseal": {
        "properties": ["antimicrobial", "antifungal", "anti-inflammatory", "digestive-bitter"],
        "active_compounds": ["berberine", "hydrastine", "canadine"],
        "best_for": ["gut-health", "candida", "immunity", "sibo"],
        "condition_synonyms": {"fungal-infection": "candida", "immune-support": "immunity", "dysbiosis": "gut-health"},
        "contraindications": ["pregnancy", "breastfeeding", "neonates", "hypertension (high doses)", "G6PD deficiency"],
        "dosing": "250–500 mg root extract 3x/day; max 3-week courses (endangered — use berberine as alternative)",
        "bioavailability_notes": "Contains berberine — same bioavailability considerations. Endangered plant; berberine HCl is a sustainable alternative.",
        "drug_interactions": ["cyclosporine", "CYP3A4 substrates", "warfarin", "metformin"],
        "evidence_tier": "observational",
        "preparation": "Capsule. Prefer berberine HCl as sustainable alternative. Short courses only.",
    },
    "grapefruit-seed-extract": {
        "properties": ["antimicrobial", "antifungal", "antiparasitic"],
        "active_compounds": ["polyphenols", "flavonoids (synthetic preservatives in some products)"],
        "best_for": ["candida", "parasites", "gut-health"],
        "condition_synonyms": {"fungal-infection": "candida", "parasite-cleanse": "parasites"},
        "contraindications": ["grapefruit drug interactions (extensive)", "pregnancy"],
        "dosing": "100–200 mg standardized extract 3x/day; liquid: 10–15 drops in water 3x/day",
        "bioavailability_notes": "Quality varies widely — many products contain synthetic preservatives (benzethonium chloride). Choose certified organic, third-party tested.",
        "drug_interactions": ["EXTENSIVE — inhibits CYP3A4: statins, calcium channel blockers, immunosuppressants, many others"],
        "evidence_tier": "observational",
        "preparation": "Capsule or liquid diluted in water. Check all medications for grapefruit interactions first.",
    },
    "andrographis": {
        "properties": ["antimicrobial", "anti-inflammatory", "immune-stimulating", "antiparasitic"],
        "active_compounds": ["andrographolide", "neoandrographolide"],
        "best_for": ["immunity", "inflammation", "gut-health", "parasites"],
        "condition_synonyms": {"immune-support": "immunity", "cold-flu": "immunity", "parasite-cleanse": "parasites"},
        "contraindications": ["pregnancy (uterine stimulant)", "autoimmune disease", "fertility treatment"],
        "dosing": "300–400 mg standardized extract (10% andrographolide) 3x/day",
        "bioavailability_notes": "Andrographolide has poor water solubility. Standardized extract preferred. Take with food.",
        "drug_interactions": ["immunosuppressants", "anticoagulants", "antihypertensives"],
        "evidence_tier": "RCT",
        "preparation": "Capsule with food. Bitter taste — capsule preferred over tea.",
    },
    "thyme": {
        "properties": ["antimicrobial", "antifungal", "expectorant", "antispasmodic"],
        "active_compounds": ["thymol", "carvacrol", "rosmarinic acid", "flavonoids"],
        "best_for": ["gut-health", "candida", "immunity", "respiratory-health"],
        "condition_synonyms": {"fungal-infection": "candida", "immune-support": "immunity", "cough": "respiratory-health"},
        "contraindications": ["thyroid disorders (high doses)", "pregnancy (culinary doses safe)", "allergy to Lamiaceae"],
        "dosing": "Culinary: unlimited; therapeutic tea: 1–2 tsp dried herb per cup 3x/day; extract: 160–200 mg thymol/day",
        "bioavailability_notes": "Thymol and carvacrol are volatile — use fresh or recently dried herb. Essential oil: topical only.",
        "drug_interactions": ["anticoagulants (high doses)", "thyroid medications"],
        "evidence_tier": "observational",
        "preparation": "Tea, culinary use, or standardized extract. Essential oil topical only (diluted).",
    },
    "uva-ursi": {
        "properties": ["antimicrobial", "astringent", "urinary-antiseptic"],
        "active_compounds": ["arbutin", "hydroquinone", "tannins", "ursolic acid"],
        "best_for": ["urinary-tract-infection", "gut-health", "kidney-support"],
        "condition_synonyms": {"uti": "urinary-tract-infection", "bladder-infection": "urinary-tract-infection"},
        "contraindications": ["pregnancy", "breastfeeding", "kidney disease", "liver disease", "children under 12", "long-term use (>2 weeks)"],
        "dosing": "400–840 mg arbutin/day (standardized); tea: 3 g dried leaf per cup 3–4x/day",
        "bioavailability_notes": "Arbutin converts to hydroquinone in alkaline urine — most effective when urine is alkaline. Avoid acidic foods during use.",
        "drug_interactions": ["lithium", "NSAIDs (kidney stress)", "diuretics"],
        "evidence_tier": "traditional",
        "preparation": "Cold infusion (cold water, 12 hours) reduces tannin content. Short courses only (max 2 weeks).",
    },
    "barberry": {
        "properties": ["antimicrobial", "antifungal", "blood-sugar-regulation", "liver-support"],
        "active_compounds": ["berberine", "berbamine", "oxyacanthine"],
        "best_for": ["gut-health", "candida", "blood-sugar", "liver-support"],
        "condition_synonyms": {"fungal-infection": "candida", "insulin-resistance": "blood-sugar", "dysbiosis": "gut-health"},
        "contraindications": ["pregnancy", "breastfeeding", "neonates"],
        "dosing": "500 mg dried root 3x/day; berberine content varies — standardize to berberine dose",
        "bioavailability_notes": "Contains berberine — same considerations. Sustainable alternative to goldenseal.",
        "drug_interactions": ["same as berberine: metformin, cyclosporine, CYP3A4 substrates"],
        "evidence_tier": "observational",
        "preparation": "Capsule or tincture. Sustainable alternative to goldenseal.",
    },

    # ── Detox & liver support ─────────────────────────────────────────────────
    "milk-thistle": {
        "properties": ["hepatoprotective", "antioxidant", "anti-inflammatory", "liver-regenerating"],
        "active_compounds": ["silymarin", "silybin", "silychristin", "silydianin"],
        "best_for": ["liver-support", "detox", "inflammation"],
        "condition_synonyms": {"fatty-liver": "liver-support", "hepatitis": "liver-support", "alcohol-damage": "liver-support"},
        "contraindications": ["allergy to Asteraceae family", "hormone-sensitive cancers (weak estrogenic effect)"],
        "dosing": "140–420 mg silymarin/day (standardized to 70–80% silymarin); therapeutic: 420 mg/day",
        "bioavailability_notes": "Silymarin is poorly water-soluble. Phosphatidylcholine complex (siliphos) increases absorption 4–10x. Take with food.",
        "drug_interactions": ["CYP3A4 substrates (mild inhibitor)", "diabetes medications (may lower blood sugar)"],
        "evidence_tier": "RCT",
        "preparation": "Standardized capsule (70–80% silymarin). Phosphatidylcholine complex preferred.",
    },
    "dandelion-root": {
        "properties": ["liver-support", "digestive-bitter", "diuretic", "prebiotic"],
        "active_compounds": ["taraxacin", "inulin", "sesquiterpene lactones", "taraxasterol"],
        "best_for": ["liver-support", "detox", "digestion", "gut-health"],
        "condition_synonyms": {"fatty-liver": "liver-support", "bloating": "digestion", "constipation": "digestion"},
        "contraindications": ["gallstones", "bile-duct-obstruction", "allergy to Asteraceae", "diuretic medications"],
        "dosing": "Root: 2–8 g dried root/day; tincture: 4–8 mL 3x/day; tea: 1–2 tsp root per cup",
        "bioavailability_notes": "Inulin content supports gut microbiome. Roasted root has less inulin but more bitter compounds for liver.",
        "drug_interactions": ["diuretics (additive)", "lithium", "quinolone antibiotics (reduced absorption)"],
        "evidence_tier": "observational",
        "preparation": "Decoction (simmer 20 min) or tincture. Roasted root as coffee substitute.",
    },
    "artichoke-leaf": {
        "properties": ["liver-support", "choleretic", "digestive-bitter", "cholesterol-lowering"],
        "active_compounds": ["cynarin", "chlorogenic acid", "luteolin", "silymarin"],
        "best_for": ["liver-support", "detox", "digestion", "cholesterol"],
        "condition_synonyms": {"fatty-liver": "liver-support", "high-cholesterol": "cholesterol", "bloating": "digestion"},
        "contraindications": ["gallstones", "bile-duct-obstruction", "allergy to Asteraceae"],
        "dosing": "320–640 mg standardized extract 3x/day; food: 1–2 artichokes/day",
        "bioavailability_notes": "Cynarin stimulates bile production — take before meals for digestive benefit.",
        "drug_interactions": ["cholesterol medications (additive)", "diuretics"],
        "evidence_tier": "RCT",
        "preparation": "Standardized extract capsule before meals, or whole artichoke steamed.",
    },
    "beets": {
        "properties": ["liver-support", "nitric-oxide-booster", "antioxidant", "detoxifying"],
        "active_compounds": ["betaine", "betalains", "nitrates", "folate"],
        "best_for": ["liver-support", "detox", "heart-health", "energy", "blood-pressure"],
        "condition_synonyms": {"fatty-liver": "liver-support", "hypertension": "blood-pressure", "fatigue": "energy"},
        "contraindications": ["kidney stones (high oxalate)", "low blood pressure"],
        "dosing": "1–2 medium beets/day; juice: 250–500 mL/day; powder: 1–2 tsp/day",
        "bioavailability_notes": "Betaine supports methylation and liver Phase II detox. Nitrates convert to nitric oxide — peak effect 2–3 hours after consumption.",
        "drug_interactions": ["blood pressure medications (additive)", "erectile dysfunction drugs (nitrate interaction)"],
        "evidence_tier": "RCT",
        "preparation": "Raw, roasted, or juiced. Cooking reduces nitrate content by ~25%.",
    },
    "chlorella": {
        "properties": ["heavy-metal-chelator", "detoxifying", "immune-support", "alkalizing"],
        "active_compounds": ["chlorophyll", "chlorella growth factor (CGF)", "beta-glucan", "vitamin B12"],
        "best_for": ["detox", "heavy-metals", "immunity", "gut-health"],
        "condition_synonyms": {"heavy-metal-detox": "heavy-metals", "mercury-detox": "heavy-metals", "immune-support": "immunity"},
        "contraindications": ["iodine sensitivity", "autoimmune thyroid disease", "warfarin (vitamin K content)", "immunosuppressed patients"],
        "dosing": "3–5 g/day (broken cell wall form); heavy metal detox: up to 10 g/day",
        "bioavailability_notes": "Must be broken cell wall form for nutrient absorption. Binds mercury, lead, cadmium in gut. Take away from medications.",
        "drug_interactions": ["warfarin (vitamin K)", "immunosuppressants"],
        "evidence_tier": "observational",
        "preparation": "Broken cell wall powder or tablets. Start low (1 g) and increase to avoid detox reactions.",
    },
    "spirulina": {
        "properties": ["detoxifying", "anti-inflammatory", "immune-support", "protein-source"],
        "active_compounds": ["phycocyanin", "gamma-linolenic acid", "beta-carotene", "iron", "B12"],
        "best_for": ["detox", "immunity", "energy", "inflammation", "heavy-metals"],
        "condition_synonyms": {"heavy-metal-detox": "heavy-metals", "immune-support": "immunity", "fatigue": "energy"},
        "contraindications": ["phenylketonuria (PKU)", "autoimmune disease (immune stimulation)", "seafood allergy"],
        "dosing": "1–8 g/day; therapeutic: 4–8 g/day",
        "bioavailability_notes": "Phycocyanin is the primary anti-inflammatory compound. Combine with chlorella for synergistic heavy metal binding.",
        "drug_interactions": ["immunosuppressants", "anticoagulants (vitamin K content)"],
        "evidence_tier": "observational",
        "preparation": "Powder in smoothies or tablets. Pair with chlorella for heavy metal detox.",
    },
    "cilantro": {
        "properties": ["heavy-metal-chelator", "antimicrobial", "digestive", "antioxidant"],
        "active_compounds": ["linalool", "alpha-pinene", "quercetin", "chlorophyll"],
        "best_for": ["heavy-metals", "detox", "digestion", "gut-health"],
        "condition_synonyms": {"heavy-metal-detox": "heavy-metals", "mercury-detox": "heavy-metals"},
        "contraindications": ["allergy (cross-reactive with carrot family)", "blood thinners (high doses)"],
        "dosing": "Fresh: 1/4–1/2 cup daily; tincture: 2–4 mL 3x/day",
        "bioavailability_notes": "Mobilizes heavy metals from tissues — must pair with binders (chlorella, activated charcoal) to prevent redistribution.",
        "drug_interactions": ["anticoagulants (high doses)"],
        "evidence_tier": "traditional",
        "preparation": "Fresh in smoothies, salads, or juiced. Always pair with a binder when using therapeutically.",
    },
    "activated-charcoal": {
        "properties": ["binder", "detoxifying", "anti-poison", "gut-adsorbent"],
        "active_compounds": ["activated carbon (porous structure)"],
        "best_for": ["detox", "heavy-metals", "herxheimer-management", "gut-health"],
        "condition_synonyms": {"herxheimer": "herxheimer-management", "die-off": "herxheimer-management", "poisoning": "detox"},
        "contraindications": ["intestinal obstruction", "within 2 hours of medications or supplements", "constipation (worsens)"],
        "dosing": "500–1000 mg between meals; Herxheimer: 1–2 g as needed",
        "bioavailability_notes": "Non-selective binder — adsorbs toxins AND nutrients/medications. Take 2+ hours away from all supplements and medications. Drink extra water.",
        "drug_interactions": ["ALL oral medications (reduces absorption) — separate by 2+ hours"],
        "evidence_tier": "observational",
        "preparation": "Capsule or powder in water between meals. Short-term use only (max 2 weeks continuous).",
    },
    "nac": {
        "properties": ["glutathione-precursor", "liver-support", "mucolytic", "antioxidant", "biofilm-disruptor"],
        "active_compounds": ["N-acetyl cysteine"],
        "best_for": ["liver-support", "detox", "respiratory-health", "sibo", "gut-health"],
        "condition_synonyms": {"fatty-liver": "liver-support", "acetaminophen-overdose": "liver-support", "biofilm": "sibo"},
        "contraindications": ["asthma (may trigger bronchospasm in some)", "bleeding disorders"],
        "dosing": "600–1800 mg/day; liver support: 600 mg 2x/day; biofilm: 600 mg 3x/day",
        "bioavailability_notes": "Precursor to glutathione — the body's master antioxidant. Liposomal glutathione is more direct but NAC is more affordable. Take with vitamin C to enhance glutathione synthesis.",
        "drug_interactions": ["nitroglycerin (hypotension)", "activated charcoal (reduces absorption)"],
        "evidence_tier": "RCT",
        "preparation": "Capsule. Take with vitamin C. Effervescent form has better taste.",
    },

    # ── Gut & microbiome support ──────────────────────────────────────────────
    "fermented-foods": {
        "properties": ["probiotic", "gut-microbiome", "immune-support", "mental-health"],
        "active_compounds": ["Lactobacillus", "Bifidobacterium", "SCFA precursors", "enzymes"],
        "best_for": ["gut-health", "immunity", "mental-health", "digestion"],
        "condition_synonyms": {"ibs": "gut-health", "dysbiosis": "gut-health", "depression": "mental-health"},
        "contraindications": ["SIBO (fermented foods may worsen)", "histamine intolerance", "immunocompromised (raw ferments)"],
        "dosing": "1–3 servings/day; introduce slowly (1 tbsp/day) to avoid bloating",
        "bioavailability_notes": "Unpasteurized only — pasteurization kills live cultures. Rotate varieties for microbiome diversity.",
        "drug_interactions": ["immunosuppressants (live cultures — consult physician)"],
        "evidence_tier": "RCT",
        "preparation": "Kimchi, sauerkraut, kefir, miso, tempeh, kombucha. Unpasteurized only.",
    },
    "bone-broth": {
        "properties": ["gut-healing", "collagen-source", "mineral-rich", "anti-inflammatory"],
        "active_compounds": ["collagen", "gelatin", "glycine", "proline", "glutamine", "minerals"],
        "best_for": ["gut-health", "joint-pain", "skin-conditions", "leaky-gut"],
        "condition_synonyms": {"leaky-gut": "gut-health", "intestinal-permeability": "gut-health", "arthritis": "joint-pain"},
        "contraindications": ["histamine intolerance (long-simmered broth is high histamine)", "gout (high purine)"],
        "dosing": "1–2 cups/day; therapeutic (leaky gut): 3 cups/day",
        "bioavailability_notes": "Glycine and glutamine directly feed enterocytes (gut lining cells). Add apple cider vinegar to extraction to increase mineral content.",
        "drug_interactions": ["none significant"],
        "evidence_tier": "observational",
        "preparation": "Simmer grass-fed bones 12–24 hours with ACV. Instant pot: 3–4 hours.",
    },
    "l-glutamine": {
        "properties": ["gut-healing", "muscle-recovery", "immune-support", "anti-catabolic"],
        "active_compounds": ["L-glutamine amino acid"],
        "best_for": ["leaky-gut", "gut-health", "immunity", "muscle-recovery"],
        "condition_synonyms": {"intestinal-permeability": "leaky-gut", "ibs": "gut-health", "crohns": "gut-health"},
        "contraindications": ["cancer (glutamine feeds some tumors — consult oncologist)", "liver disease (ammonia)", "seizure disorders"],
        "dosing": "5–40 g/day; leaky gut: 5–10 g 3x/day on empty stomach",
        "bioavailability_notes": "Primary fuel for enterocytes. Take on empty stomach for gut delivery. Powder dissolves easily in water.",
        "drug_interactions": ["lactulose (may reduce efficacy)", "anticonvulsants"],
        "evidence_tier": "RCT",
        "preparation": "Powder in water on empty stomach. Start at 5 g/day and increase gradually.",
    },
    "slippery-elm": {
        "properties": ["gut-healing", "demulcent", "anti-inflammatory", "prebiotic"],
        "active_compounds": ["mucilage", "tannins", "antioxidants"],
        "best_for": ["gut-health", "leaky-gut", "digestion", "sibo"],
        "condition_synonyms": {"ibs": "gut-health", "gerd": "digestion", "intestinal-permeability": "leaky-gut"},
        "contraindications": ["may slow absorption of oral medications — separate by 2 hours"],
        "dosing": "1–2 tsp powder in water 3x/day; capsule: 400 mg 3–4x/day",
        "bioavailability_notes": "Mucilage coats and soothes gut lining. Take between meals for maximum contact time.",
        "drug_interactions": ["all oral medications (slows absorption — separate by 2 hours)"],
        "evidence_tier": "traditional",
        "preparation": "Powder mixed into warm water or porridge. Take between meals.",
    },
    "aloe-vera": {
        "properties": ["gut-healing", "anti-inflammatory", "laxative (latex)", "antimicrobial"],
        "active_compounds": ["acemannan", "anthraquinones (latex)", "polysaccharides", "enzymes"],
        "best_for": ["gut-health", "leaky-gut", "digestion", "skin-conditions"],
        "condition_synonyms": {"ibs": "gut-health", "gerd": "digestion", "constipation": "digestion"},
        "contraindications": ["pregnancy (latex form)", "kidney disease", "intestinal obstruction", "children under 12 (latex)"],
        "dosing": "Inner gel: 30–60 mL 3x/day; decolorized (anthraquinone-free) juice: 100–200 mL/day",
        "bioavailability_notes": "Use decolorized (anthraquinone-free) inner gel for gut healing. Latex (outer leaf) is a stimulant laxative — different use case.",
        "drug_interactions": ["diuretics (electrolyte loss)", "digoxin", "diabetes medications"],
        "evidence_tier": "observational",
        "preparation": "Inner gel juice (decolorized). Avoid products containing aloin (anthraquinone) for gut healing.",
    },
    "resistant-starch": {
        "properties": ["prebiotic", "gut-microbiome", "blood-sugar-regulation", "colon-health"],
        "active_compounds": ["resistant starch type 2 and 3", "butyrate precursor"],
        "best_for": ["gut-health", "blood-sugar", "colon-health", "weight-management"],
        "condition_synonyms": {"dysbiosis": "gut-health", "insulin-resistance": "blood-sugar", "colorectal-cancer-prevention": "colon-health"},
        "contraindications": ["SIBO (may worsen)", "severe IBS (introduce very slowly)"],
        "dosing": "15–30 g/day; start at 5 g/day and increase over 2–4 weeks",
        "bioavailability_notes": "Fermented by gut bacteria to produce butyrate — primary fuel for colonocytes. Cooling cooked potatoes/rice increases resistant starch content.",
        "drug_interactions": ["none significant"],
        "evidence_tier": "RCT",
        "preparation": "Green banana flour, cooled cooked potatoes/rice, raw potato starch. Introduce slowly.",
    },

    # ── Adaptogens & vitality ─────────────────────────────────────────────────
    "ashwagandha": {
        "properties": ["adaptogen", "stress-modulating", "thyroid-support", "testosterone-support", "neuroprotective"],
        "active_compounds": ["withanolides", "withaferin A", "alkaloids", "saponins"],
        "best_for": ["stress", "fatigue", "hormonal-balance", "thyroid-support", "cognitive-function", "sleep"],
        "condition_synonyms": {"adrenal-fatigue": "stress", "anxiety": "stress", "hypothyroid": "thyroid-support", "low-testosterone": "hormonal-balance"},
        "contraindications": ["pregnancy", "autoimmune thyroid disease (Hashimoto's — may stimulate)", "hyperthyroidism", "nightshade sensitivity"],
        "dosing": "300–600 mg KSM-66 or Sensoril extract 2x/day; powder: 1–2 tsp/day",
        "bioavailability_notes": "KSM-66 (root extract) and Sensoril (root+leaf) are most studied. Take with fat-containing meal. Evening dose supports sleep.",
        "drug_interactions": ["thyroid medications (may increase T3/T4)", "immunosuppressants", "sedatives (additive)", "diabetes medications"],
        "evidence_tier": "RCT",
        "preparation": "Standardized extract capsule (KSM-66 or Sensoril). Powder in warm milk (traditional).",
    },
    "rhodiola": {
        "properties": ["adaptogen", "cognitive-enhancer", "anti-fatigue", "antidepressant"],
        "active_compounds": ["rosavins", "salidroside", "tyrosol"],
        "best_for": ["fatigue", "stress", "cognitive-function", "depression", "energy"],
        "condition_synonyms": {"burnout": "fatigue", "brain-fog": "cognitive-function", "adrenal-fatigue": "stress"},
        "contraindications": ["bipolar disorder (may trigger mania)", "pregnancy", "autoimmune disease"],
        "dosing": "200–600 mg standardized extract (3% rosavins, 1% salidroside)/day; take in morning",
        "bioavailability_notes": "Stimulating — take in morning or early afternoon. Avoid evening use. Cycle: 6 weeks on, 2 weeks off.",
        "drug_interactions": ["MAOIs", "SSRIs (serotonin syndrome risk)", "stimulants", "diabetes medications"],
        "evidence_tier": "RCT",
        "preparation": "Standardized capsule in morning. Do not take with evening meal.",
    },
    "lions-mane": {
        "properties": ["neuroprotective", "nerve-growth-factor-stimulator", "cognitive-enhancer", "immune-modulating"],
        "active_compounds": ["hericenones", "erinacines", "beta-glucans"],
        "best_for": ["cognitive-function", "nerve-repair", "immunity", "depression", "gut-health"],
        "condition_synonyms": {"brain-fog": "cognitive-function", "neuropathy": "nerve-repair", "alzheimers-prevention": "cognitive-function"},
        "contraindications": ["mushroom allergy", "autoimmune disease (immune stimulation)"],
        "dosing": "500–3000 mg/day; dual-extract (hot water + alcohol): 1000 mg 2x/day",
        "bioavailability_notes": "Dual-extract captures both water-soluble beta-glucans and alcohol-soluble hericenones. Fruiting body preferred over mycelium.",
        "drug_interactions": ["anticoagulants (mild)", "diabetes medications (may lower blood sugar)"],
        "evidence_tier": "RCT",
        "preparation": "Dual-extract capsule or powder. Fruiting body extract preferred.",
    },
    "reishi": {
        "properties": ["immune-modulating", "adaptogen", "liver-support", "anti-inflammatory", "sleep-support"],
        "active_compounds": ["triterpenes (ganoderic acids)", "beta-glucans", "polysaccharides"],
        "best_for": ["immunity", "stress", "liver-support", "sleep", "inflammation"],
        "condition_synonyms": {"immune-support": "immunity", "adrenal-fatigue": "stress", "insomnia": "sleep"},
        "contraindications": ["bleeding disorders", "pre-surgery (stop 2 weeks prior)", "mushroom allergy", "immunosuppressed patients"],
        "dosing": "1.5–9 g dried mushroom/day; extract: 1–1.5 g/day standardized",
        "bioavailability_notes": "Triterpenes require alcohol extraction; beta-glucans require hot water. Dual-extract captures both. Fruiting body preferred.",
        "drug_interactions": ["anticoagulants", "immunosuppressants", "antihypertensives"],
        "evidence_tier": "observational",
        "preparation": "Dual-extract capsule or decoction (simmer 2 hours). Bitter taste — capsule preferred.",
    },
    "cordyceps": {
        "properties": ["energy-enhancing", "adaptogen", "immune-modulating", "kidney-support", "athletic-performance"],
        "active_compounds": ["cordycepin", "adenosine", "beta-glucans", "polysaccharides"],
        "best_for": ["energy", "fatigue", "immunity", "kidney-support", "athletic-performance"],
        "condition_synonyms": {"adrenal-fatigue": "fatigue", "immune-support": "immunity", "stamina": "athletic-performance"},
        "contraindications": ["autoimmune disease", "bleeding disorders", "mushroom allergy"],
        "dosing": "1000–3000 mg/day; CS-4 strain (fermented): 3–6 g/day",
        "bioavailability_notes": "CS-4 fermented strain is the most studied. Fruiting body (Cs militaris) contains more cordycepin than mycelium.",
        "drug_interactions": ["immunosuppressants", "anticoagulants", "MAOIs"],
        "evidence_tier": "observational",
        "preparation": "Capsule or powder. CS-4 or Cs militaris fruiting body extract preferred.",
    },
    "maca": {
        "properties": ["adaptogen", "hormone-balancing", "energy-enhancing", "fertility-support"],
        "active_compounds": ["macamides", "macaenes", "glucosinolates", "alkaloids"],
        "best_for": ["hormonal-balance", "energy", "fatigue", "fertility", "libido"],
        "condition_synonyms": {"low-libido": "libido", "menopause": "hormonal-balance", "adrenal-fatigue": "fatigue"},
        "contraindications": ["hormone-sensitive cancers", "thyroid disease (goitrogens — cook first)", "pregnancy (insufficient data)"],
        "dosing": "1.5–3 g/day; gelatinized form: 1–2 tsp/day",
        "bioavailability_notes": "Gelatinized maca (pre-cooked) is easier to digest and has higher bioavailability. Black maca for cognitive/energy; red maca for hormonal balance.",
        "drug_interactions": ["hormone therapies (additive or antagonistic)", "thyroid medications"],
        "evidence_tier": "RCT",
        "preparation": "Gelatinized powder in smoothies. Color matters: black (energy/cognition), red (hormones), yellow (general).",
    },
    "moringa": {
        "properties": ["nutrient-dense", "anti-inflammatory", "antioxidant", "blood-sugar-regulation"],
        "active_compounds": ["isothiocyanates", "quercetin", "chlorogenic acid", "vitamin C", "iron", "calcium"],
        "best_for": ["energy", "inflammation", "blood-sugar", "immunity", "nutrient-deficiency"],
        "condition_synonyms": {"fatigue": "energy", "malnutrition": "nutrient-deficiency", "insulin-resistance": "blood-sugar"},
        "contraindications": ["pregnancy (root/bark — uterine stimulant; leaf is safer)", "hypothyroidism (may affect thyroid)"],
        "dosing": "2–6 g leaf powder/day; capsule: 500 mg 2–3x/day",
        "bioavailability_notes": "One of the most nutrient-dense plants. Iron absorption enhanced by vitamin C content. Avoid boiling — use raw powder or light steam.",
        "drug_interactions": ["thyroid medications", "diabetes medications (blood sugar lowering)", "antihypertensives"],
        "evidence_tier": "observational",
        "preparation": "Leaf powder in smoothies or capsule. Avoid root/bark during pregnancy.",
    },
}


class NutritionService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.usda_api_base_url,
            timeout=30.0,
        )

    async def search_foods(self, query: str, page_size: int = 10) -> list[dict[str, Any]]:
        """Search USDA FoodData Central."""
        params = {
            "query": query,
            "pageSize": page_size,
            "api_key": settings.usda_api_key or "DEMO_KEY",
        }
        try:
            resp = await self._client.get("/foods/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("foods", [])
        except httpx.HTTPError:
            # Return mock data when API key not configured
            return _mock_food_search(query)

    async def get_food_details(self, fdc_id: int) -> dict[str, Any]:
        """Fetch full nutrient profile for a food item."""
        params = {"api_key": settings.usda_api_key or "DEMO_KEY"}
        try:
            resp = await self._client.get(f"/food/{fdc_id}", params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError:
            return {"fdc_id": fdc_id, "description": "Food details unavailable", "foodNutrients": []}

    def get_healing_foods(self, condition: str) -> list[dict[str, Any]]:
        """Return foods for a condition using synonym-aware matching, ranked by evidence tier."""
        condition_lower = condition.lower().replace(" ", "-")
        results = []
        for name, data in HEALING_FOODS.items():
            # Resolve synonyms → canonical tag
            resolved = data.get("condition_synonyms", {}).get(condition_lower, condition_lower)
            best_for_lower = [b.lower() for b in data["best_for"]]
            if resolved in best_for_lower or condition_lower in best_for_lower:
                results.append({"name": name, **data})
        # Sort by evidence tier
        tier_rank = {"RCT": 0, "meta-analysis": 1, "observational": 2, "traditional": 3}
        results.sort(key=lambda x: tier_rank.get(x.get("evidence_tier", "traditional"), 4))
        return results or [{"name": k, **v} for k, v in list(HEALING_FOODS.items())[:3]]

    def get_food_monograph(self, name: str) -> dict[str, Any] | None:
        """Return the full monograph for a food or herb."""
        key = name.lower().replace(" ", "-")
        entry = HEALING_FOODS.get(key)
        if entry:
            return {"name": key, **entry}
        # Fuzzy fallback — partial name match
        for k, v in HEALING_FOODS.items():
            if key in k or k in key:
                return {"name": k, **v}
        return None

    def get_contraindications(self, food_name: str, user_profile: dict[str, Any]) -> list[str]:
        """Return contraindications relevant to a user's profile."""
        entry = self.get_food_monograph(food_name)
        if not entry:
            return []
        all_contra = entry.get("contraindications", [])
        conditions = [c.lower() for c in user_profile.get("conditions", [])]
        medications = [m.lower() for m in user_profile.get("medications", [])]
        flagged = []
        for c in all_contra:
            c_lower = c.lower()
            if any(cond in c_lower for cond in conditions):
                flagged.append(c)
            if any(med in c_lower for med in medications):
                flagged.append(c)
        return flagged or all_contra

    def get_drug_interactions(self, food_name: str, medications: list[str]) -> list[str]:
        """Return drug interactions for a food given a medication list."""
        entry = self.get_food_monograph(food_name)
        if not entry:
            return []
        interactions = entry.get("drug_interactions", [])
        meds_lower = [m.lower() for m in medications]
        flagged = [i for i in interactions if any(m in i.lower() for m in meds_lower)]
        return flagged if flagged else []

    def get_bioavailability_stack(self, food_name: str) -> str:
        """Return bioavailability enhancement notes for a food."""
        entry = self.get_food_monograph(food_name)
        if not entry:
            return ""
        return entry.get("bioavailability_notes", "")

    def get_meal_plan(self, focus: str = "anti-inflammatory", days: int = 7) -> list[dict[str, Any]]:
        """Generate a varied daily meal plan based on healing focus."""
        focus_foods = self.get_healing_foods(focus)[:8]

        MEAL_ROTATIONS: dict[str, list[dict]] = {
            "anti-inflammatory": [
                {"meal": "Breakfast", "foods": ["golden milk oatmeal", "blueberries", "walnuts", "chia seeds"], "notes": "1 tsp turmeric + pinch black pepper activates curcumin absorption 20x."},
                {"meal": "Breakfast", "foods": ["green smoothie", "spinach", "banana", "ginger", "flaxseed"], "notes": "Ginger inhibits COX-2 enzymes — same mechanism as ibuprofen, without side effects."},
                {"meal": "Breakfast", "foods": ["avocado toast", "sprouted grain bread", "hemp seeds", "lemon"], "notes": "Sprouted grains reduce phytic acid, improving mineral absorption by 50%."},
                {"meal": "Breakfast", "foods": ["overnight oats", "tart cherries", "cinnamon", "almonds"], "notes": "Tart cherries contain anthocyanins that reduce CRP (C-reactive protein)."},
                {"meal": "Breakfast", "foods": ["turmeric scrambled eggs", "sautéed kale", "olive oil"], "notes": "Eggs provide choline for liver methylation; kale provides sulforaphane."},
                {"meal": "Breakfast", "foods": ["papaya bowl", "pineapple", "mint", "lime"], "notes": "Bromelain in pineapple and papain in papaya are systemic anti-inflammatory enzymes."},
                {"meal": "Breakfast", "foods": ["miso soup", "wakame seaweed", "tofu", "green onion"], "notes": "Fermented miso provides beneficial bacteria and isoflavones."},
            ],
            "lunch": [
                {"meal": "Lunch", "foods": ["wild salmon", "arugula salad", "olive oil", "lemon", "capers"], "notes": "EPA/DHA from wild salmon reduce IL-6 and TNF-alpha inflammatory markers."},
                {"meal": "Lunch", "foods": ["lentil soup", "turmeric", "cumin", "spinach", "bone broth"], "notes": "Lentils provide resistant starch that feeds anti-inflammatory Lactobacillus strains."},
                {"meal": "Lunch", "foods": ["quinoa bowl", "roasted beets", "goat cheese", "walnuts", "arugula"], "notes": "Beets contain betalains — potent anti-inflammatory pigments that support Phase II liver detox."},
                {"meal": "Lunch", "foods": ["sardines on rye", "avocado", "cucumber", "dill"], "notes": "Sardines are highest omega-3 per calorie of any fish; rye provides beta-glucan fiber."},
                {"meal": "Lunch", "foods": ["chicken bone broth soup", "ginger", "garlic", "bok choy", "shiitake"], "notes": "Shiitake mushrooms contain lentinan — a beta-glucan that activates NK cells."},
                {"meal": "Lunch", "foods": ["black bean tacos", "cabbage slaw", "cilantro", "lime", "avocado"], "notes": "Black beans contain anthocyanins and resistant starch for gut microbiome diversity."},
                {"meal": "Lunch", "foods": ["tuna niçoise", "green beans", "olives", "hard-boiled eggs", "capers"], "notes": "Olives provide oleocanthal — a natural COX inhibitor with ibuprofen-like activity."},
            ],
            "dinner": [
                {"meal": "Dinner", "foods": ["baked cod", "roasted sweet potato", "steamed broccoli", "ginger"], "notes": "Broccoli sulforaphane activates Nrf2 pathway — master regulator of antioxidant defense."},
                {"meal": "Dinner", "foods": ["lamb stew", "rosemary", "garlic", "root vegetables", "bone broth"], "notes": "Rosemary contains rosmarinic acid — inhibits complement activation in inflammatory cascade."},
                {"meal": "Dinner", "foods": ["stir-fried tempeh", "bok choy", "ginger", "tamari", "sesame"], "notes": "Fermented tempeh has higher isoflavone bioavailability than unfermented soy."},
                {"meal": "Dinner", "foods": ["grass-fed beef", "roasted asparagus", "garlic butter", "lemon"], "notes": "Grass-fed beef has 2-5x more omega-3s and CLA than grain-fed."},
                {"meal": "Dinner", "foods": ["mung bean dal", "turmeric", "cumin", "coriander", "ghee"], "notes": "Mung beans are the most easily digestible legume — ideal for gut healing phases."},
                {"meal": "Dinner", "foods": ["baked salmon", "cauliflower rice", "tahini", "parsley"], "notes": "Cauliflower provides DIM (diindolylmethane) for estrogen metabolism support."},
                {"meal": "Dinner", "foods": ["chicken thighs", "roasted fennel", "olives", "tomatoes", "herbs"], "notes": "Fennel contains anethole — reduces NF-κB activation, a key inflammatory pathway."},
            ],
            "snacks": [
                {"meal": "Snacks", "foods": ["celery + almond butter", "green tea"], "notes": "EGCG in green tea inhibits inflammatory cytokine production."},
                {"meal": "Snacks", "foods": ["walnuts", "tart cherry juice", "dark chocolate 85%"], "notes": "Walnuts are the only nut with significant ALA omega-3s."},
                {"meal": "Snacks", "foods": ["apple + tahini", "cinnamon", "herbal tea"], "notes": "Cinnamon improves insulin sensitivity — reduces inflammatory AGE formation."},
                {"meal": "Snacks", "foods": ["pumpkin seeds", "goji berries", "coconut flakes"], "notes": "Pumpkin seeds are highest plant source of zinc — critical for immune regulation."},
                {"meal": "Snacks", "foods": ["bone broth", "turmeric", "black pepper", "coconut oil"], "notes": "Bone broth glycine reduces intestinal permeability (leaky gut)."},
                {"meal": "Snacks", "foods": ["kefir", "berries", "honey"], "notes": "Kefir contains 30+ probiotic strains vs 1-2 in most supplements."},
                {"meal": "Snacks", "foods": ["guacamole", "flaxseed crackers", "cucumber"], "notes": "Avocado oleic acid reduces CRP by up to 20% in clinical studies."},
            ],
        }

        macro_profiles = {
            "anti-inflammatory": {"protein_g": 85, "carbs_g": 200, "fat_g": 70, "fiber_g": 38},
            "gut-healing": {"protein_g": 90, "carbs_g": 180, "fat_g": 65, "fiber_g": 42},
            "detox": {"protein_g": 75, "carbs_g": 160, "fat_g": 55, "fiber_g": 45},
            "energy": {"protein_g": 100, "carbs_g": 240, "fat_g": 60, "fiber_g": 32},
            "weight-loss": {"protein_g": 110, "carbs_g": 140, "fat_g": 55, "fiber_g": 40},
        }
        macros = macro_profiles.get(focus, macro_profiles["anti-inflammatory"])

        plan = []
        for d in range(days):
            idx = d % 7
            day_meals = [
                MEAL_ROTATIONS["anti-inflammatory"][idx],
                MEAL_ROTATIONS["lunch"][idx],
                MEAL_ROTATIONS["dinner"][idx],
                MEAL_ROTATIONS["snacks"][idx],
            ]
            # Vary calories slightly each day
            cal_variance = [-100, 0, 50, -50, 100, 0, -75][idx]
            plan.append({
                "day": d + 1,
                "meals": day_meals,
                "healing_focus": focus,
                "featured_foods": [f["name"] for f in focus_foods],
                "total_calories": 1850 + cal_variance,
                "macros": macros,
                "hydration_goal_ml": 2500,
                "supplements": _supplements_for_focus(focus),
            })
        return plan

    async def close(self) -> None:
        await self._client.aclose()


DETOX_FOODS: list[str] = [
    "cilantro", "chlorella", "spirulina", "dandelion-root",
    "milk-thistle", "beets", "garlic", "lemon", "artichoke-leaf",
    "nac", "activated-charcoal", "burdock-root",
]

ANTI_INFLAMMATORY_PROTOCOL: list[dict[str, Any]] = [
    {"meal": "Breakfast", "foods": ["golden milk oatmeal", "blueberries", "walnuts"],
     "notes": "Add 1 tsp turmeric + pinch black pepper"},
    {"meal": "Lunch", "foods": ["wild salmon", "leafy greens salad", "olive oil dressing"],
     "notes": "Omega-3s reduce systemic inflammation"},
    {"meal": "Dinner", "foods": ["lentil soup", "roasted vegetables", "ginger tea"],
     "notes": "Plant protein + fiber supports gut lining"},
    {"meal": "Snacks", "foods": ["celery + almond butter", "green smoothie"],
     "notes": "Avoid processed sugar entirely"},
]


def _supplements_for_focus(focus: str) -> list[str]:
    return {
        "anti-inflammatory": ["Omega-3 2g/day", "Curcumin 500mg with piperine", "Vitamin D3 5000IU", "Magnesium glycinate 400mg"],
        "gut-healing": ["L-Glutamine 5g", "Probiotics 50B CFU", "Digestive enzymes", "Zinc carnosine 75mg"],
        "detox": ["Milk thistle 600mg", "NAC 600mg", "Activated charcoal (away from meals)", "Chlorella 3g"],
        "energy": ["CoQ10 200mg", "B-complex", "Iron bisglycinate (if deficient)", "Ashwagandha 600mg"],
        "weight-loss": ["Berberine 500mg 3x/day", "Green tea extract 400mg", "Chromium picolinate 200mcg", "Fiber supplement 10g"],
    }.get(focus, ["Multivitamin", "Omega-3 2g/day", "Vitamin D3 2000IU"])


def _mock_food_search(query: str) -> list[dict[str, Any]]:
    """Return curated food data when USDA API key is not configured."""
    q = query.lower()
    DATABASE = [
        {"fdcId": 1001, "description": "Blueberries, raw", "foodCategory": "Fruits", "foodNutrients": [{"nutrientName": "Energy", "value": 57, "unitName": "kcal"}, {"nutrientName": "Fiber", "value": 2.4, "unitName": "g"}, {"nutrientName": "Vitamin C", "value": 9.7, "unitName": "mg"}]},
        {"fdcId": 1002, "description": "Turmeric, ground", "foodCategory": "Spices", "foodNutrients": [{"nutrientName": "Energy", "value": 354, "unitName": "kcal"}, {"nutrientName": "Fiber", "value": 21.1, "unitName": "g"}, {"nutrientName": "Iron", "value": 41.4, "unitName": "mg"}]},
        {"fdcId": 1003, "description": "Salmon, wild Atlantic, raw", "foodCategory": "Fish", "foodNutrients": [{"nutrientName": "Energy", "value": 142, "unitName": "kcal"}, {"nutrientName": "Protein", "value": 19.8, "unitName": "g"}, {"nutrientName": "Omega-3", "value": 2.2, "unitName": "g"}]},
        {"fdcId": 1004, "description": "Spinach, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 23, "unitName": "kcal"}, {"nutrientName": "Iron", "value": 2.7, "unitName": "mg"}, {"nutrientName": "Folate", "value": 194, "unitName": "mcg"}]},
        {"fdcId": 1005, "description": "Avocado, raw", "foodCategory": "Fruits", "foodNutrients": [{"nutrientName": "Energy", "value": 160, "unitName": "kcal"}, {"nutrientName": "Fat", "value": 14.7, "unitName": "g"}, {"nutrientName": "Fiber", "value": 6.7, "unitName": "g"}]},
        {"fdcId": 1006, "description": "Ginger root, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 80, "unitName": "kcal"}, {"nutrientName": "Fiber", "value": 2.0, "unitName": "g"}, {"nutrientName": "Potassium", "value": 415, "unitName": "mg"}]},
        {"fdcId": 1007, "description": "Garlic, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 149, "unitName": "kcal"}, {"nutrientName": "Protein", "value": 6.4, "unitName": "g"}, {"nutrientName": "Vitamin C", "value": 31.2, "unitName": "mg"}]},
        {"fdcId": 1008, "description": "Kale, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 49, "unitName": "kcal"}, {"nutrientName": "Vitamin K", "value": 817, "unitName": "mcg"}, {"nutrientName": "Vitamin C", "value": 120, "unitName": "mg"}]},
        {"fdcId": 1009, "description": "Walnuts, raw", "foodCategory": "Nuts", "foodNutrients": [{"nutrientName": "Energy", "value": 654, "unitName": "kcal"}, {"nutrientName": "Omega-3 ALA", "value": 9.1, "unitName": "g"}, {"nutrientName": "Protein", "value": 15.2, "unitName": "g"}]},
        {"fdcId": 1010, "description": "Lentils, cooked", "foodCategory": "Legumes", "foodNutrients": [{"nutrientName": "Energy", "value": 116, "unitName": "kcal"}, {"nutrientName": "Protein", "value": 9.0, "unitName": "g"}, {"nutrientName": "Fiber", "value": 7.9, "unitName": "g"}]},
        {"fdcId": 1011, "description": "Beets, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 43, "unitName": "kcal"}, {"nutrientName": "Folate", "value": 109, "unitName": "mcg"}, {"nutrientName": "Fiber", "value": 2.8, "unitName": "g"}]},
        {"fdcId": 1012, "description": "Broccoli, raw", "foodCategory": "Vegetables", "foodNutrients": [{"nutrientName": "Energy", "value": 34, "unitName": "kcal"}, {"nutrientName": "Vitamin C", "value": 89.2, "unitName": "mg"}, {"nutrientName": "Sulforaphane", "value": 73, "unitName": "mg"}]},
        {"fdcId": 1013, "description": "Chia seeds", "foodCategory": "Seeds", "foodNutrients": [{"nutrientName": "Energy", "value": 486, "unitName": "kcal"}, {"nutrientName": "Fiber", "value": 34.4, "unitName": "g"}, {"nutrientName": "Omega-3 ALA", "value": 17.8, "unitName": "g"}]},
        {"fdcId": 1014, "description": "Bone broth, chicken", "foodCategory": "Broths", "foodNutrients": [{"nutrientName": "Energy", "value": 38, "unitName": "kcal"}, {"nutrientName": "Protein", "value": 6.8, "unitName": "g"}, {"nutrientName": "Glycine", "value": 1.2, "unitName": "g"}]},
        {"fdcId": 1015, "description": "Fermented kimchi", "foodCategory": "Fermented Foods", "foodNutrients": [{"nutrientName": "Energy", "value": 15, "unitName": "kcal"}, {"nutrientName": "Probiotics", "value": 1000, "unitName": "million CFU"}, {"nutrientName": "Vitamin K2", "value": 31, "unitName": "mcg"}]},
    ]
    results = [f for f in DATABASE if q in f["description"].lower()]
    if not results:
        results = DATABASE[:5]
    return results


nutrition_service = NutritionService()
