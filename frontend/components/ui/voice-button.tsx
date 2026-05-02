"use client";

/**
 * VoiceButton — animated mic button that drives the useVoice state machine.
 *
 * States:
 *   idle       → grey mic icon, click to start recording
 *   recording  → red pulsing ring, click to stop and send
 *   processing → spinning ring (waiting for server)
 *   speaking   → blue wave animation, click to stop playback
 *   error      → red mic with shake, click to retry
 */

import { Mic, MicOff, Loader2, Volume2, VolumeX } from "lucide-react";
import { VoiceState } from "@/lib/use-voice";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  state: VoiceState;
  onStart: () => void;
  onStop: () => void;
  onCancel: () => void;
  onStopSpeaking: () => void;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE = {
  sm: { button: "h-10 w-10", icon: 16, ring: "h-14 w-14" },
  md: { button: "h-14 w-14", icon: 22, ring: "h-20 w-20" },
  lg: { button: "h-20 w-20", icon: 30, ring: "h-28 w-28" },
};

export function VoiceButton({
  state,
  onStart,
  onStop,
  onCancel,
  onStopSpeaking,
  disabled = false,
  size = "md",
  className,
}: VoiceButtonProps) {
  const s = SIZE[size];

  function handleClick() {
    if (disabled) return;
    if (state === "idle" || state === "error") onStart();
    else if (state === "recording") onStop();
    else if (state === "speaking") onStopSpeaking();
    // processing: no-op (wait for server)
  }

  function handleRightClick(e: React.MouseEvent) {
    e.preventDefault();
    if (state === "recording") onCancel();
  }

  const label =
    state === "idle" ? "Start voice input"
    : state === "recording" ? "Stop recording"
    : state === "processing" ? "Processing…"
    : state === "speaking" ? "Stop speaking"
    : "Retry";

  return (
    <div className={cn("relative flex items-center justify-center", className)}>
      {/* Pulse ring — recording */}
      {state === "recording" && (
        <span
          className={cn(
            "absolute rounded-full bg-red-500/20 animate-ping",
            s.ring
          )}
        />
      )}

      {/* Wave ring — speaking */}
      {state === "speaking" && (
        <span
          className={cn(
            "absolute rounded-full bg-blue-500/20 animate-pulse",
            s.ring
          )}
        />
      )}

      <button
        type="button"
        aria-label={label}
        title={label}
        disabled={disabled || state === "processing"}
        onClick={handleClick}
        onContextMenu={handleRightClick}
        className={cn(
          "relative z-10 rounded-full flex items-center justify-center",
          "transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
          s.button,
          // idle
          state === "idle" &&
            "bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white focus-visible:ring-zinc-500",
          // recording
          state === "recording" &&
            "bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-900/40 focus-visible:ring-red-500",
          // processing
          state === "processing" &&
            "bg-zinc-700 text-zinc-400 cursor-not-allowed",
          // speaking
          state === "speaking" &&
            "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/40 focus-visible:ring-blue-500",
          // error
          state === "error" &&
            "bg-red-900 hover:bg-red-800 text-red-300 animate-[shake_0.4s_ease-in-out] focus-visible:ring-red-500",
          disabled && "opacity-40 cursor-not-allowed",
        )}
      >
        {state === "processing" ? (
          <Loader2 size={s.icon} className="animate-spin" />
        ) : state === "speaking" ? (
          <Volume2 size={s.icon} />
        ) : state === "error" ? (
          <MicOff size={s.icon} />
        ) : (
          <Mic size={s.icon} />
        )}
      </button>
    </div>
  );
}

/** Compact status label shown below the button. */
export function VoiceStatusLabel({ state, error }: { state: VoiceState; error: string | null }) {
  if (state === "idle") return null;

  const text =
    state === "recording" ? "Listening… (click to send)"
    : state === "processing" ? "Thinking…"
    : state === "speaking" ? "Speaking… (click to stop)"
    : error ?? "Something went wrong — tap to retry";

  const colour =
    state === "recording" ? "text-red-400"
    : state === "processing" ? "text-zinc-400"
    : state === "speaking" ? "text-blue-400"
    : "text-red-400";

  return (
    <p className={cn("text-xs font-medium mt-2 text-center animate-pulse", colour)}>
      {text}
    </p>
  );
}
