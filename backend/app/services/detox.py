"""Detox protocol library — 7 protocols covering liver, heavy metals, parasites,
candida/SIBO, gut 5R reset, mold/mycotoxin, and gentle whole-foods cleanse."""

from typing import Any

DETOX_PROTOCOLS: list[dict[str, Any]] = [
    {
        "id": "gentle-7day",
        "name": "7-Day Gentle Cleanse",
        "description": "A whole-foods reset that eliminates common inflammatory triggers while supporting liver and gut function.",
        "duration_days": 7,
        "intensity": "gentle",
        "contraindications": ["pregnancy", "eating-disorders", "underweight"],
        "supplements": ["milk thistle", "probiotics", "magnesium glycinate", "vitamin C"],
        "phases": [
            {
                "phase": 1,
                "days": "1-2",
                "name": "Preparation",
                "focus": "Eliminate caffeine, alcohol, sugar, gluten, and dairy",
                "eat": ["fruits", "vegetables", "brown rice", "lentils", "herbal teas"],
                "avoid": ["coffee", "alcohol", "processed foods", "refined sugar"],
                "practices": ["dry brushing", "10-min morning walk", "journaling"],
                "expected_symptoms": ["mild headache", "fatigue", "cravings"],
            },
            {
                "phase": 2,
                "days": "3-5",
                "name": "Deep Cleanse",
                "focus": "Maximize liver and lymphatic support",
                "eat": ["leafy greens", "beets", "lemon water", "garlic", "cilantro", "dandelion tea"],
                "avoid": ["all animal products", "oils except flaxseed"],
                "practices": ["epsom salt bath", "rebounding", "castor oil pack"],
                "expected_symptoms": ["increased energy by day 4", "clearer skin", "improved sleep"],
            },
            {
                "phase": 3,
                "days": "6-7",
                "name": "Reintegration",
                "focus": "Slowly reintroduce foods and assess reactions",
                "eat": ["wild fish", "eggs", "fermented foods", "healthy fats"],
                "avoid": ["gluten", "dairy", "alcohol"],
                "practices": ["food journal", "gratitude practice", "gentle yoga"],
                "expected_symptoms": ["clarity", "lightness", "improved digestion"],
            },
        ],
    },
    {
        "id": "liver-21day",
        "name": "21-Day Liver Reset",
        "description": "A structured protocol targeting liver regeneration, bile flow optimization, and metabolic reset.",
        "duration_days": 21,
        "intensity": "moderate",
        "contraindications": ["pregnancy", "liver-disease-advanced", "medications-requiring-food"],
        "supplements": ["NAC", "alpha-lipoic acid", "milk thistle", "B-complex", "zinc"],
        "phases": [
            {
                "phase": 1,
                "days": "1-7",
                "name": "Elimination",
                "focus": "Remove all liver stressors",
                "eat": ["cruciferous vegetables", "beets", "artichokes", "lemon", "turmeric"],
                "avoid": ["alcohol", "caffeine", "sugar", "processed foods", "seed oils"],
                "practices": ["morning lemon water", "castor oil packs", "infrared sauna"],
                "expected_symptoms": ["detox headaches", "fatigue", "emotional releases"],
            },
            {
                "phase": 2,
                "days": "8-14",
                "name": "Regeneration",
                "focus": "Provide liver-building nutrients",
                "eat": ["eggs", "wild salmon", "liver (organic)", "beets", "leafy greens"],
                "avoid": ["alcohol", "sugar", "processed foods"],
                "practices": ["coffee enema (optional)", "rebounding", "breathwork"],
                "expected_symptoms": ["increased energy", "better sleep", "weight loss"],
            },
            {
                "phase": 3,
                "days": "15-21",
                "name": "Optimization",
                "focus": "Establish sustainable liver-supportive habits",
                "eat": ["Mediterranean-style diet", "bitter greens", "fermented foods"],
                "avoid": ["alcohol", "refined sugar"],
                "practices": ["daily movement", "stress management", "sleep optimization"],
                "expected_symptoms": ["mental clarity", "stable energy", "improved skin"],
            },
        ],
    },
    {
        "id": "heavy-metal-30day",
        "name": "30-Day Heavy Metal Detox",
        "description": "Targeted protocol for mobilizing and safely eliminating heavy metals using food-based chelators.",
        "duration_days": 30,
        "intensity": "intensive",
        "contraindications": ["pregnancy", "kidney-disease", "amalgam-fillings-recent-removal"],
        "supplements": ["chlorella", "spirulina", "modified citrus pectin", "DMSA (medical supervision)", "glutathione"],
        "phases": [
            {
                "phase": 1,
                "days": "1-10",
                "name": "Binding Preparation",
                "focus": "Prepare elimination pathways before mobilizing metals",
                "eat": ["high-fiber foods", "cilantro", "garlic", "onions", "sulfur-rich vegetables"],
                "avoid": ["fish high in mercury", "alcohol", "sugar"],
                "practices": ["sauna", "epsom salt baths", "adequate hydration (3L/day)"],
                "expected_symptoms": ["fatigue", "brain fog (temporary)", "digestive changes"],
            },
            {
                "phase": 2,
                "days": "11-25",
                "name": "Active Chelation",
                "focus": "Mobilize and bind heavy metals",
                "eat": ["cilantro smoothies", "chlorella", "wild blueberries", "Atlantic dulse"],
                "avoid": ["all fish", "alcohol", "sugar", "processed foods"],
                "practices": ["daily sauna", "rebounding", "castor oil packs"],
                "expected_symptoms": ["possible symptom flare (metals mobilizing)", "improved cognition after week 3"],
            },
            {
                "phase": 3,
                "days": "26-30",
                "name": "Restoration",
                "focus": "Replenish minerals displaced during chelation",
                "eat": ["mineral-rich foods", "bone broth", "sea vegetables", "organ meats"],
                "avoid": ["alcohol", "sugar"],
                "practices": ["mineral baths", "grounding/earthing", "sleep prioritization"],
                "expected_symptoms": ["significant energy improvement", "mental clarity", "reduced inflammation"],
            },
        ],
    },
    {
        "id": "parasite-21day",
        "name": "21-Day Parasite Cleanse",
        "description": "A structured antiparasitic protocol using the herbal trinity (wormwood, black walnut hull, clove) plus biofilm disruptors and gut restoration. Moon-phase timing enhances efficacy — parasites are more active around the full moon.",
        "duration_days": 21,
        "intensity": "moderate",
        "contraindications": ["pregnancy", "breastfeeding", "children under 12", "epilepsy", "kidney disease", "liver disease (severe)", "immunocompromised"],
        "supplements": ["wormwood", "black walnut hull tincture", "clove (ground)", "mimosa pudica seed", "activated charcoal (binder)", "bentonite clay (binder)", "probiotics (restoration phase)"],
        "herxheimer_management": "Expect die-off symptoms (fatigue, headache, bloating, skin breakouts) especially days 3–7. Manage with: activated charcoal 1–2 g between meals, bentonite clay 1 tsp in water, epsom salt baths, increased water intake (3L/day), rest.",
        "moon_phase_note": "Parasites are most active and vulnerable 3 days before and after the full moon. Intensify protocol (double dose) during this window for maximum efficacy.",
        "phases": [
            {
                "phase": 1,
                "days": "1-7",
                "name": "Starve & Prepare",
                "focus": "Eliminate parasite food sources; open drainage pathways",
                "eat": ["pumpkin seeds (raw, 1 cup/day on empty stomach)", "papaya seeds (1 tbsp/day)", "raw garlic (3–4 cloves/day)", "coconut oil (2–3 tbsp/day)", "pomegranate juice", "fermented vegetables (small amounts)", "high-fiber vegetables"],
                "avoid": ["all sugar and sweeteners", "refined carbohydrates", "alcohol", "pork and shellfish", "processed foods", "dairy"],
                "supplements_this_phase": ["mimosa pudica seed 1g 2x/day on empty stomach", "activated charcoal 500mg between meals", "digestive enzymes with meals"],
                "practices": ["morning lemon water (16 oz)", "castor oil pack over abdomen 3x/week", "dry brushing daily", "epsom salt bath 2x/week"],
                "expected_symptoms": ["bloating", "increased bowel movements", "mild fatigue", "cravings for sugar"],
            },
            {
                "phase": 2,
                "days": "8-18",
                "name": "Active Kill Phase",
                "focus": "Deploy antiparasitic herbs; manage die-off with binders",
                "eat": ["continue Phase 1 diet", "add bone broth daily", "pumpkin seeds", "raw garlic", "ginger tea", "anti-inflammatory foods"],
                "avoid": ["all sugar", "alcohol", "pork", "shellfish", "processed foods"],
                "supplements_this_phase": [
                    "wormwood 400mg 3x/day (with meals)",
                    "black walnut hull tincture 2mL 3x/day",
                    "clove 500mg ground 3x/day",
                    "mimosa pudica seed 1g 2x/day on empty stomach",
                    "oregano oil 200mg 2x/day",
                    "activated charcoal 1g between meals (2+ hours from supplements)",
                    "bentonite clay 1 tsp in water at bedtime",
                ],
                "practices": ["daily sauna or epsom salt bath", "rebounding 10 min/day (lymphatic drainage)", "castor oil packs 4x/week", "adequate sleep (8+ hours)", "stress management"],
                "expected_symptoms": ["Herxheimer reaction days 10–14 (fatigue, headache, skin breakouts, emotional releases)", "improved energy after day 14", "changes in bowel movements", "possible visible parasites in stool"],
                "herxheimer_protocol": "If symptoms severe: pause herbs for 24–48 hours, increase binders, rest, hydrate. Resume at half dose then build back up.",
            },
            {
                "phase": 3,
                "days": "19-21",
                "name": "Restore & Rebuild",
                "focus": "Replenish gut microbiome; repair intestinal lining",
                "eat": ["fermented foods (kefir, kimchi, sauerkraut)", "bone broth", "prebiotic foods (garlic, onion, leeks)", "L-glutamine rich foods", "collagen-rich foods"],
                "avoid": ["sugar", "alcohol", "processed foods"],
                "supplements_this_phase": ["high-potency probiotics (50+ billion CFU, multi-strain)", "L-glutamine 5g 3x/day", "zinc carnosine 75mg/day", "slippery elm 400mg 3x/day", "colostrum 500mg 2x/day"],
                "practices": ["continue dry brushing", "gentle yoga or walking", "food journal to track improvements"],
                "expected_symptoms": ["improved digestion", "increased energy", "clearer skin", "better sleep", "reduced bloating"],
            },
        ],
    },
    {
        "id": "candida-sibo-30day",
        "name": "30-Day Candida & SIBO Protocol",
        "description": "A comprehensive antifungal and antibacterial protocol targeting Candida overgrowth and Small Intestinal Bacterial Overgrowth (SIBO). Combines strict dietary elimination, antifungal herbs, biofilm disruptors, and microbiome restoration.",
        "duration_days": 30,
        "intensity": "moderate",
        "contraindications": ["pregnancy", "breastfeeding", "severe malnutrition", "eating disorders", "immunocompromised (consult physician)"],
        "supplements": ["oregano oil", "caprylic acid", "berberine", "NAC (biofilm disruptor)", "serrapeptase (biofilm disruptor)", "pau d'arco", "probiotics (Saccharomyces boulardii + Lactobacillus)"],
        "phases": [
            {
                "phase": 1,
                "days": "1-7",
                "name": "Strict Elimination",
                "focus": "Remove all Candida/SIBO food sources; begin biofilm disruption",
                "eat": ["non-starchy vegetables", "leafy greens", "wild fish", "organic poultry", "eggs", "nuts and seeds (except peanuts)", "coconut oil", "olive oil", "bone broth", "herbal teas"],
                "avoid": ["ALL sugar (including fruit, honey, maple syrup)", "ALL grains (including gluten-free)", "alcohol", "dairy (except ghee)", "fermented foods (may worsen SIBO initially)", "starchy vegetables", "legumes", "caffeine"],
                "supplements_this_phase": ["NAC 600mg 3x/day (biofilm disruptor)", "serrapeptase 120,000 IU on empty stomach 2x/day", "digestive enzymes with every meal", "HCl with pepsin (if low stomach acid)"],
                "practices": ["stress reduction (cortisol feeds Candida)", "sleep 8+ hours", "avoid antibiotics unless essential"],
                "expected_symptoms": ["die-off symptoms days 3–5 (fatigue, brain fog, flu-like)", "intense sugar cravings", "mood changes"],
            },
            {
                "phase": 2,
                "days": "8-23",
                "name": "Active Antifungal Phase",
                "focus": "Deploy antifungal herbs; continue biofilm disruption",
                "eat": ["continue Phase 1 diet", "add small amounts of low-sugar fruit (berries only)", "add fermented vegetables slowly if tolerated"],
                "avoid": ["all sugar", "grains", "alcohol", "high-sugar fruits"],
                "supplements_this_phase": [
                    "oregano oil 200mg (70%+ carvacrol) 3x/day with meals",
                    "caprylic acid 1000mg 3x/day with meals",
                    "berberine 500mg 3x/day with meals",
                    "pau d'arco tea 3 cups/day",
                    "Saccharomyces boulardii 5 billion CFU 2x/day (antifungal probiotic)",
                    "NAC 600mg 3x/day",
                    "activated charcoal 500mg between meals for die-off",
                ],
                "practices": ["continue stress management", "sauna 3x/week", "avoid damp/moldy environments"],
                "expected_symptoms": ["gradual improvement in brain fog", "reduced bloating", "possible skin clearing", "improved energy by week 3"],
            },
            {
                "phase": 3,
                "days": "24-30",
                "name": "Microbiome Restoration",
                "focus": "Rebuild diverse, healthy gut microbiome",
                "eat": ["slowly reintroduce fermented foods", "add prebiotic foods (cooked and cooled)", "add low-glycemic fruits", "continue anti-inflammatory diet"],
                "avoid": ["sugar", "alcohol", "processed foods", "gluten (continue avoiding for 3+ months)"],
                "supplements_this_phase": ["high-potency multi-strain probiotics 50+ billion CFU", "L-glutamine 5g 3x/day", "zinc carnosine 75mg/day", "slippery elm 400mg 3x/day", "colostrum 500mg 2x/day"],
                "practices": ["food reintroduction journal", "track symptoms carefully", "continue stress management"],
                "expected_symptoms": ["significantly improved digestion", "mental clarity", "stable energy", "reduced food sensitivities"],
            },
        ],
    },
    {
        "id": "gut-5r-60day",
        "name": "60-Day Gut 5R Reset",
        "description": "The functional medicine 5R framework for comprehensive gut healing: Remove, Replace, Reinoculate, Repair, Rebalance. Addresses root causes of leaky gut, IBS, IBD, food sensitivities, and chronic inflammation.",
        "duration_days": 60,
        "intensity": "gentle",
        "contraindications": ["active GI bleeding", "severe IBD flare (modify under physician supervision)", "recent GI surgery"],
        "supplements": ["digestive enzymes", "HCl with pepsin", "probiotics", "L-glutamine", "zinc carnosine", "collagen peptides", "slippery elm", "aloe vera"],
        "phases": [
            {
                "phase": 1,
                "days": "1-14",
                "name": "Remove",
                "focus": "Eliminate pathogens, irritants, and inflammatory triggers",
                "eat": ["elimination diet: remove gluten, dairy, eggs, soy, corn, peanuts, sugar, alcohol", "focus on whole foods, vegetables, clean proteins", "bone broth daily"],
                "avoid": ["gluten", "dairy", "eggs", "soy", "corn", "peanuts", "sugar", "alcohol", "NSAIDs", "processed foods"],
                "supplements_this_phase": ["antimicrobial herbs if infection suspected (oregano oil, berberine)", "digestive enzymes with meals", "activated charcoal if bloating severe"],
                "practices": ["food and symptom journal", "stress reduction", "adequate sleep"],
                "expected_symptoms": ["withdrawal symptoms days 3–5", "improved digestion by day 10", "reduced bloating"],
            },
            {
                "phase": 2,
                "days": "15-28",
                "name": "Replace",
                "focus": "Restore digestive capacity with enzymes and stomach acid",
                "eat": ["continue elimination diet", "add fermented vegetables slowly", "focus on easily digestible foods"],
                "avoid": ["continue avoiding all Phase 1 foods"],
                "supplements_this_phase": ["HCl with pepsin (if low stomach acid — test with baking soda test)", "full-spectrum digestive enzymes with every meal", "ox bile if fat malabsorption"],
                "practices": ["chew food thoroughly (30 chews per bite)", "eat in relaxed state (parasympathetic)", "avoid drinking large amounts with meals"],
                "expected_symptoms": ["improved digestion", "less bloating after meals", "better nutrient absorption"],
            },
            {
                "phase": 3,
                "days": "29-42",
                "name": "Reinoculate",
                "focus": "Rebuild diverse gut microbiome with probiotics and prebiotics",
                "eat": ["add fermented foods daily (kefir, kimchi, sauerkraut, miso)", "prebiotic foods (garlic, onion, leeks, asparagus, Jerusalem artichoke)", "resistant starch (cooled cooked potatoes/rice, green banana)"],
                "avoid": ["sugar", "alcohol", "processed foods"],
                "supplements_this_phase": ["high-potency multi-strain probiotics 50+ billion CFU", "Saccharomyces boulardii 5 billion CFU", "prebiotic fiber (inulin, FOS) — start low and increase slowly"],
                "practices": ["continue stress management", "outdoor time (microbiome diversity)"],
                "expected_symptoms": ["initial bloating from probiotics/prebiotics (normal)", "improved bowel regularity", "better mood (gut-brain axis)"],
            },
            {
                "phase": 4,
                "days": "43-56",
                "name": "Repair",
                "focus": "Heal intestinal lining and reduce permeability (leaky gut)",
                "eat": ["bone broth 2–3 cups/day", "collagen-rich foods", "zinc-rich foods (pumpkin seeds, oysters)", "vitamin A foods (liver, sweet potato, carrots)", "anti-inflammatory omega-3 foods"],
                "avoid": ["continue avoiding inflammatory foods"],
                "supplements_this_phase": ["L-glutamine 5g 3x/day on empty stomach", "zinc carnosine 75mg/day", "collagen peptides 10–20g/day", "slippery elm 400mg 3x/day", "aloe vera inner gel 60mL 3x/day", "vitamin D3 5000 IU/day"],
                "practices": ["stress management (cortisol increases gut permeability)", "adequate sleep (gut repairs during sleep)", "gentle exercise"],
                "expected_symptoms": ["reduced food sensitivities", "improved skin", "better energy", "reduced systemic inflammation"],
            },
            {
                "phase": 5,
                "days": "57-60",
                "name": "Rebalance",
                "focus": "Establish sustainable lifestyle habits for long-term gut health",
                "eat": ["Mediterranean-style whole foods diet", "diverse plant foods (30+ varieties/week)", "fermented foods daily", "prebiotic foods daily"],
                "avoid": ["processed foods", "excess sugar", "alcohol"],
                "supplements_this_phase": ["maintenance probiotic 10–25 billion CFU", "digestive enzymes as needed", "L-glutamine 5g/day maintenance"],
                "practices": ["food reintroduction (one food every 3 days, track reactions)", "stress management as lifestyle", "regular movement", "sleep optimization"],
                "expected_symptoms": ["significantly improved gut function", "expanded food tolerance", "stable energy", "improved mental clarity"],
            },
        ],
    },
    {
        "id": "mold-mycotoxin-90day",
        "name": "90-Day Mold & Mycotoxin Detox",
        "description": "A comprehensive protocol for mycotoxin illness (CIRS — Chronic Inflammatory Response Syndrome). Requires removal from mold exposure first. Combines binders, antifungals, glutathione support, and nervous system restoration.",
        "duration_days": 90,
        "intensity": "intensive",
        "contraindications": ["pregnancy", "breastfeeding", "active mold exposure (must remediate first)", "severe kidney disease", "cholestyramine contraindications"],
        "critical_first_step": "Remove from mold exposure FIRST. No protocol will work if ongoing exposure continues. Test home with ERMI or HERTSMI-2 test.",
        "supplements": ["cholestyramine (Rx — most effective binder)", "activated charcoal", "bentonite clay", "zeolite", "NAC", "liposomal glutathione", "liposomal vitamin C", "VIP nasal spray (Rx)", "omega-3 fatty acids"],
        "phases": [
            {
                "phase": 1,
                "days": "1-30",
                "name": "Binder Phase",
                "focus": "Bind and eliminate mycotoxins from gut; reduce total toxic burden",
                "eat": ["low-amylose diet (no high-starch foods)", "mold-free foods only (no leftovers, no aged cheese, no peanuts, no corn)", "fresh organic produce", "clean proteins", "anti-inflammatory fats"],
                "avoid": ["ALL high-amylose foods (corn, potatoes, rice, bread)", "aged cheeses", "peanuts", "alcohol", "sugar", "leftovers (mold grows rapidly)", "coffee (often contaminated with mycotoxins)"],
                "supplements_this_phase": ["cholestyramine 4g 4x/day (Rx — most effective)", "OR activated charcoal 1g 3x/day + bentonite clay 1 tsp 2x/day + zeolite 1 tsp/day", "take binders 30 min before meals, 2+ hours from all medications"],
                "practices": ["ERMI/HERTSMI-2 home test", "air purifier with HEPA + activated carbon", "sauna 3–4x/week (infrared preferred)", "nasal rinse daily (mycotoxins colonize sinuses)"],
                "expected_symptoms": ["initial worsening (mobilizing toxins)", "fatigue", "brain fog", "possible mood changes", "gradual improvement by week 3–4"],
            },
            {
                "phase": 2,
                "days": "31-60",
                "name": "Glutathione & Antioxidant Support",
                "focus": "Restore cellular antioxidant capacity; support liver detox pathways",
                "eat": ["continue low-amylose, mold-free diet", "add sulfur-rich foods (eggs, garlic, onions, cruciferous vegetables)", "add glutathione-boosting foods (avocado, asparagus, okra)"],
                "avoid": ["continue Phase 1 avoidances"],
                "supplements_this_phase": ["liposomal glutathione 500mg 2x/day", "NAC 600mg 3x/day", "liposomal vitamin C 2g 2x/day", "alpha-lipoic acid 300mg 2x/day", "B-complex (methylated)", "magnesium glycinate 400mg at night", "continue binders"],
                "practices": ["continue sauna", "lymphatic drainage massage", "gentle exercise (avoid overexertion)", "sleep optimization"],
                "expected_symptoms": ["improved energy", "reduced brain fog", "better sleep", "possible skin improvements"],
            },
            {
                "phase": 3,
                "days": "61-90",
                "name": "Nervous System & Immune Restoration",
                "focus": "Restore HPA axis, immune regulation, and neurological function",
                "eat": ["expand diet gradually", "Mediterranean-style anti-inflammatory diet", "omega-3 rich foods", "polyphenol-rich foods"],
                "avoid": ["continue avoiding mold-prone foods", "sugar", "alcohol"],
                "supplements_this_phase": ["VIP (vasoactive intestinal peptide) nasal spray (Rx — if indicated)", "omega-3 EPA/DHA 3g/day", "vitamin D3 10,000 IU/day (monitor levels)", "vitamin K2 MK-7 200mcg/day", "adaptogenic herbs (ashwagandha, rhodiola)", "continue glutathione support"],
                "practices": ["limbic system retraining (DNRS or Gupta program)", "gentle movement", "stress management", "social connection", "nature exposure"],
                "expected_symptoms": ["significant cognitive improvement", "stable energy", "reduced chemical sensitivities", "improved immune resilience"],
            },
        ],
    },
]


