"""
Meat Substitute Knowledge Module — plant-based alternatives that satisfy meat cravings.

Covers: texture techniques, protein sources, recipes, cooking methods, and
nutritional equivalence for every major meat category.
"""

from typing import Any

# ── Protein base ingredients ──────────────────────────────────────────────────

PROTEIN_BASES: list[dict[str, Any]] = [
    {
        "id": "jackfruit",
        "name": "Young Green Jackfruit",
        "protein_per_100g": 1.7,
        "texture": "fibrous, pulls apart like pulled pork",
        "best_for": ["pulled pork", "carnitas", "BBQ", "tacos"],
        "prep": "Drain canned jackfruit, shred with forks, season heavily, cook until caramelized edges form.",
        "flavor_profile": "neutral — absorbs marinades completely",
        "nutrition_notes": "Low protein but high fiber; pair with legumes for complete amino acid profile.",
        "craving_it_satisfies": "pulled pork, BBQ brisket, carnitas",
    },
    {
        "id": "tempeh",
        "name": "Tempeh",
        "protein_per_100g": 19,
        "texture": "firm, chewy, slightly nutty — slices like chicken breast",
        "best_for": ["bacon strips", "steak slices", "stir-fry", "sandwiches"],
        "prep": "Steam 10 min to remove bitterness. Marinate 2+ hours. Pan-fry until golden crust forms.",
        "flavor_profile": "earthy, nutty — takes on smoky/savory marinades beautifully",
        "nutrition_notes": "Complete protein. Fermented — supports gut microbiome. High in B vitamins.",
        "craving_it_satisfies": "bacon, chicken strips, steak bites",
    },
    {
        "id": "seitan",
        "name": "Seitan (Wheat Gluten)",
        "protein_per_100g": 25,
        "texture": "dense, chewy, meaty — closest to chicken/beef texture",
        "best_for": ["steak", "chicken wings", "gyros", "roasts", "deli slices"],
        "prep": "Knead vital wheat gluten with broth and spices. Simmer in seasoned broth 45 min. Pan-sear for crust.",
        "flavor_profile": "savory, umami — takes on any seasoning",
        "nutrition_notes": "Highest plant protein. Not suitable for gluten intolerance. Low fat, high iron.",
        "craving_it_satisfies": "steak, chicken, deli meat, roast beef",
    },
    {
        "id": "lentils",
        "name": "Black/Green Lentils",
        "protein_per_100g": 9,
        "texture": "hearty, earthy — works as ground meat base",
        "best_for": ["bolognese", "tacos", "meat sauce", "shepherd's pie", "meatballs"],
        "prep": "Cook until just tender (not mushy). Season with smoked paprika, cumin, tamari for depth.",
        "flavor_profile": "earthy, hearty — absorbs spices well",
        "nutrition_notes": "High fiber, folate, iron. Pair with vitamin C to boost iron absorption.",
        "craving_it_satisfies": "ground beef, meat sauce, taco meat",
    },
    {
        "id": "mushrooms",
        "name": "Portobello / King Oyster Mushrooms",
        "protein_per_100g": 3.1,
        "texture": "meaty, umami-rich — portobello mimics burger patty",
        "best_for": ["burgers", "steaks", "pulled meat", "scallops (king oyster)", "bacon"],
        "prep": "Marinate in tamari + liquid smoke + garlic. Grill or roast at high heat for caramelization.",
        "flavor_profile": "deep umami, earthy, savory",
        "nutrition_notes": "Rich in ergothioneine (antioxidant), B vitamins, selenium. Low calorie.",
        "craving_it_satisfies": "burger patty, steak, scallops",
    },
    {
        "id": "chickpeas",
        "name": "Chickpeas",
        "protein_per_100g": 8.9,
        "texture": "firm when roasted, creamy when mashed",
        "best_for": ["tuna salad", "chicken salad", "nuggets", "meatballs", "shawarma"],
        "prep": "Roast at 425°F until crispy for nuggets. Mash with nori + celery for tuna substitute.",
        "flavor_profile": "mild, nutty — extremely versatile",
        "nutrition_notes": "High fiber, folate, manganese. Resistant starch feeds beneficial gut bacteria.",
        "craving_it_satisfies": "tuna, chicken salad, nuggets",
    },
    {
        "id": "cauliflower",
        "name": "Cauliflower",
        "protein_per_100g": 1.9,
        "texture": "dense florets mimic chicken wings/steaks when roasted",
        "best_for": ["buffalo wings", "steaks", "fried chicken", "fish tacos"],
        "prep": "Cut into thick steaks or florets. Batter with seasoned flour + plant milk. Bake or air-fry.",
        "flavor_profile": "mild, absorbs sauces completely",
        "nutrition_notes": "High in sulforaphane (anti-cancer), vitamin C, choline. Very low calorie.",
        "craving_it_satisfies": "chicken wings, fried chicken, fish",
    },
    {
        "id": "black-beans",
        "name": "Black Beans",
        "protein_per_100g": 8.9,
        "texture": "dense, hearty — excellent burger base",
        "best_for": ["burgers", "meatballs", "taco filling", "chili"],
        "prep": "Drain, partially mash, mix with oats + flax egg + spices. Form patties, chill 30 min, pan-fry.",
        "flavor_profile": "earthy, slightly sweet — pairs with smoky spices",
        "nutrition_notes": "Anthocyanins (anti-inflammatory), high fiber, folate, iron.",
        "craving_it_satisfies": "burger patty, ground beef",
    },
    {
        "id": "tofu",
        "name": "Extra-Firm Tofu",
        "protein_per_100g": 17,
        "texture": "varies by prep — can mimic scrambled eggs, chicken, fish",
        "best_for": ["scrambled eggs", "fish fillets", "chicken cubes", "ricotta"],
        "prep": "Press 30 min to remove water. Freeze/thaw for chewier texture. Marinate deeply.",
        "flavor_profile": "neutral — completely takes on marinade flavor",
        "nutrition_notes": "Complete protein, calcium, isoflavones. Freeze-thaw creates spongy texture that absorbs more marinade.",
        "craving_it_satisfies": "scrambled eggs, chicken, fish fillets",
    },
    {
        "id": "walnuts",
        "name": "Raw Walnuts",
        "protein_per_100g": 15,
        "texture": "pulsed in food processor = perfect ground meat texture",
        "best_for": ["taco meat", "bolognese", "meat sauce", "stuffed peppers"],
        "prep": "Pulse in food processor until crumbly. Season with cumin, chili, tamari, smoked paprika.",
        "flavor_profile": "rich, slightly bitter — takes on spices well",
        "nutrition_notes": "Highest ALA omega-3 of any nut. Anti-inflammatory. Supports brain health.",
        "craving_it_satisfies": "ground beef, taco meat",
    },
    {
        "id": "banana-blossom",
        "name": "Banana Blossom",
        "protein_per_100g": 1.6,
        "texture": "flaky, fibrous — closest plant texture to fish/crab",
        "best_for": ["fish and chips", "crab cakes", "fish tacos", "seafood salad"],
        "prep": "Drain canned blossom. Marinate in nori + lemon + old bay. Batter and fry.",
        "flavor_profile": "mild, slightly floral — takes on seafood seasonings",
        "nutrition_notes": "High in fiber, potassium, iron. Anti-inflammatory compounds.",
        "craving_it_satisfies": "fish, crab, seafood",
    },
    {
        "id": "eggplant",
        "name": "Eggplant / Aubergine",
        "protein_per_100g": 1.0,
        "texture": "dense, meaty when roasted — absorbs fat and flavor",
        "best_for": ["meatballs", "steak", "bacon", "gyros", "moussaka"],
        "prep": "Salt and press to remove moisture. Roast at high heat or grill for smoky char.",
        "flavor_profile": "rich, slightly bitter, smoky when charred",
        "nutrition_notes": "Nasunin (anthocyanin) protects brain cell membranes. Low calorie, high fiber.",
        "craving_it_satisfies": "steak, meatballs, gyro meat",
    },
]


