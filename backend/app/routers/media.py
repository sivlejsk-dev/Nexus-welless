"""
Media endpoints — image generation and visual guides for Nexus Console.

GET  /media/guides              — list all visual guides
GET  /media/guides/{id}         — get a guide (with fallback images)
GET  /media/guides/{id}/dalle   — get a guide with DALL-E images per step
POST /media/generate            — generate a single image from a prompt
POST /media/query               — natural language → best media response
GET  /media/config              — capability flags
"""

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.services.media import media_service

router = APIRouter(prefix="/media", tags=["media"])


class ImageRequest(BaseModel):
    prompt: str
    topic: str = "general"
    size: str = "1024x1024"
    quality: str = "standard"
    style: str = "vivid"


class MediaQueryRequest(BaseModel):
    query: str
    media_type: str = "auto"   # "image" | "guide" | "auto"


@router.get("/config")
async def media_config():
    """Return capability flags so the frontend knows what's available."""
    return {
        "dalle_available": media_service._dalle_available,
        "guides_available": True,
        "fallback_images": True,
        "supported_sizes": ["1024x1024", "1792x1024", "1024x1792"],
        "supported_styles": ["vivid", "natural"],
        "guide_count": len(media_service.list_guides()),
    }


@router.get("/guides")
async def list_guides():
    """List all available visual guides."""
    return media_service.list_guides()


@router.get("/guides/{guide_id}")
async def get_guide(guide_id: str, dalle: bool = False):
    """
    Get a visual guide with images.
    Pass ?dalle=true to generate DALL-E images per step (requires OpenAI credits).
    """
    result = await media_service.generate_visual_guide(
        guide_id=guide_id,
        generate_images=dalle,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/generate")
async def generate_image(req: ImageRequest):
    """Generate a single image from a text prompt."""
    return await media_service.generate_image(
        prompt=req.prompt,
        topic=req.topic,
        size=req.size,
        quality=req.quality,
        style=req.style,
    )


@router.post("/query")
async def media_query(req: MediaQueryRequest):
    """
    Natural language query → best media response.
    Nexus decides whether to return an image or a visual guide.
    """
    return await media_service.query_to_media(
        query=req.query,
        media_type=req.media_type,
    )
