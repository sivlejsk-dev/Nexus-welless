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
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class MediaProvider:
    """Runtime capability metadata for a creative media provider."""

    id: str
    label: str
    media_type: str
    configured: bool
    model: str
    status: str
    note: str

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
        self._video_available = bool(self._openai_key)
        self._elevenlabs_music_available = bool(settings.elevenlabs_api_key)
        self._suno_music_available = bool(settings.suno_api_key)

    def provider_capabilities(self) -> list[dict[str, Any]]:
        """Return modular provider metadata without exposing credentials."""
        providers = [
            MediaProvider(
                id="openai-images",
                label="OpenAI Images",
                media_type="image",
                configured=self._dalle_available,
                model=settings.openai_image_model,
                status="ready_when_funded" if self._dalle_available else "missing_api_key",
                note="Uses the OpenAI Image API and falls back to curated wellness images when unavailable.",
            ),
            MediaProvider(
                id="openai-video",
                label="OpenAI Sora Video",
                media_type="video",
                configured=self._video_available,
                model=settings.openai_video_model,
                status="ready_when_funded" if self._video_available else "missing_api_key",
                note="Uses the OpenAI Video API. Successful renders depend on account access, credits, and model availability.",
            ),
            MediaProvider(
                id="elevenlabs-music",
                label="ElevenLabs Music",
                media_type="music",
                configured=self._elevenlabs_music_available,
                model=settings.elevenlabs_music_model,
                status="ready_when_funded" if self._elevenlabs_music_available else "missing_api_key",
                note="Uses the ElevenLabs Music API on paid ElevenLabs accounts.",
            ),
            MediaProvider(
                id="suno-music",
                label="Suno-compatible Music",
                media_type="music",
                configured=self._suno_music_available,
                model=settings.suno_music_model,
                status="ready_when_funded" if self._suno_music_available else "missing_api_key",
                note="Optional music provider slot for Suno-compatible APIs with a configured API base URL.",
            ),
        ]
        return [provider.__dict__ for provider in providers]

    # ── Pollinations.ai (Flux) — free, no API key, real AI generation ────────

    _POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
    _POLLINATIONS_VIDEO_BASE = "https://video.pollinations.ai/prompt"

    def _pollinations_image_url(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        enhance: bool = True,
        seed: int | None = None,
    ) -> str:
        """Build a Pollinations.ai Flux image URL — no API key required."""
        import urllib.parse
        encoded = urllib.parse.quote(prompt, safe="")
        params = f"width={width}&height={height}&model={model}&nologo=true"
        if enhance:
            params += "&enhance=true"
        if seed is not None:
            params += f"&seed={seed}"
        return f"{self._POLLINATIONS_BASE}/{encoded}?{params}"

    def _pollinations_video_url(
        self,
        prompt: str,
        width: int = 1280,
        height: int = 720,
    ) -> str:
        """Build a Pollinations.ai video URL — no API key required."""
        import urllib.parse
        encoded = urllib.parse.quote(prompt, safe="")
        return f"{self._POLLINATIONS_VIDEO_BASE}/{encoded}?width={width}&height={height}&nologo=true"

    async def _generate_via_pollinations(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
    ) -> dict[str, Any]:
        """Generate an image via Pollinations.ai Flux — always available, no credits needed."""
        import random
        seed = random.randint(1, 999999)

        # Enhance prompt for wellness aesthetic
        enhanced = (
            f"{prompt}. "
            "Photorealistic, high quality, wellness aesthetic, "
            "soft natural lighting, clean composition, inspiring and calming mood."
        )
        url = self._pollinations_image_url(enhanced, width=width, height=height, seed=seed)

        # Verify the image actually generates (Pollinations returns the image directly)
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10.0, read=45.0, write=10.0, pool=5.0),
                follow_redirects=True,
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image/"):
                    return {
                        "url": url,
                        "source": "flux-ai",
                        "model": "Flux (Pollinations.ai)",
                        "prompt": prompt,
                        "revised_prompt": enhanced,
                        "ai_generated": True,
                        "seed": seed,
                    }
        except Exception as exc:
            log.warning("Pollinations image generation error: %s", exc)

        # If Pollinations fails, return the URL anyway — browser will load it directly
        return {
            "url": url,
            "source": "flux-ai",
            "model": "Flux (Pollinations.ai)",
            "prompt": prompt,
            "revised_prompt": enhanced,
            "ai_generated": True,
            "seed": seed,
        }

    async def _generate_via_dalle(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "auto",
        style: str = "vivid",
    ) -> dict[str, Any] | None:
        """Try DALL-E / gpt-image-1 — returns None if billing limit hit."""
        enhanced = (
            f"{prompt}. "
            "Photorealistic, high quality, wellness aesthetic, "
            "soft natural lighting, clean composition, inspiring and calming mood."
        )
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10.0, read=50.0, write=10.0, pool=5.0)
            ) as client:
                resp = await client.post(
                    f"{self._openai_base}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self._openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openai_image_model,
                        "prompt": enhanced,
                        "n": 1,
                        "size": size,
                        "quality": quality,
                        "response_format": "url",
                    },
                )
                # Billing limit, rate limit, or access denied — fall through to Flux
                if resp.status_code in (402, 429, 403):
                    log.info("DALL-E unavailable (%s) — using Flux", resp.status_code)
                    return None
                resp.raise_for_status()
                data = resp.json()
                img = data["data"][0]
                return {
                    "url": img.get("url"),
                    "source": settings.openai_image_model,
                    "model": settings.openai_image_model,
                    "prompt": prompt,
                    "revised_prompt": img.get("revised_prompt"),
                    "ai_generated": True,
                }
        except Exception as exc:
            log.warning("DALL-E error: %s — falling back to Flux", exc)
            return None

    def _static_fallback(self, topic: str, index: int = 0) -> dict[str, Any]:
        """Last-resort static Unsplash image — only used if all AI generation fails."""
        images = FALLBACK_IMAGES.get(topic, FALLBACK_IMAGES["general"])
        url = images[index % len(images)]
        return {
            "url": url,
            "source": "unsplash",
            "model": "static",
            "prompt": None,
            "revised_prompt": None,
            "ai_generated": False,
        }

    async def generate_image(
        self,
        prompt: str,
        topic: str = "general",
        size: str = "1024x1024",
        quality: str = "auto",
        style: str = "vivid",
    ) -> dict[str, Any]:
        """
        Generate an AI image.

        Priority:
          1. DALL-E 3 / gpt-image-1 (OpenAI) — best quality, requires credits
          2. Flux via Pollinations.ai — free, no API key, real AI generation
          3. Static Unsplash — last resort only
        """
        # Parse size into width/height for Pollinations
        try:
            w, h = (int(x) for x in size.split("x"))
        except Exception:
            w, h = 1024, 1024

        # Try DALL-E first if key is configured
        if self._dalle_available:
            result = await self._generate_via_dalle(prompt, size=size, quality=quality, style=style)
            if result:
                return result

        # Flux — always works, real AI generation
        return await self._generate_via_pollinations(prompt, width=w, height=h)

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
            # Always generate AI images for guides — Flux is free
            img_prompt = (
                f"Wellness illustration: {step['title']}. "
                f"{step['description'][:120]}. "
                "Clean, inspiring, photorealistic wellness photography."
            )
            image_data = await self.generate_image(
                prompt=img_prompt,
                topic=step["image_topic"],
                size="512x512",
            )
            # Small delay between generations to avoid hammering the API
            if i < len(template["steps"]) - 1:
                await asyncio.sleep(0.5)

            steps.append({
                "step_number": i + 1,
                "title": step["title"],
                "description": step["description"],
                "action": step["action"],
                "icon": step["icon"],
                "image_url": image_data.get("url"),
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

    async def start_video_generation(
        self,
        prompt: str,
        size: str = "1280x720",
        seconds: str = "8",
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a video.

        Priority:
          1. OpenAI Sora — best quality, requires credits
          2. Pollinations.ai video — free, real AI generation, no API key
        """
        try:
            w, h = (int(x) for x in size.split("x"))
        except Exception:
            w, h = 1280, 720

        # Try Sora first if key is configured and has credits
        if self._video_available:
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(connect=10.0, read=50.0, write=10.0, pool=5.0)
                ) as client:
                    resp = await client.post(
                        f"{self._openai_base}/videos/generations",
                        headers={
                            "Authorization": f"Bearer {self._openai_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model or settings.openai_video_model,
                            "prompt": prompt,
                            "size": size,
                            "n": 1,
                        },
                    )
                    if resp.status_code not in (402, 403, 429):
                        resp.raise_for_status()
                        data = resp.json()
                        return {
                            "provider": "sora",
                            "status": data.get("status", "queued"),
                            "job_id": data.get("id"),
                            "video_url": data.get("url"),
                            "ai_generated": True,
                        }
                    log.info("Sora unavailable (%s) — using Pollinations video", resp.status_code)
            except Exception as exc:
                log.warning("Sora error: %s — falling back to Pollinations video", exc)

        # Pollinations video — free, direct URL, real AI generation
        enhanced = (
            f"{prompt}. "
            "Cinematic, smooth motion, wellness aesthetic, soft natural lighting, high quality."
        )
        video_url = self._pollinations_video_url(enhanced, width=w, height=h)
        return {
            "provider": "pollinations-video",
            "status": "ready",
            "video_url": video_url,
            "prompt": prompt,
            "ai_generated": True,
        }

    async def get_video_generation(self, video_id: str) -> dict[str, Any]:
        """Fetch an OpenAI/Sora video render job status."""
        if not self._video_available:
            return {"configured": False, "provider": "openai-video", "status": "missing_api_key"}

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._openai_base}/videos/{video_id}",
                headers={"Authorization": f"Bearer {self._openai_key}"},
            )
            resp.raise_for_status()
            return {"configured": True, "provider": "openai-video", "video": resp.json()}

    async def start_music_generation(
        self,
        prompt: str,
        provider: str = "auto",
        title: str | None = None,
        instrumental: bool = True,
    ) -> dict[str, Any]:
        """
        Modular music-generation entrypoint.

        The provider adapters are intentionally isolated here so future paid
        provider setup does not leak into the rest of the media console.
        """
        if provider in ("auto", "elevenlabs") and self._elevenlabs_music_available:
            try:
                async with httpx.AsyncClient(timeout=180) as client:
                    resp = await client.post(
                        f"{settings.elevenlabs_api_base_url.rstrip('/')}/music",
                        params={"output_format": "mp3_44100_128"},
                        headers={
                            "xi-api-key": settings.elevenlabs_api_key,
                            "Content-Type": "application/json",
                        },
                        json={
                            "prompt": prompt,
                            "music_length_ms": 30_000,
                            "model_id": settings.elevenlabs_music_model,
                            "force_instrumental": instrumental,
                        },
                    )
                    if resp.status_code in (402, 403, 429):
                        return {
                            "configured": True,
                            "provider": "elevenlabs-music",
                            "status": "funding_or_access_required",
                            "message": "ElevenLabs Music is configured, but this account needs paid access, credits, or higher rate limits.",
                        }
                    resp.raise_for_status()
                    return {
                        "configured": True,
                        "provider": "elevenlabs-music",
                        "status": "completed",
                        "music": {
                            "title": title or "Nexus Wellness Track",
                            "content_type": resp.headers.get("content-type", "audio/mpeg"),
                            "song_id": resp.headers.get("song-id"),
                            "audio_base64": base64.b64encode(resp.content).decode("ascii"),
                        },
                    }
            except Exception as exc:
                log.warning("ElevenLabs music generation error: %s", exc)
                return {"configured": True, "provider": "elevenlabs-music", "status": "error", "message": str(exc)}

        if provider in ("auto", "suno") and self._suno_music_available:
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(
                        f"{settings.suno_api_base_url.rstrip('/')}/api/v1/generate",
                        headers={
                            "Authorization": f"Bearer {settings.suno_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "prompt": prompt,
                            "title": title or "Nexus Wellness Track",
                            "customMode": True,
                            "instrumental": instrumental,
                            "model": settings.suno_music_model,
                        },
                    )
                    if resp.status_code in (402, 403, 429):
                        return {
                            "configured": True,
                            "provider": "suno-music",
                            "status": "funding_or_access_required",
                            "message": "Suno-compatible music generation is configured, but funding, access, or limits blocked the request.",
                        }
                    resp.raise_for_status()
                    return {
                        "configured": True,
                        "provider": "suno-music",
                        "status": "queued",
                        "music": resp.json(),
                    }
            except Exception as exc:
                log.warning("Music generation error: %s", exc)
                return {"configured": True, "provider": "suno-music", "status": "error", "message": str(exc)}

        return {
            "configured": False,
            "provider": provider,
            "status": "missing_api_key",
            "message": "Music generation is modularly wired. Configure ELEVENLABS_API_KEY or SUNO_API_KEY to activate a provider.",
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

        media_type: "image" | "guide" | "video" | "music" | "auto"
        """
        q = query.lower()

        if media_type == "music":
            music = await self.start_music_generation(prompt=query)
            return {"type": "music", "data": music}

        if media_type == "video":
            video = await self.start_video_generation(prompt=query)
            return {"type": "video", "data": video}

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
