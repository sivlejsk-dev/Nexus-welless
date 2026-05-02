"use client";

/**
 * useVoice — full voice pipeline hook for Nexus.
 *
 * Recording:  MediaRecorder API (webm/opus, falls back to audio/mp4)
 * STT:        Server-side Whisper via POST /voice/chat
 *             → falls back to browser Web Speech API if server TTS unavailable
 * TTS:        Server returns base64 MP3 → decoded and played via Web Audio API
 *             → falls back to browser SpeechSynthesis if audio_b64 is null
 *
 * State machine:
 *   idle → recording → processing → speaking → idle
 *                                 ↘ error → idle
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { voiceChat, VoiceChatResponse } from "./api";

type BrowserSpeechRecognition = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((event: { error?: string; message?: string }) => void) | null;
  onend: (() => void) | null;
};

type WindowWithSpeechRecognition = Window & typeof globalThis & {
  webkitSpeechRecognition?: new () => BrowserSpeechRecognition;
  SpeechRecognition?: new () => BrowserSpeechRecognition;
};

export type VoiceState = "idle" | "recording" | "processing" | "speaking" | "error";

export interface VoiceMessage {
  role: "user" | "assistant";
  text: string;
  timestamp: Date;
}

export interface UseVoiceOptions {
  voice?: string;           // TTS voice (nova, alloy, echo, fable, onyx, shimmer)
  ttsEnabled?: boolean;     // set false to always use browser TTS
  language?: string;        // BCP-47 hint for Whisper, e.g. "en"
  onTranscript?: (text: string) => void;
  onResponse?: (result: VoiceChatResponse) => void;
  onError?: (err: Error) => void;
  onStateChange?: (state: VoiceState) => void;
}

export interface UseVoiceReturn {
  state: VoiceState;
  messages: VoiceMessage[];
  isRecording: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  cancelRecording: () => void;
  stopSpeaking: () => void;
  clearMessages: () => void;
  error: string | null;
  browserSTTSupported: boolean;
  browserTTSSupported: boolean;
}

export function useVoice(opts: UseVoiceOptions = {}): UseVoiceReturn {
  const {
    voice = "nova",
    ttsEnabled = true,
    language,
    onTranscript,
    onResponse,
    onError,
    onStateChange,
  } = opts;

  const [state, setState] = useState<VoiceState>("idle");
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const speechSynthRef = useRef<SpeechSynthesisUtterance | null>(null);
  const recognitionRef = useRef<BrowserSpeechRecognition | null>(null);
  const browserTranscriptRef = useRef("");
  const cancelledRef = useRef(false);

  const browserSTTSupported =
    typeof window !== "undefined" && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window);
  const browserTTSSupported =
    typeof window !== "undefined" && "speechSynthesis" in window;

  // ── State helper ────────────────────────────────────────────────────────────
  const transition = useCallback(
    (next: VoiceState) => {
      setState(next);
      onStateChange?.(next);
    },
    [onStateChange]
  );

  // ── Cleanup on unmount ───────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      stopStream();
      stopAudio();
      recognitionRef.current?.abort();
    };
  }, []);

  // ── Internal helpers ─────────────────────────────────────────────────────────
  function stopStream() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }

  function stopAudio() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }

  // ── Play server MP3 (base64) ─────────────────────────────────────────────────
  function playBase64Audio(b64: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(`data:audio/mpeg;base64,${b64}`);
      audioRef.current = audio;
      audio.onended = () => resolve();
      audio.onerror = () => reject(new Error("Audio playback failed"));
      audio.play().catch(reject);
    });
  }

  // ── Browser TTS fallback ─────────────────────────────────────────────────────
  const speakWithBrowser = useCallback((text: string): Promise<void> => {
    return new Promise((resolve) => {
      if (!browserTTSSupported) {
        resolve();
        return;
      }
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 1.0;
      utt.pitch = 1.0;
      // Prefer a natural-sounding voice
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(
        (v) =>
          v.lang.startsWith("en") &&
          (v.name.includes("Natural") || v.name.includes("Neural") || v.name.includes("Samantha"))
      );
      if (preferred) utt.voice = preferred;
      utt.onend = () => resolve();
      utt.onerror = () => resolve(); // don't fail on TTS error
      speechSynthRef.current = utt;
      window.speechSynthesis.speak(utt);
    });
  }, [browserTTSSupported]);

  // ── Start recording ──────────────────────────────────────────────────────────
  const startRecording = useCallback(async () => {
    if (state !== "idle" && state !== "error") return;

    setError(null);
    cancelledRef.current = false;
    stopAudio();

    const SpeechRecognitionCtor = typeof window !== "undefined"
      ? (window as WindowWithSpeechRecognition).SpeechRecognition ?? (window as WindowWithSpeechRecognition).webkitSpeechRecognition
      : undefined;

    if (SpeechRecognitionCtor) {
      browserTranscriptRef.current = "";
      const recognition = new SpeechRecognitionCtor();
      recognitionRef.current = recognition;
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = language ?? "en-US";

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0]?.transcript ?? "")
          .join(" ")
          .trim();
        browserTranscriptRef.current = transcript;
      };

      recognition.onerror = (event) => {
        if (cancelledRef.current || event.error === "aborted") {
          transition("idle");
          return;
        }
        const msg = event.message || event.error || "Browser speech recognition failed";
        setError(msg);
        transition("error");
        onError?.(new Error(msg));
      };

      recognition.onend = async () => {
        const transcript = browserTranscriptRef.current.trim();
        recognitionRef.current = null;
        if (cancelledRef.current) {
          transition("idle");
          return;
        }
        if (!transcript) {
          transition("idle");
          return;
        }

        onTranscript?.(transcript);
        setMessages((prev) => [
          ...prev,
          { role: "user", text: transcript, timestamp: new Date() },
        ]);

        // Send transcript through the Nexus voice-chat pipeline so the caller
        // receives a response (same as the MediaRecorder path).
        transition("processing");
        try {
          // Encode the transcript as a tiny blob so the server endpoint accepts it.
          // The server will re-transcribe it via Whisper; the text is what matters.
          const enc = new TextEncoder();
          const bytes = enc.encode(transcript);
          const blob = new Blob([bytes], { type: "audio/webm" });
          const result = await voiceChat(blob, { voice, ttsEnabled, language });

          if (cancelledRef.current) { transition("idle"); return; }

          setMessages((prev) => [
            ...prev,
            { role: "assistant", text: result.response_text, timestamp: new Date() },
          ]);
          onResponse?.(result);

          transition("speaking");
          if (result.audio_b64) {
            try { await playBase64Audio(result.audio_b64); } catch {
              if (ttsEnabled) await speakWithBrowser(result.response_text);
            }
          } else if (ttsEnabled && browserTTSSupported) {
            await speakWithBrowser(result.response_text);
          }
          if (!cancelledRef.current) transition("idle");
        } catch (err) {
          const msg = err instanceof Error ? err.message : "Voice chat failed";
          if (cancelledRef.current || msg.includes("signal is aborted") || msg.includes("AbortError")) {
            transition("idle");
            return;
          }
          setError(msg);
          transition("error");
          onError?.(err instanceof Error ? err : new Error(msg));
        }
      };

      try {
        recognition.start();
        transition("recording");
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Could not start browser speech recognition";
        setError(msg);
        transition("error");
        onError?.(new Error(msg));
      }
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    } catch {
      const msg = "Microphone access denied. Please allow microphone access and try again.";
      setError(msg);
      transition("error");
      onError?.(new Error(msg));
      return;
    }

    streamRef.current = stream;
    chunksRef.current = [];

    // Pick best supported MIME type
    const mimeType = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
    ].find((m) => MediaRecorder.isTypeSupported(m)) ?? "";

    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      stopStream();
      if (cancelledRef.current) {
        transition("idle");
        return;
      }

      const blob = new Blob(chunksRef.current, {
        type: mimeType || "audio/webm",
      });
      chunksRef.current = [];

      if (blob.size < 100) {
        transition("idle");
        return;
      }

      transition("processing");

      try {
        const result = await voiceChat(blob, { voice, ttsEnabled, language });

        if (cancelledRef.current) {
          transition("idle");
          return;
        }

        // Add user message
        if (result.transcript) {
          onTranscript?.(result.transcript);
          setMessages((prev) => [
            ...prev,
            { role: "user", text: result.transcript, timestamp: new Date() },
          ]);
        }

        // Add assistant message
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: result.response_text, timestamp: new Date() },
        ]);

        onResponse?.(result);

        // Speak the response
        transition("speaking");

        if (result.audio_b64) {
          // Server TTS — play MP3
          try {
            await playBase64Audio(result.audio_b64);
          } catch {
            // Fall back to browser TTS
            if (ttsEnabled) await speakWithBrowser(result.response_text);
          }
        } else if (ttsEnabled && browserTTSSupported) {
          // Browser TTS fallback
          await speakWithBrowser(result.response_text);
        }

        if (!cancelledRef.current) transition("idle");
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Voice chat failed";
        if (cancelledRef.current || msg.includes("signal is aborted") || msg.includes("AbortError")) {
          transition("idle");
          return;
        }
        setError(msg);
        transition("error");
        onError?.(err instanceof Error ? err : new Error(msg));
      }
    };

    recorder.start(250); // collect chunks every 250 ms
    transition("recording");
  }, [state, voice, ttsEnabled, language, transition, onTranscript, onResponse, onError, browserTTSSupported, speakWithBrowser]);

  // ── Stop recording (send to server) ─────────────────────────────────────────
  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // ── Cancel recording (discard audio) ────────────────────────────────────────
  const cancelRecording = useCallback(() => {
    cancelledRef.current = true;
    recognitionRef.current?.abort();
    recognitionRef.current = null;
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    stopStream();
    stopAudio();
    transition("idle");
  }, [transition]);

  // ── Stop speaking ────────────────────────────────────────────────────────────
  const stopSpeaking = useCallback(() => {
    stopAudio();
    if (!cancelledRef.current) transition("idle");
  }, [transition]);

  const clearMessages = useCallback(() => setMessages([]), []);

  return {
    state,
    messages,
    isRecording: state === "recording",
    isProcessing: state === "processing",
    isSpeaking: state === "speaking",
    startRecording,
    stopRecording,
    cancelRecording,
    stopSpeaking,
    clearMessages,
    error,
    browserSTTSupported,
    browserTTSSupported,
  };
}
