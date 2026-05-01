"use client";

import { useEffect, useRef, useState } from "react";
import {
  mediaApi, nexus,
  MediaImage, MediaGuide, MediaGuideInfo,
  MediaQueryResult, NexusChatResponse,
} from "@/lib/api";
import { useVoice } from "@/lib/use-voice";
import { VoiceButton, VoiceStatusLabel } from "@/components/ui/voice-button";
import { cn } from "@/lib/utils";
import {
  Monitor, Send, Image as ImageIcon, BookOpen, Sparkles,
  ChevronRight, ChevronLeft, Loader2, Zap, ExternalLink,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

type MessageRole = "user" | "nexus";
type MessageType = "text" | "image" | "guide" | "guide_list" | "error";

interface ConsoleMessage {
  id: string;
  role: MessageRole;
  type: MessageType;
  text?: string;
  image?: MediaImage;
  guide?: MediaGuide;
  guideList?: MediaGuideInfo[];
  via?: "text" | "voice";
  timestamp: Date;
}

// ── Quick prompts ─────────────────────────────────────────────────────────────

const QUICK_PROMPTS = [
  { label: "Anti-inflammatory guide", query: "show me the anti-inflammatory protocol steps", icon: "🔥" },
  { label: "Gut healing 5R", query: "how to heal my gut with the 5R protocol", icon: "🦠" },
  { label: "Morning ritual", query: "show me a morning wellness routine", icon: "🌅" },
  { label: "Plant meat mastery", query: "guide to making plant-based meat substitutes", icon: "🌿" },
  { label: "Visualize turmeric", query: "generate an image of turmeric and anti-inflammatory foods", icon: "🎨" },
  { label: "Healing foods image", query: "show me an image of a healing anti-inflammatory meal", icon: "🥗" },
];

// ── Sub-components ────────────────────────────────────────────────────────────

function ImageCard({ image }: { image: MediaImage }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  return (
    <div className="rounded-2xl overflow-hidden border border-white/10 bg-white/5 max-w-lg">
      {!loaded && !error && (
        <div className="w-full h-64 flex items-center justify-center bg-white/5">
          <Loader2 className="w-6 h-6 text-white/30 animate-spin" />
        </div>
      )}
      {error && (
        <div className="w-full h-48 flex flex-col items-center justify-center bg-white/5 gap-2">
          <ImageIcon className="w-8 h-8 text-white/20" />
          <p className="text-white/30 text-sm">Image unavailable</p>
        </div>
      )}
      {!error && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={image.url}
          alt={image.prompt ?? "Wellness image"}
          className={cn("w-full object-cover transition-opacity duration-300", loaded ? "opacity-100" : "opacity-0")}
          style={{ maxHeight: 400 }}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
        />
      )}
      <div className="p-3 space-y-1">
        {image.source === "dalle-3" && (
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span className="text-violet-400 text-xs font-medium">DALL·E 3</span>
          </div>
        )}
        {image.source === "unsplash" && (
          <div className="flex items-center gap-1.5">
            <ExternalLink className="w-3 h-3 text-white/30" />
            <span className="text-white/30 text-xs">Unsplash (DALL·E unavailable)</span>
          </div>
        )}
        {image.revised_prompt && (
          <p className="text-white/40 text-xs italic leading-relaxed">{image.revised_prompt}</p>
        )}
      </div>
    </div>
  );
}

function StepImage({ image }: { image: MediaImage }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  return (
    <>
      {!loaded && !error && (
        <div className="w-full h-48 flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-white/30 animate-spin" />
        </div>
      )}
      {error && (
        <div className="w-full h-32 flex items-center justify-center">
          <ImageIcon className="w-6 h-6 text-white/20" />
        </div>
      )}
      {!error && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={image.url}
          alt="Step illustration"
          className={cn("w-full object-cover transition-opacity duration-300", loaded ? "opacity-100" : "opacity-0")}
          style={{ maxHeight: 240 }}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
        />
      )}
    </>
  );
}

