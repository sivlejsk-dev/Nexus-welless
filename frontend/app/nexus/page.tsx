"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { nexus, NexusChatResponse, NexusTurn } from "@/lib/api";
import { useVoice } from "@/lib/use-voice";
import { VoiceButton, VoiceStatusLabel } from "@/components/ui/voice-button";
import {
  Sparkles, Send, Brain, Leaf, Star, Droplets, Mic,
  Settings2, ChefHat, X, History, Trash2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const MODULES = [
  { id: "general",    label: "General",    icon: Sparkles, color: "text-violet-400"  },
  { id: "nutrition",  label: "Nutrition",  icon: Leaf,     color: "text-emerald-400" },
  { id: "meditation", label: "Meditation", icon: Brain,    color: "text-sky-400"     },
  { id: "detox",      label: "Detox",      icon: Droplets, color: "text-cyan-400"    },
  { id: "astrology",  label: "Astrology",  icon: Star,     color: "text-amber-400"   },
  { id: "food",       label: "Plant Food", icon: ChefHat,  color: "text-green-400"   },
] as const;

const VOICES = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"] as const;

const SUGGESTIONS = [
  "What foods reduce inflammation?",
  "Guide me through a 5-minute breathwork session",
  "What does my Aries horoscope say today?",
  "Design a 3-day gentle detox for me",
  "How do I make a plant-based burger that tastes like beef?",
];

interface Message {
  id: string;
  role: "user" | "nexus";
  content: string;
  via?: "text" | "voice" | "history";
  ts: Date;
}

function TypingDots() {
  return (
    <div className="flex gap-1 items-center py-1">
      {[0, 1, 2].map((i) => (
        <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400/60 animate-bounce"
          style={{ animationDelay: `${i * 0.18}s` }} />
      ))}
    </div>
  );
}

/** Render Nexus markdown responses with consistent styling. */
function NexusMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p:      ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
        strong: ({ children }) => <strong className="text-white/95 font-semibold">{children}</strong>,
        em:     ({ children }) => <em className="text-white/70 italic">{children}</em>,
        ul:     ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2 text-white/75">{children}</ul>,
        ol:     ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2 text-white/75">{children}</ol>,
        li:     ({ children }) => <li className="leading-relaxed">{children}</li>,
        h1:     ({ children }) => <h1 className="text-white font-bold text-base mb-2 mt-1">{children}</h1>,
        h2:     ({ children }) => <h2 className="text-white font-semibold text-sm mb-1.5 mt-1">{children}</h2>,
        h3:     ({ children }) => <h3 className="text-white/90 font-medium text-sm mb-1 mt-1">{children}</h3>,
        code:   ({ children }) => <code className="bg-white/10 rounded px-1 py-0.5 text-xs font-mono text-violet-300">{children}</code>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-violet-500/40 pl-3 my-2 text-white/60 italic">{children}</blockquote>
        ),
        hr: () => <hr className="border-white/10 my-3" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default function NexusPage() {
  const WELCOME: Message = {
    id: "welcome",
    role: "nexus",
    content: "I'm Nexus — your personal wellness intelligence. Ask me anything about nutrition, meditation, detox, astrology, or plant-based cooking. Speak or type.",
    ts: new Date(),
  };

  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [module, setModule] = useState("general");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("nova");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyHydratedRef = useRef(false);

  // ── Hydrate history from the most recent backend session on mount ──────────
  useEffect(() => {
    if (historyHydratedRef.current) return;
    historyHydratedRef.current = true;

    nexus.listSessions(1)
      .then(async ({ sessions }) => {
        if (!sessions.length) return;
        const detail = await nexus.getSession(sessions[0].session_id);
        if (!detail.turns.length) return;

        const restored: Message[] = detail.turns.map((t: NexusTurn, i: number) => ({
          id: `hist-${i}-${t.turn_index}-${t.role}`,
          role: t.role === "user" ? "user" : "nexus",
          content: t.content,
          via: "history" as const,
          ts: new Date(t.created_at),
        }));

        setMessages([
          WELCOME,
          {
            id: "history-divider",
            role: "nexus",
            content: `_Resuming your last session (${detail.total_turns} turns)…_`,
            via: "history",
            ts: new Date(),
          },
          ...restored,
        ]);
        setShowSuggestions(false);
      })
      .catch(() => { /* history unavailable — start fresh */ })
      .finally(() => setHistoryLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, historyLoading]);

  const addMsg = useCallback((msg: Omit<Message, "id" | "ts">) =>
    setMessages((p) => [...p, { ...msg, id: Math.random().toString(36).slice(2), ts: new Date() }]),
  []);

  const voice = useVoice({
    voice: selectedVoice,
    ttsEnabled,
    onTranscript: (text) => { addMsg({ role: "user", content: text, via: "voice" }); setShowSuggestions(false); },
    onResponse: (r) => addMsg({ role: "nexus", content: r.response_text, via: "voice" }),
    onError: (err) => addMsg({ role: "nexus", content: `Voice error: ${err.message}` }),
  });

  const sendMessage = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setInput("");
    setShowSuggestions(false);
    addMsg({ role: "user", content: msg, via: "text" });
    setLoading(true);
    try {
      // Pass the active module so Nexus stays contextually focused.
      const res: NexusChatResponse = await nexus.chat(msg, module === "general" ? undefined : module);
      addMsg({ role: "nexus", content: res.response, via: "text" });
    } catch {
      addMsg({ role: "nexus", content: "Something went wrong — please try again." });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearHistory = async () => {
    await nexus.clearSession().catch(() => {});
    setMessages([WELCOME]);
    setShowSuggestions(true);
    setShowHistory(false);
  };

  const voiceActive = voice.state !== "idle" && voice.state !== "error";
  const isBusy = loading || voice.isProcessing;

  return (
    <div className="flex flex-col h-[calc(100dvh-56px)] md:h-screen max-w-3xl mx-auto">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-4 pt-5 pb-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Sparkles className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-none tracking-tight">Nexus AI</h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className="pulse-dot w-1.5 h-1.5" />
              <p className="text-white/30 text-[11px]">Wellness intelligence · online</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowHistory((v) => !v)}
            className={cn("p-2 rounded-xl transition-all", showHistory ? "bg-violet-500/20 text-violet-400" : "text-white/25 hover:text-white/60 hover:bg-white/5")}
            title="Session history"
          >
            <History className="w-4 h-4" />
          </button>
          <button
            onClick={clearHistory}
            className="p-2 rounded-xl text-white/20 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowSettings((v) => !v)}
            className={cn("p-2 rounded-xl transition-all", showSettings ? "bg-violet-500/20 text-violet-400" : "text-white/25 hover:text-white/60 hover:bg-white/5")}
          >
            <Settings2 className="w-4.5 h-4.5" />
          </button>
        </div>
      </div>

      {/* ── Settings panel ──────────────────────────────────────────────── */}
      {showSettings && (
        <div className="mx-4 mb-3 glass-card p-4 flex-shrink-0 animate-scale-in">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white/50 text-xs font-semibold uppercase tracking-widest">Voice settings</p>
            <button onClick={() => setShowSettings(false)} className="text-white/25 hover:text-white/60">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-white/40 text-xs">Voice</span>
              <select value={selectedVoice} onChange={(e) => setSelectedVoice(e.target.value)}
                className="bg-white/8 border border-white/10 rounded-lg px-2.5 py-1.5 text-white/80 text-xs focus:outline-none focus:border-violet-500/40">
                {VOICES.map((v) => <option key={v} value={v} className="bg-zinc-900">{v.charAt(0).toUpperCase() + v.slice(1)}</option>)}
              </select>
            </div>
            <label className="flex items-center gap-2.5 cursor-pointer select-none">
              <span className="text-white/40 text-xs">Speak responses</span>
              <button onClick={() => setTtsEnabled((v) => !v)}
                className={cn("relative w-9 h-5 rounded-full transition-colors duration-200", ttsEnabled ? "bg-violet-600" : "bg-white/10")}>
                <span className={cn("absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200", ttsEnabled && "translate-x-4")} />
              </button>
            </label>
          </div>
        </div>
      )}

      {/* ── Module pills ─────────────────────────────────────────────────── */}
      <div className="flex gap-1.5 px-4 pb-3 overflow-x-auto flex-shrink-0 scrollbar-none">
        {MODULES.map(({ id, label, icon: Icon, color }) => (
          <button key={id} onClick={() => setModule(id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap flex-shrink-0 border",
              module === id
                ? "bg-violet-600/20 border-violet-500/40 text-violet-300"
                : "bg-white/4 border-white/6 text-white/40 hover:text-white/70 hover:bg-white/6"
            )}>
            <Icon className={cn("w-3 h-3", module === id ? color : "")} />
            {label}
          </button>
        ))}
      </div>

      {/* ── Messages ─────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 space-y-4 min-h-0 pb-2">

        {/* History loading skeleton */}
        {historyLoading && (
          <div className="space-y-3 pt-2">
            {[1, 0.8, 0.9].map((w, i) => (
              <div key={i} className={cn("skeleton h-10 rounded-2xl", i % 2 === 0 ? "mr-12" : "ml-12")}
                style={{ width: `${w * 100}%` }} />
            ))}
          </div>
        )}

        {/* Suggestion chips */}
        {!historyLoading && showSuggestions && (
          <div className="space-y-2 animate-fade-up">
            <p className="text-white/20 text-xs text-center pt-2">Try asking…</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => sendMessage(s)}
                  className="px-3 py-1.5 rounded-full text-xs bg-white/4 border border-white/8 text-white/50 hover:text-white/80 hover:bg-white/8 hover:border-violet-500/30 transition-all">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {!historyLoading && messages.map((msg) => (
          <div key={msg.id} className={cn("flex gap-2.5 animate-fade-up", msg.role === "user" ? "justify-end" : "justify-start")}>
            {msg.role === "nexus" && (
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md shadow-violet-500/20">
                <Sparkles className="w-3.5 h-3.5 text-white" />
              </div>
            )}
            <div className={cn("max-w-[85%] space-y-1", msg.role === "user" && "items-end flex flex-col")}>
              <div className={cn(
                "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "user" ? "bubble-user text-white" : "bubble-nexus text-white/80",
                msg.via === "history" && "opacity-70"
              )}>
                {msg.role === "nexus"
                  ? <NexusMarkdown content={msg.content} />
                  : msg.content
                }
              </div>
              {msg.via === "voice" && (
                <div className={cn("flex items-center gap-1 px-1", msg.role === "user" ? "justify-end" : "justify-start")}>
                  <Mic className="w-2.5 h-2.5 text-white/15" />
                  <span className="text-white/15 text-[10px]">voice</span>
                </div>
              )}
              {msg.via === "history" && msg.role === "nexus" && msg.id !== "history-divider" && (
                <span className="text-white/15 text-[10px] px-1">restored</span>
              )}
            </div>
          </div>
        ))}

        {isBusy && (
          <div className="flex gap-2.5 animate-fade-in">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="bubble-nexus rounded-2xl px-4 py-3">
              <TypingDots />
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-1" />
      </div>

      {/* ── Input bar ────────────────────────────────────────────────────── */}
      <div className="flex-shrink-0 px-4 pb-5 pt-2 space-y-2">
        <VoiceStatusLabel state={voice.state} error={voice.error} />

        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder={
                voice.state === "recording"  ? "Listening…"  :
                voice.state === "processing" ? "Processing…" :
                voice.state === "speaking"   ? "Speaking…"   :
                `Ask about ${module}…`
              }
              disabled={voiceActive}
              className={cn(
                "input-field w-full px-4 py-3 text-sm pr-12",
                voiceActive && "opacity-40 cursor-not-allowed"
              )}
            />
            {input.trim() && !voiceActive && (
              <button onClick={() => sendMessage()} disabled={isBusy}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-xl bg-violet-600 hover:bg-violet-500 flex items-center justify-center transition-all active:scale-95 disabled:opacity-40">
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            )}
          </div>

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

        {voice.state === "idle" && !voice.error && (
          <p className="text-white/15 text-[11px] text-center">Tap mic to speak · Enter to send</p>
        )}
      </div>
    </div>
  );
}