# ── Recipes ───────────────────────────────────────────────────────────────────

RECIPES: list[dict] = [
    {
        "id": "jackfruit-pulled-pork",
        "name": "BBQ Pulled Jackfruit",
        "satisfies_craving": "pulled pork / BBQ",
        "base_ingredient": "jackfruit",
        "prep_time_min": 10, "cook_time_min": 30, "servings": 4, "difficulty": "easy",
        "ingredients": ["2 cans young green jackfruit (brine, not syrup)", "1 cup BBQ sauce", "1 tbsp smoked paprika", "1 tsp garlic powder", "1 tsp onion powder", "1 tbsp apple cider vinegar", "1 tbsp olive oil"],
        "instructions": ["Drain and rinse jackfruit. Pat dry. Shred with two forks.", "Heat oil in skillet over medium-high. Cook jackfruit 5 min without stirring to develop crust.", "Add paprika, garlic powder, onion powder. Cook 2 min.", "Add BBQ sauce and vinegar. Simmer 20 min until caramelized.", "Serve on buns with coleslaw or in tacos with avocado."],
        "pro_tips": ["High heat at the start is essential — you want caramelized edges.", "Add 1 tsp liquid smoke for deeper BBQ flavor.", "Leftovers improve overnight."],
        "nutrition_per_serving": {"calories": 180, "protein_g": 3, "fiber_g": 5, "fat_g": 4},
        "upgrade": "Add 1 cup cooked lentils to boost protein to 12g per serving.",
    },
    {
        "id": "walnut-taco-meat",
        "name": "Walnut & Lentil Taco Meat",
        "satisfies_craving": "ground beef tacos",
        "base_ingredient": "walnuts",
        "prep_time_min": 5, "cook_time_min": 15, "servings": 4, "difficulty": "easy",
        "ingredients": ["1 cup raw walnuts", "1 cup cooked black lentils", "2 tbsp tamari", "1 tbsp cumin", "1 tbsp chili powder", "1 tsp smoked paprika", "1 tsp garlic powder", "Juice of 1 lime"],
        "instructions": ["Pulse walnuts in food processor 8-10 times until crumbly.", "Toast walnut crumble in skillet 3 min.", "Add lentils and all spices. Cook 8-10 min until dry and fragrant.", "Finish with lime juice.", "Serve in tacos with avocado, salsa, cilantro."],
        "pro_tips": ["Don't over-process — you want texture, not paste.", "Lentils add protein and meatier bite.", "Freezes perfectly."],
        "nutrition_per_serving": {"calories": 280, "protein_g": 14, "fiber_g": 8, "fat_g": 18},
        "upgrade": "Add 1 tbsp nutritional yeast for cheesy umami depth.",
    },
    {
        "id": "cauliflower-buffalo-wings",
        "name": "Crispy Buffalo Cauliflower Wings",
        "satisfies_craving": "chicken wings",
        "base_ingredient": "cauliflower",
        "prep_time_min": 15, "cook_time_min": 35, "servings": 4, "difficulty": "medium",
        "ingredients": ["1 large head cauliflower, cut into florets", "1 cup flour (or chickpea flour)", "1 cup plant milk", "1 tsp garlic powder", "1 tsp onion powder", "1/2 tsp salt", "1/2 cup hot sauce", "2 tbsp vegan butter melted", "1 tbsp apple cider vinegar"],
        "instructions": ["Preheat oven to 450°F. Whisk flour, milk, spices into batter.", "Dip florets in batter, place on lined baking sheet.", "Bake 25 min until golden.", "Toss in hot sauce + butter + vinegar. Return to oven 10 min.", "Serve with vegan ranch."],
        "pro_tips": ["450°F is non-negotiable — lower temp = soggy.", "Chickpea flour batter is crispier.", "Air fryer: 400°F for 18 min, flip halfway."],
        "nutrition_per_serving": {"calories": 220, "protein_g": 7, "fiber_g": 5, "fat_g": 6},
        "upgrade": "Double-bake: plain first, sauce, then bake again for maximum crispiness.",
    },
    {
        "id": "seitan-steak",
        "name": "Pan-Seared Seitan Steak",
        "satisfies_craving": "beef steak",
        "base_ingredient": "seitan",
        "prep_time_min": 20, "cook_time_min": 50, "servings": 2, "difficulty": "advanced",
        "ingredients": ["1 cup vital wheat gluten", "2 tbsp nutritional yeast", "1 tsp garlic powder", "1 tsp smoked paprika", "3/4 cup vegetable broth", "2 tbsp tamari", "1 tbsp tomato paste", "4 cups broth for simmering", "2 tbsp olive oil", "Vegan garlic butter for basting"],
        "instructions": ["Mix dry ingredients. Whisk wet ingredients. Combine into dough.", "Knead 3 min until elastic. Shape into 2 steaks.", "Simmer in seasoned broth 45 min, turning halfway. Cool in broth.", "Pat dry. Heat cast iron until smoking. Sear 3-4 min per side.", "Baste with garlic butter last minute. Rest 5 min before slicing."],
        "pro_tips": ["Knead enough to develop gluten — this creates meaty texture.", "Simmer, don't boil — boiling makes seitan spongy.", "Cast iron is essential for the crust."],
        "nutrition_per_serving": {"calories": 320, "protein_g": 42, "fiber_g": 2, "fat_g": 8},
        "upgrade": "Marinate overnight in red wine + herbs before searing.",
    },
    {
        "id": "tempeh-bacon",
        "name": "Smoky Tempeh Bacon",
        "satisfies_craving": "bacon",
        "base_ingredient": "tempeh",
        "prep_time_min": 10, "cook_time_min": 15, "servings": 4, "difficulty": "easy",
        "ingredients": ["1 block tempeh", "3 tbsp tamari", "2 tbsp maple syrup", "1 tbsp liquid smoke", "1 tsp smoked paprika", "1 tsp garlic powder", "1 tbsp apple cider vinegar", "1 tbsp olive oil"],
        "instructions": ["Slice tempeh into thin strips (3-4mm).", "Whisk marinade ingredients. Marinate strips 30+ min.", "Heat oil in skillet over medium-high.", "Cook strips 2-3 min per side until caramelized.", "Serve immediately."],
        "pro_tips": ["Liquid smoke is non-negotiable for bacon flavor.", "Thinner slices = crispier bacon.", "Steam tempeh 10 min first to remove bitterness."],
        "nutrition_per_serving": {"calories": 160, "protein_g": 12, "fiber_g": 3, "fat_g": 7},
        "upgrade": "Add 1 tsp miso paste to marinade for extra depth.",
    },
    {
        "id": "mushroom-burger",
        "name": "Portobello Mushroom Burger",
        "satisfies_craving": "beef burger",
        "base_ingredient": "mushrooms",
        "prep_time_min": 10, "cook_time_min": 15, "servings": 2, "difficulty": "easy",
        "ingredients": ["2 large portobello caps", "3 tbsp balsamic vinegar", "2 tbsp tamari", "1 tbsp olive oil", "2 cloves garlic minced", "1 tsp thyme", "Avocado, caramelized onions, lettuce, tomato"],
        "instructions": ["Score caps in crosshatch. Marinate 20 min.", "Grill or pan-sear 5-6 min per side.", "Toast buns. Build with toppings."],
        "pro_tips": ["Scoring helps marinade penetrate.", "Don't skip caramelized onions.", "High heat gives better flavor."],
        "nutrition_per_serving": {"calories": 180, "protein_g": 6, "fiber_g": 4, "fat_g": 8},
        "upgrade": "Add a black bean patty underneath for a protein-packed double stack.",
    },
    {
        "id": "chickpea-tuna-salad",
        "name": "Chickpea 'Tuna' Salad",
        "satisfies_craving": "tuna salad",
        "base_ingredient": "chickpeas",
        "prep_time_min": 10, "cook_time_min": 0, "servings": 3, "difficulty": "easy",
        "ingredients": ["1 can chickpeas drained", "2 sheets nori crumbled", "3 tbsp vegan mayo", "1 tbsp Dijon mustard", "2 stalks celery diced", "2 tbsp red onion minced", "1 tbsp capers", "1 tbsp lemon juice", "1 tsp kelp powder", "Salt, pepper, dill"],
        "instructions": ["Roughly mash chickpeas — leave chunks.", "Mix in all remaining ingredients.", "Chill 30 min.", "Serve on toast, in wraps, or over greens."],
        "pro_tips": ["Nori + kelp powder = ocean flavor.", "Don't over-mash — chunky texture is key.", "Keeps 4 days refrigerated."],
        "nutrition_per_serving": {"calories": 220, "protein_g": 10, "fiber_g": 7, "fat_g": 9},
        "upgrade": "Add 1 tbsp white miso for extra umami depth.",
    },
    {
        "id": "banana-blossom-fish",
        "name": "Banana Blossom Fish & Chips",
        "satisfies_craving": "fish and chips",
        "base_ingredient": "banana-blossom",
        "prep_time_min": 20, "cook_time_min": 20, "servings": 2, "difficulty": "medium",
        "ingredients": ["1 can banana blossom drained", "2 sheets nori crumbled", "1 tbsp lemon juice", "1 tsp old bay seasoning", "1 tsp kelp powder", "Batter: 1 cup flour, 1 cup cold sparkling water, 1/2 tsp salt, 1/2 tsp turmeric", "Oil for frying"],
        "instructions": ["Marinate banana blossom in nori, lemon, old bay, kelp 30 min.", "Make batter with cold sparkling water.", "Heat oil to 375°F. Dip blossom in batter, fry 3-4 min.", "Drain, season immediately. Serve with tartar sauce."],
        "pro_tips": ["Cold sparkling water makes batter extra crispy.", "Kelp powder adds authentic ocean flavor.", "Don't overcrowd the fryer."],
        "nutrition_per_serving": {"calories": 290, "protein_g": 5, "fiber_g": 6, "fat_g": 10},
        "upgrade": "Add 1 tbsp white miso to the marinade.",
    },
]