function GuideCard({ guide }: { guide: MediaGuide }) {
  const [step, setStep] = useState(0);
  const current = guide.steps[step];
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden max-w-2xl w-full">
      <div className="bg-gradient-to-r from-violet-600/20 to-indigo-600/20 border-b border-white/10 p-4">
        <div className="flex items-center gap-2 mb-1">
          <BookOpen className="w-4 h-4 text-violet-400" />
          <span className="text-violet-400 text-xs font-semibold uppercase tracking-wider">Visual Guide</span>
        </div>
        <h3 className="text-white font-bold text-lg">{guide.title}</h3>
        <p className="text-white/50 text-sm">{guide.subtitle}</p>
        <div className="flex gap-1 mt-3">
          {guide.steps.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={cn("h-1.5 rounded-full transition-all", i === step ? "bg-violet-400 flex-[2]" : "bg-white/20 flex-1")}
            />
          ))}
        </div>
      </div>
      <div className="p-4 space-y-4">
        <div className="rounded-xl overflow-hidden bg-white/5 border border-white/10">
          <StepImage image={current.image} />
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{current.icon}</span>
            <div>
              <p className="text-white/40 text-xs">Step {current.step_number} of {guide.total_steps}</p>
              <h4 className="text-white font-semibold">{current.title}</h4>
            </div>
          </div>
          <p className="text-white/70 text-sm leading-relaxed">{current.description}</p>
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3">
            <p className="text-emerald-400 text-xs font-semibold mb-1">Action</p>
            <p className="text-white/80 text-sm">{current.action}</p>
          </div>
        </div>
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-white/50 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>
          <span className="text-white/30 text-xs">{step + 1} / {guide.total_steps}</span>
          <button
            onClick={() => setStep((s) => Math.min(guide.total_steps - 1, s + 1))}
            disabled={step === guide.total_steps - 1}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-white/50 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function GuideListCard({ guides, onSelect }: { guides: MediaGuideInfo[]; onSelect: (id: string) => void }) {
  return (
    <div className="space-y-2 max-w-lg w-full">
      <p className="text-white/50 text-sm mb-3">Available visual guides:</p>
      {guides.map((g) => (
        <button
          key={g.id}
          onClick={() => onSelect(g.id)}
          className="w-full text-left bg-white/5 hover:bg-white/10 border border-white/10 hover:border-violet-500/30 rounded-xl p-3 transition-all group"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium text-sm group-hover:text-violet-300 transition-colors">{g.title}</p>
              <p className="text-white/40 text-xs mt-0.5">{g.subtitle} · {g.step_count} steps</p>
            </div>
            <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-violet-400 transition-colors" />
          </div>
        </button>
      ))}
    </div>
  );
}

// ── Main Console ──────────────────────────────────────────────────────────────

