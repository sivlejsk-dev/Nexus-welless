"""
Voice API endpoints — STT, TTS, and combined voice chat.

POST /voice/transcribe   — audio file → transcript text
POST /voice/synthesise   — text → MP3 audio (streaming)
POST /voice/chat         — audio → transcript → Nexus response → audio (one round-trip)
GET  /voice/config       — returns available voices and whether TTS/STT are configured
"""

import base64
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.voice import voice_service, DEFAULT_VOICE, DEFAULT_VOICE_SPEED
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/voice", tags=["voice"])

# Supported voices (OpenAI TTS)
AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
# Max upload size: 25 MB (Whisper limit)
MAX_AUDIO_BYTES = 25 * 1024 * 1024


# ── Config ────────────────────────────────────────────────────────────────────

@router.get("/config")
async def get_voice_config(current_user: User = Depends(get_current_user)):
    """Return voice capability flags and available voices."""
    return {
        "stt_available": voice_service._stt_configured,
        "tts_available": voice_service._tts_configured,
        "available_voices": AVAILABLE_VOICES,
        "default_voice": DEFAULT_VOICE,
        "default_speed": DEFAULT_VOICE_SPEED,
        "supported_formats": ["webm", "mp4", "m4a", "wav", "mp3", "ogg", "flac"],
        "max_audio_mb": MAX_AUDIO_BYTES // (1024 * 1024),
    }


# ── STT ───────────────────────────────────────────────────────────────────────

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (webm, mp4, wav, mp3, ogg, flac)"),
    language: str | None = Form(None, description="BCP-47 language code, e.g. 'en'"),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe an audio file to text using Whisper.

    Upload a recorded audio file and receive the transcript.
    Supports webm (Chrome/Firefox MediaRecorder default), mp4, wav, mp3, ogg, flac.
    """
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds 25 MB limit")
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file is too small or empty")

    result = await voice_service.transcribe(
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.webm",
        language=language,
    )
    return result


# ── TTS ───────────────────────────────────────────────────────────────────────

@router.post("/synthesise")
async def synthesise_speech(
    text: str = Form(..., description="Text to synthesise (max 4096 chars)"),
    voice: str = Form(DEFAULT_VOICE, description="Voice: alloy, echo, fable, onyx, nova, shimmer"),
    speed: float = Form(DEFAULT_VOICE_SPEED, description="Speed multiplier 0.25–4.0"),
    current_user: User = Depends(get_current_user),
):
    """
    Synthesise text to MP3 audio.

    Returns the audio as a binary MP3 stream. The frontend can play this
    directly via an Audio element or the Web Audio API.
    """
    if voice not in AVAILABLE_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice '{voice}'. Choose from: {', '.join(AVAILABLE_VOICES)}"
        )
    if not (0.25 <= speed <= 4.0):
        raise HTTPException(status_code=400, detail="Speed must be between 0.25 and 4.0")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    audio_bytes = await voice_service.synthesise(text=text, voice=voice, speed=speed)

    if audio_bytes is None:
        raise HTTPException(
            status_code=503,
            detail="TTS is not configured. Set NEXUS_API_KEY to enable speech synthesis."
        )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=nexus_response.mp3"},
    )


# ── Combined voice chat ───────────────────────────────────────────────────────

@router.post("/chat")
async def voice_chat(
    audio: UploadFile = File(..., description="Recorded audio of the user's question"),
    voice: str = Form(DEFAULT_VOICE, description="TTS voice for the response"),
    speed: float = Form(DEFAULT_VOICE_SPEED, description="TTS speed multiplier 0.25–4.0"),
    tts_enabled: bool = Form(True, description="Set false to skip TTS and get text only"),
    language: str | None = Form(None, description="BCP-47 language hint for STT"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full voice round-trip: speak → hear Nexus respond.

    1. Transcribes the uploaded audio to text (Whisper STT)
    2. Sends the transcript through the full Nexus chat pipeline
       (RAG + NutritionExpertise + reasoning + LLM)
    3. Synthesises the response to MP3 (OpenAI TTS)
    4. Returns transcript, response text, and base64-encoded MP3

    The frontend plays the audio_b64 field directly.
    When tts_enabled=false or TTS is unavailable, audio_b64 is null and
    the frontend should use the browser's Web Speech API to speak response_text.
    """
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds 25 MB limit")
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file is too small or empty")

    if voice not in AVAILABLE_VOICES:
        voice = DEFAULT_VOICE
    if not (0.25 <= speed <= 4.0):
        speed = DEFAULT_VOICE_SPEED

    # Build user profile from DB record
    profile = current_user.profile
    user_profile: dict = {}
    if profile:
        import json as _json
        user_profile = {
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
            "health_goals": _json.loads(profile.health_goals or "[]"),
            "dietary_preferences": _json.loads(profile.dietary_preferences or "[]"),
            "conditions": _json.loads(profile.conditions or "[]"),
        }

    result = await voice_service.voice_chat(
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.webm",
        user_id=str(current_user.id),
        user_profile=user_profile,
        voice=voice,
        speed=speed,
        tts_enabled=tts_enabled,
        db=db,
    )
    return result