# ── Texture techniques ────────────────────────────────────────────────────────

TEXTURE_TECHNIQUES: list[dict] = [
    {
        "technique": "High-Heat Searing",
        "purpose": "Creates Maillard reaction crust — the brown caramelized exterior that makes meat taste 'meaty'",
        "applies_to": ["seitan", "tempeh", "tofu", "mushrooms", "jackfruit"],
        "how": "Cast iron or stainless pan. Heat until smoking. Pat ingredient DRY. Don't move for 3-4 min.",
        "why_it_works": "Maillard reaction at 280°F+ creates hundreds of flavor compounds identical to seared meat.",
    },
    {
        "technique": "Freeze-Thaw Tofu",
        "purpose": "Creates spongy, chewy texture that absorbs marinades like a sponge",
        "applies_to": ["tofu"],
        "how": "Freeze block overnight. Thaw completely. Press out water. Ice crystals create air pockets.",
        "why_it_works": "Ice crystals rupture cell walls, creating a porous structure that soaks up 3x more marinade.",
    },
    {
        "technique": "Liquid Smoke + Smoked Paprika",
        "purpose": "Replicates the smoky flavor of grilled/smoked meat",
        "applies_to": ["all plant proteins"],
        "how": "Add 1/2-1 tsp liquid smoke to any marinade. Use smoked (not sweet) paprika.",
        "why_it_works": "Liquid smoke contains the same phenolic compounds produced by actual wood smoking.",
    },
    {
        "technique": "Umami Layering",
        "purpose": "Builds the savory depth that makes meat satisfying",
        "applies_to": ["all plant proteins"],
        "how": "Combine 2-3 umami sources: tamari + miso + nutritional yeast + tomato paste + mushroom powder.",
        "why_it_works": "Glutamates from multiple sources create synergistic umami — more satisfying than any single source.",
    },
    {
        "technique": "Resting After Cooking",
        "purpose": "Allows juices to redistribute — same as resting meat",
        "applies_to": ["seitan", "tempeh", "thick tofu"],
        "how": "Remove from heat. Rest 5 min before cutting.",
        "why_it_works": "Cutting immediately releases all moisture. Resting retains it.",
    },
]

