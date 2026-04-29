"use client";

import { useEffect, useRef, useState } from "react";
import { nexus, NexusResponse } from "@/lib/api";
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
        "I am Nexus — your personal wellness intelligence. Ask me anything about nutrition, meditation, detox, astrology, or your overall wellbeing. You can type or tap the microphone to speak.",
    },
  ]);
  const [input, setInput] = useState("");
  const [module, setModule] = useState("general");
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("nova");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

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
      const res: NexusResponse = await nexus.recommend(module, {}, userMsg);
      setMessages((p) => [
        ...p,
        { role: "nexus", content: res.recommendation, action_items: res.action_items, via: "text" },
      ]);
    } catch {
      setMessages((p) => [
        ...p,
        { role: "nexus", content: "Unable to connect. Please ensure the Nexus API is configured." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const voiceActive = voice.state !== "idle" && voice.state !== "error";

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-4rem)] space-y-4">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Sparkles className="w-7 h-7 text-violet-400" /> Nexus AI
          </h1>
          <p className="text-white/40 mt-1">Your personal wellness intelligence engine.</p>
        </div>
        <button
          onClick={() => setShowSettings((v) => !v)}
          className="p-2 rounded-lg text-white/30 hover:text-white/70 hover:bg-white/5 transition-colors"
          title="Voice settings"
        >
          <Settings2 className="w-5 h-5" />
        </button>
      </div>

      {/* Voice settings */}
      {showSettings && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-3">
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

      {/* Module selector */}
      <div className="flex gap-2 flex-wrap">
        {MODULES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setModule(id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
              module === id ? "bg-violet-600 text-white" : "bg-white/5 text-white/50 hover:text-white"
            )}
          >
            <Icon className="w-3 h-3" />
            {label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 min-h-0 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
            {msg.role === "nexus" && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mr-3 mt-1">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={cn("max-w-[80%]", msg.role === "user" && "order-first")}>
              <div className={cn(
                "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "user" ? "bg-violet-600 text-white ml-auto" : "glass text-white/80"
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
                  <p className="text-white/30 text-xs px-1">Action items</p>
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
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white animate-pulse" />
            </div>
            <div className="glass rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div className="space-y-1 pb-2">
        <div className="flex gap-3 items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={
              voiceActive
                ? voice.state === "recording" ? "Listening…"
                  : voice.state === "processing" ? "Processing…"
                  : "Speaking…"
                : `Ask Nexus about ${module}…`
            }
            disabled={voiceActive}
            className={cn(
              "flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm",
              "placeholder:text-white/20 focus:outline-none focus:border-violet-500/50 transition-colors",
              voiceActive && "opacity-40 cursor-not-allowed"
            )}
          />
          <Button onClick={sendMessage} disabled={loading || !input.trim() || voiceActive}>
            <Send className="w-4 h-4" />
          </Button>
          <VoiceButton
            state={voice.state}
            onStart={voice.startRecording}
            onStop={voice.stopRecording}
            onCancel={voice.cancelRecording}
            onStopSpeaking={voice.stopSpeaking}
            disabled={loading}
          />
        </div>
        <VoiceStatusLabel state={voice.state} error={voice.error} />
        {voice.state === "idle" && !voice.error && (
          <p className="text-white/20 text-[11px] text-center">
            Tap mic to speak · Right-click to cancel
          </p>
        )}
      </div>
    </div>
  );
}