export default function ConsolePage() {
  const [messages, setMessages] = useState<ConsoleMessage[]>([
    {
      id: "welcome",
      role: "nexus",
      type: "text",
      text: "Welcome to the Nexus Console. Ask me anything — by voice or text. I can generate images, show step-by-step visual guides, and answer wellness questions. Tap the mic to speak.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [dalleAvailable, setDalleAvailable] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Voice ──────────────────────────────────────────────────────────────────
  const voice = useVoice({
    voice: "nova",
    ttsEnabled: true,
    onTranscript: (text) => {
      addMessage({ role: "user", type: "text", text, via: "voice" });
    },
    onResponse: (r) => {
      addMessage({ role: "nexus", type: "text", text: r.response_text, via: "voice" });
    },
    onError: (err) => {
      addMessage({ role: "nexus", type: "error", text: `Voice error: ${err.message}` });
    },
  });

  useEffect(() => {
    mediaApi.config().then((c) => setDalleAvailable(c.dalle_available)).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, voice.state]);

  const addMessage = (msg: Omit<ConsoleMessage, "id" | "timestamp">) => {
    setMessages((p) => [
      ...p,
      { ...msg, id: Math.random().toString(36).slice(2), timestamp: new Date() },
    ]);
  };

  const handleQuery = async (query: string) => {
    if (!query.trim() || loading) return;
    setInput("");
    addMessage({ role: "user", type: "text", text: query, via: "text" });
    setLoading(true);

    try {
      const result: MediaQueryResult = await mediaApi.query(query);

      if (result.type === "image") {
        addMessage({ role: "nexus", type: "image", image: result.data as MediaImage });
      } else if (result.type === "guide") {
        addMessage({ role: "nexus", type: "guide", guide: result.data as MediaGuide });
      } else if (result.type === "guide_list") {
        addMessage({ role: "nexus", type: "guide_list", guideList: result.data as MediaGuideInfo[] });
      }

      // Text response from Nexus chat
      try {
        const chat: NexusChatResponse = await nexus.chat(query);
        if (chat.response) {
          addMessage({ role: "nexus", type: "text", text: chat.response, via: "text" });
        }
      } catch {
        // text response is optional
      }
    } catch {
      addMessage({ role: "nexus", type: "error", text: "Something went wrong. Please try again." });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const loadGuide = async (guideId: string) => {
    setLoading(true);
    addMessage({ role: "user", type: "text", text: `Show me the ${guideId.replace(/-/g, " ")} guide` });
    try {
      const guide = await mediaApi.guide(guideId, false);
      addMessage({ role: "nexus", type: "guide", guide });
    } catch {
      addMessage({ role: "nexus", type: "error", text: "Could not load guide." });
    } finally {
      setLoading(false);
    }
  };

  const isBusy = loading || voice.isProcessing;

  return (
    <div className="flex flex-col h-[calc(100dvh-56px)] md:h-screen max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-4 pb-3 border-b border-white/5 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Monitor className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-none">Nexus Console</h1>
            <p className="text-white/40 text-xs">Visual intelligence · voice · images · guides</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {dalleAvailable ? (
            <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
              <Zap className="w-3 h-3" /> DALL·E 3
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-white/30 bg-white/5 px-2 py-1 rounded-full">
              <ImageIcon className="w-3 h-3" /> Fallback images
            </span>
          )}
        </div>
      </div>

      {/* Quick prompts */}
      <div className="flex gap-2 px-4 py-2 overflow-x-auto flex-shrink-0 scrollbar-none">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p.label}
            onClick={() => handleQuery(p.query)}
            disabled={isBusy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-white/5 text-white/50 hover:text-white hover:bg-violet-600/30 transition-all whitespace-nowrap flex-shrink-0 disabled:opacity-40"
          >
            <span>{p.icon}</span> {p.label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-5 min-h-0">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn("flex gap-3", msg.role === "user" ? "justify-end" : "justify-start")}
          >
            {msg.role === "nexus" && (
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-1">
                <Monitor className="w-3.5 h-3.5 text-white" />
              </div>
            )}

            <div className={cn("max-w-[90%] space-y-2", msg.role === "user" && "items-end flex flex-col")}>
              {msg.type === "text" && msg.text && (
                <div className={cn(
                  "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                  msg.role === "user"
                    ? "bg-violet-600 text-white"
                    : "bg-white/5 border border-white/10 text-white/80"
                )}>
                  {msg.via === "voice" && msg.role === "user" && (
                    <span className="text-violet-300/60 text-xs mr-2">🎤</span>
                  )}
                  {msg.text}
                </div>
              )}
              {msg.type === "error" && (
                <div className="rounded-2xl px-4 py-3 text-sm bg-rose-500/10 border border-rose-500/20 text-rose-300">
                  {msg.text}
                </div>
              )}
              {msg.type === "image" && msg.image && <ImageCard image={msg.image} />}
              {msg.type === "guide" && msg.guide && <GuideCard guide={msg.guide} />}
              {msg.type === "guide_list" && msg.guideList && (
                <GuideListCard guides={msg.guideList} onSelect={loadGuide} />
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {(loading || voice.isProcessing) && (
          <div className="flex gap-3 items-center">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
              <Monitor className="w-3.5 h-3.5 text-white animate-pulse" />
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3 flex gap-1">
              {[0, 1, 2].map((i) => (
                <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-2" />
      </div>

      {/* Input bar */}
      <div className="flex-shrink-0 px-4 pb-4 pt-2 space-y-2">
        {/* Voice status */}
        <VoiceStatusLabel state={voice.state} error={voice.error} />

        <div className="flex gap-2 items-center">
          {/* Text input — hidden while recording/speaking */}
          {voice.state === "idle" || voice.state === "error" ? (
            <>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleQuery(input)}
                placeholder="Ask for an image, guide, or wellness question…"
                disabled={isBusy}
                className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-violet-500/50 transition-colors disabled:opacity-50"
              />
              <button
                onClick={() => handleQuery(input)}
                disabled={isBusy || !input.trim()}
                className="w-11 h-11 flex-shrink-0 rounded-2xl bg-violet-600 hover:bg-violet-500 active:scale-95 transition-all flex items-center justify-center disabled:opacity-40"
                aria-label="Send"
              >
                {loading
                  ? <Loader2 className="w-4 h-4 text-white animate-spin" />
                  : <Send className="w-4 h-4 text-white" />
                }
              </button>
            </>
          ) : (
            // While recording/processing/speaking, show a full-width status
            <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white/40 text-sm">
              {voice.state === "recording" && "Listening…"}
              {voice.state === "processing" && "Processing your question…"}
              {voice.state === "speaking" && "Speaking response…"}
            </div>
          )}

          {/* Mic button — always visible */}
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

        <p className="text-white/20 text-[11px] text-center">
          Tap mic to speak · tap again to send · right-click mic to cancel
        </p>
      </div>
    </div>
  );
}