# ── Nutritional comparison ────────────────────────────────────────────────────

NUTRITIONAL_COMPARISON: dict = {
    "ground_beef_vs_walnut_lentil": {
        "meat": {"name": "Ground beef 80/20", "protein_g": 26, "fat_g": 20, "fiber_g": 0, "calories": 287},
        "substitute": {"name": "Walnut + lentil mix", "protein_g": 18, "fat_g": 14, "fiber_g": 9, "calories": 240},
        "advantages": ["9g fiber vs 0g", "Anti-inflammatory omega-3s", "No saturated fat", "Prebiotic fiber"],
    },
    "chicken_breast_vs_seitan": {
        "meat": {"name": "Chicken breast", "protein_g": 31, "fat_g": 3.6, "fiber_g": 0, "calories": 165},
        "substitute": {"name": "Seitan", "protein_g": 25, "fat_g": 1.9, "fiber_g": 1.2, "calories": 120},
        "advantages": ["Lower calories", "No cholesterol", "Lower fat", "Iron from wheat gluten"],
    },
    "bacon_vs_tempeh_bacon": {
        "meat": {"name": "Pork bacon (3 strips)", "protein_g": 9, "fat_g": 13, "fiber_g": 0, "calories": 161},
        "substitute": {"name": "Tempeh bacon (3 strips)", "protein_g": 11, "fat_g": 6, "fiber_g": 2, "calories": 120},
        "advantages": ["More protein", "Less fat", "Fermented — probiotic benefits", "No nitrates"],
    },
}