class DetoxService:
    def get_all_protocols(self) -> list[dict[str, Any]]:
        return DETOX_PROTOCOLS

    def get_protocol(self, protocol_id: str) -> dict[str, Any] | None:
        return next((p for p in DETOX_PROTOCOLS if p["id"] == protocol_id), None)

    def get_day_guidance(self, protocol_id: str, day: int) -> dict[str, Any] | None:
        protocol = self.get_protocol(protocol_id)
        if not protocol:
            return None
        for phase in protocol["phases"]:
            start, end = map(int, phase["days"].split("-"))
            if start <= day <= end:
                result = {
                    "protocol": protocol["name"],
                    "day": day,
                    "phase": phase["name"],
                    "focus": phase["focus"],
                    "eat": phase["eat"],
                    "avoid": phase["avoid"],
                    "practices": phase["practices"],
                    "expected_symptoms": phase["expected_symptoms"],
                    "supplements": phase.get("supplements_this_phase", protocol.get("supplements", [])),
                }
                if "herxheimer_management" in protocol:
                    result["herxheimer_management"] = protocol["herxheimer_management"]
                if "moon_phase_note" in protocol:
                    result["moon_phase_note"] = protocol["moon_phase_note"]
                return result
        return None

    def check_contraindications(self, protocol_id: str, profile: dict[str, Any]) -> list[str]:
        """Return contraindications that apply to this user's profile."""
        protocol = self.get_protocol(protocol_id)
        if not protocol:
            return []
        conditions = [c.lower() for c in profile.get("conditions", [])]
        medications = [m.lower() for m in profile.get("medications", [])]
        flagged = []
        for contra in protocol.get("contraindications", []):
            c_lower = contra.lower()
            if any(cond in c_lower for cond in conditions):
                flagged.append(contra)
            if any(med in c_lower for med in medications):
                flagged.append(contra)
        return flagged

    def recommend_protocol(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Recommend a protocol based on full user profile with contraindication check."""
        goals = [g.lower() for g in profile.get("health_goals", [])]
        conditions = [c.lower() for c in profile.get("conditions", [])]
        all_terms = goals + conditions

        # Priority order: specific conditions first
        if any(t in " ".join(all_terms) for t in ["mold", "mycotoxin", "cirs"]):
            pid = "mold-mycotoxin-90day"
        elif any(t in " ".join(all_terms) for t in ["parasite", "worm", "giardia", "blastocystis"]):
            pid = "parasite-21day"
        elif any(t in " ".join(all_terms) for t in ["candida", "sibo", "fungal", "yeast"]):
            pid = "candida-sibo-30day"
        elif any(t in " ".join(all_terms) for t in ["leaky gut", "ibs", "gut", "intestinal"]):
            pid = "gut-5r-60day"
        elif any(t in " ".join(all_terms) for t in ["heavy metal", "mercury", "lead", "arsenic"]):
            pid = "heavy-metal-30day"
        elif any(t in " ".join(all_terms) for t in ["liver", "alcohol", "hepat"]):
            pid = "liver-21day"
        else:
            pid = "gentle-7day"

        protocol = self.get_protocol(pid) or DETOX_PROTOCOLS[0]

        # Check contraindications
        flagged = self.check_contraindications(protocol["id"], profile)
        if flagged:
            # Fall back to gentler protocol
            protocol = self.get_protocol("gentle-7day") or DETOX_PROTOCOLS[0]

        return protocol


detox_service = DetoxService()
