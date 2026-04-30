"""
Media service — image generation and visual guide creation for Nexus Console.

Image pipeline:
  1. DALL-E 3 via OpenAI API (when key has credits)
  2. Unsplash-sourced wellness images as fallback (no API key needed)

Visual guides: structured step-by-step slides, each with an image prompt,
description, and action. Nexus generates the guide structure; images are
generated per step.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
from typing import Any

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

# ── Fallback image library (Unsplash — no key required) ──────────────────────
# Format: topic → list of direct image URLs (800x600, wellness-themed)
FALLBACK_IMAGES: dict[str, list[str]] = {
    "nutrition": [
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&q=80",
        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80",
    ],
    "meditation": [
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80",
        "https://images.unsplash.com/photo-1545389336-cf090694435e?w=800&q=80",
        "https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?w=800&q=80",
    ],
    "detox": [
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
        "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=800&q=80",
        "https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80",
    ],
    "herbs": [
        "https://images.unsplash.com/photo-1471193945509-9ad0617afabf?w=800&q=80",
        "https://images.unsplash.com/photo-1515023115689-589c33041d3c?w=800&q=80",
        "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
    ],
    "cooking": [
        "https://images.unsplash.com/photo-1466637574441-749b8f19452f?w=800&q=80",
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80",
        "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800&q=80",
    ],
    "fitness": [
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80",
    ],
    "sleep": [
        "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800&q=80",
        "https://images.unsplash.com/photo-1520206183501-b80df61043c2?w=800&q=80",
    ],
    "general": [
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80",
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
    ],
}

# ── Visual guide templates ────────────────────────────────────────────────────

GUIDE_TEMPLATES: dict[str, dict[str, Any]] = {
    "anti-inflammatory-protocol": {
        "title": "Anti-Inflammatory Protocol",
        "subtitle": "7-day food-as-medicine reset",
        "steps": [
            {"title": "Remove Inflammatory Triggers", "description": "Eliminate refined sugar, seed oils (canola, soybean, corn), gluten (if sensitive), dairy, and alcohol for 7 days. These are the primary drivers of NF-κB activation — the master switch of inflammation.", "action": "Clear your pantry of: vegetable oils, white sugar, processed snacks, soda", "image_topic": "nutrition", "icon": "🚫"},
            {"title": "Morning Anti-Inflammatory Tonic", "description": "Start each day with: 1 cup warm water + juice of 1 lemon + 1 tsp turmeric + pinch black pepper + 1 tsp raw honey. Curcumin in turmeric inhibits COX-2 enzymes. Black pepper increases absorption 2000%.", "action": "Prepare ingredients the night before for easy morning routine", "image_topic": "herbs", "icon": "🌅"},
            {"title": "Build Your Healing Plate", "description": "50% colorful vegetables (aim for 5 colors), 25% clean protein (wild fish, pastured eggs, legumes), 25% complex carbs (sweet potato, quinoa, brown rice). Every color = different phytonutrients.", "action": "Shop for: wild salmon, blueberries, leafy greens, sweet potato, walnuts", "image_topic": "nutrition", "icon": "🥗"},
            {"title": "Omega-3 Loading", "description": "Wild salmon 3x/week OR sardines daily. Supplement: 2-3g EPA+DHA/day. Omega-3s directly compete with omega-6 arachidonic acid for COX enzymes, reducing prostaglandin E2 (inflammatory signaling).", "action": "Take fish oil with your largest meal. Store in refrigerator to prevent oxidation.", "image_topic": "nutrition", "icon": "🐟"},
            {"title": "Gut Healing Support", "description": "Add fermented foods daily: sauerkraut, kimchi, kefir, or kombucha. These provide Lactobacillus strains that produce short-chain fatty acids (butyrate) — the primary fuel for colon cells and a potent anti-inflammatory.", "action": "Add 2 tbsp sauerkraut to lunch and dinner daily", "image_topic": "detox", "icon": "🦠"},
            {"title": "Anti-Inflammatory Spice Protocol", "description": "Cook with: turmeric + black pepper (curcumin), ginger (gingerols inhibit COX-2), rosemary (rosmarinic acid), cinnamon (cinnamaldehyde reduces NF-κB). These are pharmaceutical-grade anti-inflammatories in food form.", "action": "Make a spice blend: 2 parts turmeric, 1 part ginger, 1 part cinnamon, pinch black pepper", "image_topic": "herbs", "icon": "🌿"},
            {"title": "Evening Wind-Down & Recovery", "description": "Magnesium glycinate 400mg before bed reduces inflammatory cytokines and improves sleep quality. Poor sleep raises IL-6 and CRP by 40-60%. Sleep IS anti-inflammatory medicine.", "action": "Take magnesium 30 min before bed. Dim lights 1 hour before sleep.", "image_topic": "sleep", "icon": "🌙"},
        ],
    },
    "gut-healing-5r": {
        "title": "5R Gut Healing Protocol",
        "subtitle": "Remove → Replace → Reinoculate → Repair → Rebalance",
        "steps": [
            {"title": "R1: Remove", "description": "Eliminate: gluten, dairy, refined sugar, alcohol, NSAIDs, processed foods. These damage tight junction proteins (zonulin, claudin, occludin) causing intestinal permeability (leaky gut). Also remove pathogens: consider herbal antimicrobials if SIBO/candida suspected.", "action": "Start a 2-week elimination diet. Keep a food-symptom journal.", "image_topic": "nutrition", "icon": "🚫"},
            {"title": "R2: Replace", "description": "Replace digestive factors that may be deficient: Betaine HCl (low stomach acid is epidemic — causes bloating, GERD, poor protein digestion), digestive enzymes (lipase, protease, amylase), ox bile (if fat malabsorption). Low stomach acid allows pathogens to survive.", "action": "Take digestive enzymes with every meal for 30 days. Test for low HCl with the baking soda test.", "image_topic": "detox", "icon": "⚗️"},
            {"title": "R3: Reinoculate", "description": "Introduce beneficial bacteria: Saccharomyces boulardii first (it clears the way for bacteria), then multi-strain probiotics (Lactobacillus + Bifidobacterium, 50B+ CFU). Feed them with prebiotics: inulin, FOS, resistant starch (green banana, cooked/cooled potato).", "action": "Take S. boulardii for 2 weeks, then add probiotic. Eat 1 serving fermented food daily.", "image_topic": "detox", "icon": "🦠"},
            {"title": "R4: Repair", "description": "Heal the gut lining: L-Glutamine 5g/day (primary fuel for enterocytes), Zinc carnosine 75mg (repairs tight junctions), Collagen peptides 10g/day (provides glycine and proline for mucosal repair), Bone broth daily (glycine reduces intestinal permeability).", "action": "Morning: L-glutamine in water on empty stomach. Evening: collagen in warm broth.", "image_topic": "nutrition", "icon": "🔧"},
            {"title": "R5: Rebalance", "description": "Address root causes: chronic stress (cortisol destroys gut lining), poor sleep (gut repairs during deep sleep), movement (exercise increases microbial diversity by 40%), connection (loneliness increases gut permeability via vagal tone reduction).", "action": "Daily: 10 min meditation, 30 min walk, 7-9 hours sleep, one meaningful social connection.", "image_topic": "meditation", "icon": "⚖️"},
        ],
    },
    "plant-based-meat-mastery": {
        "title": "Plant-Based Meat Mastery",
        "subtitle": "Master the techniques that make plants taste like meat",
        "steps": [
            {"title": "The Maillard Reaction", "description": "The secret to meaty flavor is the Maillard reaction — a chemical reaction between amino acids and sugars at 280°F+ that creates hundreds of flavor compounds. This is why seared meat tastes different from boiled meat. You can achieve this with plants.", "action": "Get a cast iron skillet. Heat until smoking before adding any plant protein.", "image_topic": "cooking", "icon": "🔥"},
            {"title": "Umami Layering", "description": "Meat's satisfying depth comes from glutamates (umami). Layer multiple umami sources: tamari (fermented soy glutamates) + miso (fermented grain glutamates) + nutritional yeast (nucleotides that synergize with glutamates) + tomato paste (glutamic acid) + mushroom powder (guanylate).", "action": "Make umami paste: 2 tbsp miso + 2 tbsp tamari + 1 tbsp tomato paste + 1 tbsp nutritional yeast", "image_topic": "cooking", "icon": "🧂"},
            {"title": "Texture Engineering", "description": "Different proteins need different techniques: Jackfruit → shred + high heat caramelization. Seitan → knead to develop gluten + simmer in broth. Tempeh → steam to remove bitterness + deep marinate. Tofu → freeze/thaw for spongy texture + press dry.", "action": "This week: try freeze-thaw tofu. Freeze overnight, thaw, press, marinate 2 hours, sear.", "image_topic": "cooking", "icon": "🔨"},
            {"title": "Smoke & Char", "description": "Smoke is a powerful flavor signal that the brain associates with cooked meat. Liquid smoke contains the same phenolic compounds as actual wood smoking. Smoked paprika adds color and smoke. Charring vegetables on high heat creates similar compounds.", "action": "Add 1/2 tsp liquid smoke to every plant protein marinade. Use smoked (not sweet) paprika.", "image_topic": "cooking", "icon": "💨"},
            {"title": "The Perfect Marinade Formula", "description": "Every great plant protein marinade needs: ACID (breaks down texture, carries flavor) + FAT (carries fat-soluble flavor compounds) + SALT (draws out moisture, seasons deeply) + UMAMI (depth) + SMOKE (meat association) + TIME (minimum 2 hours, overnight is best).", "action": "Base marinade: 3 tbsp tamari + 1 tbsp olive oil + 1 tbsp balsamic + 1 tsp liquid smoke + 1 tsp smoked paprika", "image_topic": "cooking", "icon": "🧪"},
            {"title": "Protein Completion", "description": "Most plant proteins are incomplete (missing one or more essential amino acids). Combine: grains + legumes (rice + beans = complete), nuts + legumes (walnut taco meat + lentils = complete), or use complete plant proteins: quinoa, soy, hemp, buckwheat.", "action": "Always pair jackfruit or mushroom dishes with lentils, beans, or quinoa for complete protein.", "image_topic": "nutrition", "icon": "🧬"},
        ],
    },
    "morning-wellness-ritual": {
        "title": "Morning Wellness Ritual",
        "subtitle": "A science-backed morning routine for energy and clarity",
        "steps": [
            {"title": "Hydration First (0-5 min)", "description": "Before anything else: 500ml water with a pinch of sea salt and squeeze of lemon. You wake up dehydrated after 8 hours without water. Salt provides electrolytes for cellular hydration. Lemon stimulates bile production and liver detox.", "action": "Place a glass of water on your nightstand the night before.", "image_topic": "detox", "icon": "💧"},
            {"title": "Sunlight Exposure (5-15 min)", "description": "Get outside within 30 minutes of waking. Morning sunlight (even cloudy) sets your circadian rhythm, triggers cortisol awakening response (healthy morning energy), and starts the 12-16 hour melatonin timer for sleep. This single habit improves sleep quality more than any supplement.", "action": "Walk outside for 10 minutes. No sunglasses. Face toward the sky.", "image_topic": "fitness", "icon": "☀️"},
            {"title": "Movement (15-30 min)", "description": "10-20 minutes of movement before eating: walk, yoga, stretching, or light exercise. This depletes liver glycogen, making your first meal go to muscle glycogen instead of fat storage. It also raises BDNF (brain-derived neurotrophic factor) — the brain's growth hormone.", "action": "5 min stretching + 10 min walk = minimum effective dose.", "image_topic": "fitness", "icon": "🏃"},
            {"title": "Anti-Inflammatory Breakfast (30-60 min)", "description": "Break your fast with protein + healthy fat + fiber. Avoid sugar and refined carbs — they spike insulin and cortisol, creating an energy crash by 10am. Ideal: eggs + avocado + leafy greens, or smoothie with protein powder + berries + spinach + flaxseed.", "action": "Prep smoothie ingredients in freezer bags the night before for a 2-minute breakfast.", "image_topic": "nutrition", "icon": "🥗"},
            {"title": "Mindset & Intention (60-70 min)", "description": "5-10 minutes of journaling or meditation before checking your phone. The first 30 minutes of the day set the emotional tone for the next 16 hours. Checking your phone first thing puts you in reactive mode. Journaling puts you in creative/intentional mode.", "action": "Write 3 things: what you're grateful for, your top priority today, one thing you're looking forward to.", "image_topic": "meditation", "icon": "📝"},
        ],
    },
}


class MediaService:
    """Generates images and visual guides for the Nexus Console."""

    def __init__(self) -> None:
        self._openai_key = settings.nexus_api_key
        self._openai_base = settings.nexus_api_base_url.rstrip("/")
        self._dalle_available = bool(self._openai_key)

    def _fallback_image(self, topic: str, index: int = 0) -> dict[str, Any]:
        """Return a fallback image URL for a given topic."""
        images = FALLBACK_IMAGES.get(topic, FALLBACK_IMAGES["general"])
        url = images[index % len(images)]
        return {
            "url": url,
            "source": "unsplash",
            "prompt": None,
            "revised_prompt": None,
            "dalle_available": False,
        }

    async def generate_image(
        self,
        prompt: str,
        topic: str = "general",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
    ) -> dict[str, Any]:
        """Generate an image via DALL-E 3, falling back to Unsplash."""
        if not self._dalle_available:
            return self._fallback_image(topic)

        # Build a wellness-optimised prompt
        enhanced = (
            f"{prompt}. "
            "Photorealistic, high quality, wellness aesthetic, "
            "soft natural lighting, clean composition, inspiring and calming mood."
        )

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self._openai_base}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self._openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": enhanced,
                        "n": 1,
                        "size": size,
                        "quality": quality,
                        "style": style,
                        "response_format": "url",
                    },
                )
                if resp.status_code in (429, 402, 403):
                    log.warning("DALL-E unavailable (%s) — using fallback", resp.status_code)
                    return self._fallback_image(topic)
                resp.raise_for_status()
                data = resp.json()
                img = data["data"][0]
                return {
                    "url": img.get("url"),
                    "source": "dalle-3",
                    "prompt": prompt,
                    "revised_prompt": img.get("revised_prompt"),
                    "dalle_available": True,
                }
        except Exception as exc:
            log.warning("DALL-E error: %s — using fallback", exc)
            return self._fallback_image(topic)

    async def generate_visual_guide(
        self,
        guide_id: str,
        generate_images: bool = False,
    ) -> dict[str, Any]:
        """Return a structured visual guide, optionally with DALL-E images per step."""
        template = GUIDE_TEMPLATES.get(guide_id)
        if not template:
            return {"error": f"Guide '{guide_id}' not found"}

        steps = []
        for i, step in enumerate(template["steps"]):
            image_data: dict[str, Any]
            if generate_images and self._dalle_available:
                prompt = (
                    f"Wellness illustration: {step['title']}. "
                    f"{step['description'][:120]}. "
                    "Clean, inspiring, photorealistic wellness photography."
                )
                image_data = await self.generate_image(
                    prompt=prompt,
                    topic=step["image_topic"],
                    size="1024x1024",
                )
                # Rate limit: small delay between DALL-E calls
                if i < len(template["steps"]) - 1:
                    await asyncio.sleep(1)
            else:
                image_data = self._fallback_image(step["image_topic"], i)

            steps.append({
                "step_number": i + 1,
                "title": step["title"],
                "description": step["description"],
                "action": step["action"],
                "icon": step["icon"],
                "image": image_data,
            })

        return {
            "id": guide_id,
            "title": template["title"],
            "subtitle": template["subtitle"],
            "total_steps": len(steps),
            "steps": steps,
            "images_generated": generate_images and self._dalle_available,
        }

    def list_guides(self) -> list[dict[str, Any]]:
        return [
            {
                "id": gid,
                "title": t["title"],
                "subtitle": t["subtitle"],
                "step_count": len(t["steps"]),
            }
            for gid, t in GUIDE_TEMPLATES.items()
        ]

    async def query_to_media(
        self,
        query: str,
        media_type: str = "auto",
    ) -> dict[str, Any]:
        """
        Interpret a natural language query and return the best media response.

        media_type: "image" | "guide" | "auto"
        """
        q = query.lower()

        # Detect intent
        guide_keywords = ["how to", "steps", "protocol", "guide", "routine", "ritual", "plan", "process"]
        image_keywords = ["show me", "image", "picture", "visualize", "what does", "draw", "generate"]

        is_guide = any(kw in q for kw in guide_keywords) or media_type == "guide"
        is_image = any(kw in q for kw in image_keywords) or media_type == "image"

        # Match to a guide template
        guide_map = {
            "anti-inflammatory": "anti-inflammatory-protocol",
            "inflammation": "anti-inflammatory-protocol",
            "gut": "gut-healing-5r",
            "5r": "gut-healing-5r",
            "leaky gut": "gut-healing-5r",
            "plant": "plant-based-meat-mastery",
            "meat substitute": "plant-based-meat-mastery",
            "vegan": "plant-based-meat-mastery",
            "morning": "morning-wellness-ritual",
            "routine": "morning-wellness-ritual",
            "wake up": "morning-wellness-ritual",
        }

        matched_guide = next(
            (gid for kw, gid in guide_map.items() if kw in q),
            None,
        )

        if is_guide and matched_guide:
            guide = await self.generate_visual_guide(matched_guide, generate_images=False)
            return {"type": "guide", "data": guide}

        if is_guide and not matched_guide:
            # Return all guides as options
            return {"type": "guide_list", "data": self.list_guides()}

        # Default: generate an image
        topic = next(
            (t for t in FALLBACK_IMAGES if t in q),
            "general",
        )
        image = await self.generate_image(prompt=query, topic=topic)
        return {"type": "image", "data": image}


media_service = MediaService()