class MeatSubstituteService:
    def get_all_bases(self) -> list[dict]:
        return PROTEIN_BASES

    def get_base(self, base_id: str) -> dict | None:
        return next((b for b in PROTEIN_BASES if b["id"] == base_id), None)

    def get_all_recipes(self) -> list[dict]:
        return RECIPES

    def get_recipe(self, recipe_id: str) -> dict | None:
        return next((r for r in RECIPES if r["id"] == recipe_id), None)

    def find_by_craving(self, craving: str) -> dict:
        q = craving.lower()
        return {
            "recipes": [r for r in RECIPES if q in r["satisfies_craving"].lower() or q in r["name"].lower()],
            "bases": [b for b in PROTEIN_BASES if q in b["craving_it_satisfies"].lower() or any(q in bf.lower() for bf in b["best_for"])],
        }

    def get_techniques(self) -> list[dict]:
        return TEXTURE_TECHNIQUES

    def get_nutritional_comparison(self) -> dict:
        return NUTRITIONAL_COMPARISON

    def get_substitutes_for_meat(self, meat_type: str) -> list[dict]:
        q = meat_type.lower()
        return [b for b in PROTEIN_BASES if q in b["craving_it_satisfies"].lower() or any(q in bf.lower() for bf in b["best_for"])]


meat_substitute_service = MeatSubstituteService()
