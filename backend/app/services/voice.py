"""
Voice service — Speech-to-Text (STT) and Text-to-Speech (TTS) for Nexus.

STT: OpenAI Whisper via the /audio/transcriptions endpoint.
TTS: OpenAI TTS via the /audio/speech endpoint.

Both use the same API key and base URL as the chat service so a single
provider credential covers the full voice pipeline.

When NEXUS_API_KEY is not configured the service falls back gracefully:
  - STT returns an empty transcript with a warning flag
  - TTS returns None so the frontend can fall back to Web Speech API

Voice-optimised chat
--------------------
voice_chat() is a convenience wrapper that:
  1. Transcribes the uploaded audio → text
  2. Sends the text through NexusService.chat()
  3. Synthesises the response text → audio bytes
  4. Returns transcript, text response, and audio in one call
"""

from __future__ import annotations

import asyncio
import io
import logging
from typing import Any

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

# TTS voice options (OpenAI-compatible): alloy, echo, fable, onyx, nova, shimmer
# Shimmer at a slightly slower pace gives Nexus the calmest default presence.
DEFAULT_VOICE = "shimmer"
DEFAULT_VOICE_SPEED = 0.88
DEFAULT_TTS_MODEL = "tts-1"
DEFAULT_STT_MODEL = "whisper-1"
# Groq uses a different model name for Whisper
GROQ_STT_MODEL = "whisper-large-v3-turbo"
# Audio format returned by TTS — mp3 is universally supported in browsers
TTS_RESPONSE_FORMAT = "mp3"


