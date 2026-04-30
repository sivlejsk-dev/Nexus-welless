"use client";

import { useEffect, useRef, useState } from "react";
import { nexus, NexusChatResponse } from "@/lib/api";
import { useVoice } from "@/lib/use-voice";
import { VoiceButton, VoiceStatusLabel } from "@/components/ui/voice-button";
import { Button } from "@/components/ui/button";
import {
  Sparkles, Send, Brain, Leaf, Star, Droplets, Mic, Settings2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const MODULES = [
  { id: "nutrition",  label: "Nutrition",  icon: Leaf     },
  { id: "meditation", label: "Meditation", icon: Brain    },
  { id: "detox",      label: "Detox",      icon: Droplets },
  { id: "astrology",  label: "Astrology",  icon: Star     },
  { id: "general",    label: "General",    icon: Sparkles },
] as const;

const VOICES = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"] as const;

interface Message {
  role: "user" | "nexus";
  content: string;
  action_items?: string[];
  via?: "text" | "voice";
}

export default function NexusPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "nexus",
      content:
        "I am Nexus — your personal wellness intelligence. Ask me anything about nutrition, meditation, detox, astrology, or your overall wellbeing. Type below or tap the microphone to speak.",
    },
  ]);
  const [input, setInput] = useState("");
  const [module, setModule] = useState("general");
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("nova");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const voice = useVoice({
    voice: selectedVoice,
    ttsEnabled,
    onTranscript: (text) =>
      setMessages((p) => [...p, { role: "user", content: text, via: "voice" }]),
    onResponse: (r) =>
      setMessages((p) => [...p, { role: "nexus", content: r.response_text, via: "voice" }]),
    onError: (err) =>
      setMessages((p) => [...p, { role: "nexus", content: `Voice error: ${err.message}` }]),
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, voice.state]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((p) => [...p, { role: "user", content: userMsg, via: "text" }]);
    setLoading(true);
    try {
      const res: NexusChatResponse = await nexus.chat(userMsg);
      setMessages((p) => [
        ...p,
        { role: "nexus", content: res.response, via: "text" },
      ]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        { role: "nexus", content: "Something went wrong — please try again." },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const voiceActive = voice.state !== "idle" && voice.state !== "error";

  return (
    /* Full-height column — accounts for mobile bottom nav (56px) and desktop sidebar */
    <div className="flex flex-col h-[calc(100dvh-56px)] md:h-[calc(100vh-2rem)] max-w-3xl mx-auto">

      {/* ── Header ── */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-none">Nexus AI</h1>
            <p className="text-white/40 text-[11px]">Wellness intelligence</p>
          </div>
        </div>
        <button
          onClick={() => setShowSettings((v) => !v)}
          className="p-2 rounded-lg text-white/30 hover:text-white/70 hover:bg-white/5 transition-colors"
          aria-label="Voice settings"
        >
          <Settings2 className="w-5 h-5" />
        </button>
      </div>

      {/* ── Voice settings panel ── */}
      {showSettings && (
        <div className="mx-4 mb-2 bg-white/5 border border-white/10 rounded-xl p-4 space-y-3 flex-shrink-0">
          <p className="text-white/50 text-xs font-semibold uppercase tracking-wider">Voice settings</p>
          <div className="flex items-center gap-5 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-white/50 text-xs">Voice</span>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="bg-white/10 border border-white/10 rounded-lg px-2 py-1 text-white text-xs focus:outline-none"
              >
                {VOICES.map((v) => (
                  <option key={v} value={v} className="bg-zinc-900">
                    {v.charAt(0).toUpperCase() + v.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <span className="text-white/50 text-xs">Speak responses</span>
              <button
                onClick={() => setTtsEnabled((v) => !v)}
                className={cn(
                  "relative w-9 h-5 rounded-full transition-colors",
                  ttsEnabled ? "bg-violet-600" : "bg-white/10"
                )}
              >
                <span className={cn(
                  "absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform",
                  ttsEnabled && "translate-x-4"
                )} />
              </button>
            </label>
          </div>
        </div>
      )}

      {/* ── Module selector ── */}
      <div className="flex gap-2 px-4 pb-2 overflow-x-auto flex-shrink-0 scrollbar-none">
        {MODULES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setModule(id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap flex-shrink-0",
              module === id ? "bg-violet-600 text-white" : "bg-white/5 text-white/50 hover:text-white"
            )}
          >
            <Icon className="w-3 h-3" />
            {label}
          </button>
        ))}
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-4 space-y-4 min-h-0">
        {messages.map((msg, i) => (
          <div key={i} className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
            {msg.role === "nexus" && (
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mr-2 mt-1">
                <Sparkles className="w-3.5 h-3.5 text-white" />
              </div>
            )}
            <div className="max-w-[85%]">
              <div className={cn(
                "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "user"
                  ? "bg-violet-600 text-white"
                  : "bg-white/5 border border-white/10 text-white/80"
              )}>
                {msg.content}
              </div>
              {msg.via === "voice" && (
                <div className={cn("flex items-center gap-1 mt-1 px-1",
                  msg.role === "user" ? "justify-end" : "justify-start")}>
                  <Mic className="w-2.5 h-2.5 text-white/20" />
                  <span className="text-white/20 text-[10px]">voice</span>
                </div>
              )}
              {msg.action_items && msg.action_items.length > 0 && (
                <div className="mt-2 space-y-1">
                  {msg.action_items.map((item, j) => (
                    <div key={j} className="flex items-start gap-2 px-1">
                      <span className="text-violet-400 text-xs mt-0.5">→</span>
                      <span className="text-white/60 text-xs">{item}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {(loading || voice.isProcessing) && (
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5 text-white animate-pulse" />
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-2" />
      </div>

      {/* ── Input area ── */}
      <div className="flex-shrink-0 px-4 pb-4 pt-2 space-y-2">

        {/* Voice status */}
        <VoiceStatusLabel state={voice.state} error={voice.error} />

        {/* Input row */}
        <div className="flex gap-2 items-center">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={
              voice.state === "recording"  ? "Listening…"   :
              voice.state === "processing" ? "Processing…"  :
              voice.state === "speaking"   ? "Speaking…"    :
              `Ask Nexus about ${module}…`
            }
            disabled={voiceActive}
            className={cn(
              "flex-1 min-w-0 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white text-sm",
              "placeholder:text-white/25 focus:outline-none focus:border-violet-500/50 transition-colors",
              voiceActive && "opacity-40 cursor-not-allowed"
            )}
          />

          {/* Send button — only show when there's text */}
          {input.trim() && !voiceActive && (
            <button
              onClick={sendMessage}
              disabled={loading}
              className="w-11 h-11 flex-shrink-0 rounded-2xl bg-violet-600 hover:bg-violet-500 active:scale-95 transition-all flex items-center justify-center disabled:opacity-50"
              aria-label="Send"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          )}

          {/* Mic button — large and always visible */}
          <VoiceButton
            state={voice.state}
            onStart={voice.startRecording}
            onStop={voice.stopRecording}
            onCancel={voice.cancelRecording}
            onStopSpeaking={voice.stopSpeaking}
            disabled={loading}
            size="md"
          />
        </div>

        {/* Hint text */}
        {voice.state === "idle" && !voice.error && (
          <p className="text-white/20 text-[11px] text-center">
            Tap the mic to speak · tap again to send
          </p>
        )}
      </div>
    </div>
  );
}