class VoiceService:
    """STT + TTS wrapper around the OpenAI-compatible Nexus API."""

    def __init__(self) -> None:
        # STT: prefer Groq Whisper (free), fall back to OpenAI Whisper
        self._groq_key = settings.groq_api_key
        self._groq_base = settings.groq_api_base_url.rstrip("/")
        # TTS: OpenAI only (Groq has no TTS)
        self._openai_key = settings.nexus_api_key
        self._openai_base = settings.nexus_api_base_url.rstrip("/")
        # STT is available if either key is set
        self._stt_configured = bool(self._groq_key or self._openai_key)
        # TTS requires OpenAI key
        self._tts_configured = bool(self._openai_key)
        # Legacy compat
        self._configured = self._stt_configured

    # ── STT ───────────────────────────────────────────────────────────────────

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language: str | None = None,
    ) -> dict[str, Any]:
        """
        Transcribe audio bytes to text using Whisper.

        Returns:
            {
                "transcript": str,
                "language": str | None,
                "duration": float | None,
                "configured": bool,   # False when API key is missing
            }
        """
        if not self._stt_configured:
            log.warning("STT not configured — no API key set")
            return {"transcript": "", "language": None, "duration": None, "configured": False}

        # Prefer Groq Whisper (fast, free tier)
        if self._groq_key:
            try:
                return await self._transcribe_with(
                    base_url=self._groq_base,
                    api_key=self._groq_key,
                    model=GROQ_STT_MODEL,
                    audio_bytes=audio_bytes,
                    filename=filename,
                    language=language,
                )
            except Exception as exc:
                log.warning("Groq STT failed, falling back to OpenAI: %s", exc)

        # Fall back to OpenAI Whisper
        if self._openai_key:
            try:
                return await self._transcribe_with(
                    base_url=self._openai_base,
                    api_key=self._openai_key,
                    model=DEFAULT_STT_MODEL,
                    audio_bytes=audio_bytes,
                    filename=filename,
                    language=language,
                )
            except Exception as exc:
                log.error("OpenAI STT failed: %s", exc)

        return {"transcript": "", "language": None, "duration": None, "configured": True}

    async def _transcribe_with(
        self,
        base_url: str,
        api_key: str,
        model: str,
        audio_bytes: bytes,
        filename: str,
        language: str | None,
    ) -> dict[str, Any]:
        mime = _mime_for(filename)
        _stt_timeout = httpx.Timeout(connect=8.0, read=30.0, write=15.0, pool=5.0)
        async with httpx.AsyncClient(timeout=_stt_timeout) as client:
            files = {"file": (filename, io.BytesIO(audio_bytes), mime)}
            data: dict[str, str] = {"model": model, "response_format": "verbose_json"}
            if language:
                data["language"] = language
            resp = await client.post(
                f"{base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data=data,
            )
            resp.raise_for_status()
            body = resp.json()
            return {
                "transcript": body.get("text", "").strip(),
                "language": body.get("language"),
                "duration": body.get("duration"),
                "configured": True,
            }

    # ── TTS ───────────────────────────────────────────────────────────────────

    async def synthesise(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        model: str = DEFAULT_TTS_MODEL,
        speed: float = 1.0,
    ) -> bytes | None:
        """
        Synthesise text to MP3 audio bytes.

        Returns None when the API key is not configured so callers can
        fall back to the browser's Web Speech API.
        """
        if not self._tts_configured:
            return None

        # Tighter timeout for TTS — 20s is plenty; 60s blocks the server
        _tts_timeout = httpx.Timeout(connect=8.0, read=20.0, write=8.0, pool=5.0)

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=_tts_timeout) as client:
                    resp = await client.post(
                        f"{self._openai_base}/audio/speech",
                        headers={
                            "Authorization": f"Bearer {self._openai_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model,
                            "input": text[:4096],
                            "voice": voice,
                            "response_format": TTS_RESPONSE_FORMAT,
                            "speed": speed,
                        },
                    )
                    if resp.status_code == 429:
                        # Rate limited — wait briefly then retry once, then give up
                        if attempt == 0:
                            await asyncio.sleep(2)
                            continue
                        log.warning("TTS rate limited after retry — skipping audio")
                        return None
                    resp.raise_for_status()
                    return resp.content
            except asyncio.TimeoutError:
                log.warning("TTS timeout on attempt %d — skipping audio", attempt + 1)
                return None
            except Exception as exc:
                log.warning("TTS synthesis failed: %s", exc)
                return None
        return None

    # ── Combined voice chat ───────────────────────────────────────────────────

    async def voice_chat(
        self,
        audio_bytes: bytes,
        filename: str,
        user_id: str,
        user_profile: dict[str, Any] | None = None,
        voice: str = DEFAULT_VOICE,
        speed: float = DEFAULT_VOICE_SPEED,
        tts_enabled: bool = True,
        db: Any | None = None,
    ) -> dict[str, Any]:
        """
        Full voice round-trip: audio → transcript → Nexus response → audio.

        Returns:
            {
                "transcript":    str,          # what the user said
                "response_text": str,          # Nexus text response
                "audio_b64":     str | None,   # base64-encoded MP3 (or None)
                "domain":        str,
                "intent":        str,
                "session_id":    str | None,
                "tts_available": bool,
            }
        """
        import base64
        from app.services.nexus import nexus_service

        # 1. Transcribe
        stt_result = await self.transcribe(audio_bytes, filename)
        transcript = stt_result["transcript"]

        if not transcript:
            return {
                "transcript": "",
                "response_text": "I didn't catch that — could you try again?",
                "audio_b64": None,
                "domain": "general",
                "intent": "unknown",
                "session_id": None,
                "tts_available": self._configured,
            }

        # 2. Chat
        chat_result = await nexus_service.chat(
            user_id=user_id,
            raw_message=transcript,
            user_profile=user_profile,
            db=db,
        )
        response_text: str = chat_result["response"]

        # 3. Synthesise (optional)
        audio_b64: str | None = None
        if tts_enabled:
            try:
                audio_bytes_out = await self.synthesise(response_text, voice=voice, speed=speed)
                if audio_bytes_out:
                    audio_b64 = base64.b64encode(audio_bytes_out).decode()
            except Exception:
                pass  # TTS failure must not break the voice chat response

        return {
            "transcript": transcript,
            "response_text": response_text,
            "audio_b64": audio_b64,
            "domain": chat_result.get("domain", "general"),
            "intent": chat_result.get("intent", "unknown"),
            "session_id": chat_result.get("session_id"),
            "tts_available": self._configured,
        }


def _mime_for(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "webm": "audio/webm",
        "mp4": "audio/mp4",
        "m4a": "audio/mp4",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }.get(ext, "audio/webm")


# Singleton
voice_service = VoiceService()
