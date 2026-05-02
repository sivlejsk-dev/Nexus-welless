"use client";

import { useEffect, useRef, useState } from "react";
import {
  mediaApi, nexus,
  MediaImage, MediaGuide, MediaGuideInfo,
  MediaQueryResult, NexusChatResponse, MediaVideo,
} from "@/lib/api";
import {
  fallbackGuideList,
  fallbackVideos,
  getFallbackGuide,
  getFallbackMedia,
} from "@/lib/media-fallback";
import { useVoice } from "@/lib/use-voice";
import { VoiceButton, VoiceStatusLabel } from "@/components/ui/voice-button";
import { cn } from "@/lib/utils";
import {
  Monitor, Send, Image as ImageIcon, BookOpen, Sparkles,
  ChevronRight, ChevronLeft, Loader2, Zap, ExternalLink, AlertCircle, RotateCcw,
  Video, PlayCircle, CheckCircle2, Compass, WifiOff,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

type MessageRole = "user" | "nexus";
type MessageType = "text" | "image" | "video" | "guide" | "guide_list" | "error";
type MediaMode = "auto" | "image" | "video" | "guide";

interface ConsoleMessage {
  id: string;
  role: MessageRole;
  type: MessageType;
  text?: string;
  image?: MediaImage;
  video?: MediaVideo;
  guide?: MediaGuide;
  guideList?: MediaGuideInfo[];
  via?: "text" | "voice";
  retryQuery?: string; // Query to retry if this is an error message
  timestamp: Date;
}

// ── Quick prompts ─────────────────────────────────────────────────────────────

const QUICK_PROMPTS = [
  { label: "Anti-inflammatory guide", query: "show me the anti-inflammatory protocol steps", icon: "🔥" },
  { label: "Gut healing 5R", query: "how to heal my gut with the 5R protocol", icon: "🦠" },
  { label: "Morning ritual", query: "show me a morning wellness routine", icon: "🌅" },
  { label: "Breathwork video", query: "show me a breathwork video", icon: "▶️" },
  { label: "Plant meat mastery", query: "guide to making plant-based meat substitutes", icon: "🌿" },
  { label: "Visualize turmeric", query: "generate an image of turmeric and anti-inflammatory foods", icon: "🎨" },
  { label: "Healing foods image", query: "show me an image of a healing anti-inflammatory meal", icon: "🥗" },
];

// ── Sub-components ────────────────────────────────────────────────────────────

function VisualFallback({ image, compact = false }: { image: MediaImage; compact?: boolean }) {
  return (
    <div className={cn(
      "w-full flex flex-col items-center justify-center bg-gradient-to-br from-violet-950/70 via-slate-900 to-emerald-950/60 text-center",
      compact ? "h-32" : "h-56",
    )}>
      <ImageIcon className="w-8 h-8 text-white/25 mb-2" />
      <p className="text-white/60 text-sm font-medium">{image.prompt ?? "Wellness visual"}</p>
      <p className="text-white/30 text-xs mt-1">Local visual fallback</p>
    </div>
  );
}

function ImageCard({ image }: { image: MediaImage }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  
  return (
    <div className="rounded-2xl overflow-hidden border border-white/10 bg-gradient-to-br from-white/5 to-white/2 max-w-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
      {!loaded && !error && (
        <div className="w-full h-64 flex items-center justify-center bg-gradient-to-br from-white/5 to-white/2">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
            <p className="text-white/40 text-xs">Loading image...</p>
          </div>
        </div>
      )}
      {error && (
        <VisualFallback image={image} />
      )}
      {!error && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={image.url}
          alt={image.prompt ?? "Wellness image"}
          className={cn("w-full object-cover transition-all duration-500", loaded ? "opacity-100 scale-100" : "opacity-0 scale-95")}
          style={{ maxHeight: 400 }}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
          loading="lazy"
        />
      )}
      <div className="p-4 space-y-2 bg-white/2 border-t border-white/5">
        <div className="flex items-center justify-between">
          {image.source === "dalle-3" && (
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-violet-400 animate-pulse" />
              <span className="text-violet-400 text-xs font-semibold">DALL·E 3</span>
            </div>
          )}
          {image.source === "unsplash" && (
            <div className="flex items-center gap-1.5">
              <ExternalLink className="w-3 h-3 text-white/40" />
              <span className="text-white/40 text-xs">Unsplash</span>
            </div>
          )}
          {image.source === "local" && (
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400 text-xs font-semibold">Local fallback</span>
            </div>
          )}
        </div>
        {image.revised_prompt && (
          <p className="text-white/50 text-xs italic leading-relaxed">{image.revised_prompt}</p>
        )}
        {image.prompt && image.source === "dalle-3" && (
          <p className="text-white/40 text-xs leading-relaxed">{image.prompt}</p>
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
        <div className="w-full h-48 flex items-center justify-center bg-gradient-to-br from-white/5 to-white/2">
          <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
        </div>
      )}
      {error && (
        <VisualFallback image={image} compact />
      )}
      {!error && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={image.url}
          alt="Step illustration"
          className={cn("w-full object-cover transition-all duration-500", loaded ? "opacity-100 scale-100" : "opacity-0 scale-95")}
          style={{ maxHeight: 240 }}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
          loading="lazy"
        />
      )}
    </>
  );
}

function VideoCard({ video }: { video: MediaVideo }) {
  const [playing, setPlaying] = useState(false);

  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-white/2 overflow-hidden max-w-2xl w-full shadow-lg">
      <div className="relative aspect-video bg-black">
        {playing ? (
          <iframe
            src={`${video.embed_url}?autoplay=1&rel=0`}
            title={video.title}
            className="absolute inset-0 h-full w-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <button
            onClick={() => setPlaying(true)}
            className="absolute inset-0 w-full h-full text-left group"
            aria-label={`Play ${video.title}`}
          >
            <StepImage image={video.thumbnail} />
            <div className="absolute inset-0 bg-black/35 group-hover:bg-black/20 transition-colors" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-16 h-16 rounded-full bg-white/90 text-slate-950 flex items-center justify-center shadow-xl group-hover:scale-105 transition-transform">
                <PlayCircle className="w-9 h-9" />
              </div>
            </div>
          </button>
        )}
      </div>
      <div className="p-5 space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Video className="w-4 h-4 text-sky-400" />
            <span className="text-sky-300 text-xs font-bold uppercase tracking-wider">{video.duration}</span>
          </div>
          <h3 className="text-white font-bold text-lg">{video.title}</h3>
          <p className="text-white/55 text-sm mt-1">{video.description}</p>
        </div>
        <div className="grid sm:grid-cols-2 gap-2">
          {video.steps.map((item, index) => (
            <div key={item} className="flex items-center gap-2 rounded-xl bg-white/[0.04] border border-white/10 px-3 py-2">
              <span className="text-sky-300 text-xs font-mono">{String(index + 1).padStart(2, "0")}</span>
              <span className="text-white/70 text-sm">{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GuideCard({ guide }: { guide: MediaGuide }) {
  const [step, setStep] = useState(0);
  const current = guide.steps[step];
  const progress = ((step + 1) / guide.total_steps) * 100;

  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-white/2 overflow-hidden max-w-2xl w-full shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-violet-600/30 to-indigo-600/20 border-b border-white/10 p-5">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="w-4 h-4 text-violet-400" />
          <span className="text-violet-400 text-xs font-semibold uppercase tracking-wider">Visual Guide</span>
        </div>
        <h3 className="text-white font-bold text-lg mb-1">{guide.title}</h3>
        <p className="text-white/50 text-sm mb-4">{guide.subtitle}</p>
        
        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-white/40 text-xs font-medium">Progress</span>
            <span className="text-white/40 text-xs">{step + 1} / {guide.total_steps}</span>
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        
        {/* Step dots */}
        <div className="flex gap-1 mt-4">
          {guide.steps.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={cn(
                "h-2 rounded-full transition-all duration-300",
                i === step 
                  ? "bg-violet-400 flex-[2]" 
                  : i < step 
                  ? "bg-emerald-500/60" 
                  : "bg-white/20 flex-1"
              )}
              title={`Step ${i + 1}`}
            />
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* Step image */}
        <div className="rounded-xl overflow-hidden bg-white/5 border border-white/10 shadow-sm">
          <StepImage image={current.image} />
        </div>

        {/* Step details */}
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center gap-3">
            <span className="text-3xl flex-shrink-0">{current.icon}</span>
            <div>
              <p className="text-white/40 text-xs font-medium">Step {current.step_number} of {guide.total_steps}</p>
              <h4 className="text-white font-bold text-base">{current.title}</h4>
            </div>
          </div>

          {/* Description */}
          <p className="text-white/70 text-sm leading-relaxed">{current.description}</p>

          {/* Action box */}
          <div className="bg-emerald-500/15 border border-emerald-500/30 rounded-xl p-4 backdrop-blur-sm">
            <p className="text-emerald-400 text-xs font-bold mb-2 uppercase tracking-wider">Action</p>
            <p className="text-white/85 text-sm leading-relaxed">{current.action}</p>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-2 gap-2">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>
          <span className="text-white/30 text-xs font-medium">{step + 1} / {guide.total_steps}</span>
          <button
            onClick={() => setStep((s) => Math.min(guide.total_steps - 1, s + 1))}
            disabled={step === guide.total_steps - 1}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
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
  const [offlineMedia, setOfflineMedia] = useState(false);
  const [mediaMode, setMediaMode] = useState<MediaMode>("auto");
  const [voiceQuery, setVoiceQuery] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Voice ──────────────────────────────────────────────────────────────────
  const voice = useVoice({
    voice: "nova",
    ttsEnabled: true,
    onTranscript: (text) => {
      setVoiceQuery(text);
    },
    onResponse: (r) => {
      addMessage({ role: "nexus", type: "text", text: r.response_text, via: "voice" });
    },
    onError: (err) => {
      const aborted = err.message.includes("signal is aborted") || err.name === "AbortError";
      addMessage({
        role: "nexus",
        type: aborted ? "text" : "error",
        text: aborted
          ? "Voice capture was interrupted. Please try speaking again, or type your question below."
          : `Voice error: ${err.message}`,
      });
    },
  });

  useEffect(() => {
    mediaApi.config()
      .then((c) => {
        setDalleAvailable(c.dalle_available);
        setOfflineMedia(false);
      })
      .catch(() => {
        setDalleAvailable(false);
        setOfflineMedia(true);
      });
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

  const speakText = (text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const pushMediaResult = (result: MediaQueryResult, query: string): string => {
    if (result.type === "image") {
      const image = result.data as MediaImage;
      addMessage(
        image.url
          ? { role: "nexus", type: "image", image }
          : { role: "nexus", type: "error", text: "Image URL not available. Please try another query.", retryQuery: query },
      );
      return image.url ? `Here is an image for ${query}.` : "I could not load that image.";
    }

    if (result.type === "video") {
      const video = result.data as MediaVideo;
      addMessage({ role: "nexus", type: "video", video });
      return `I found a video for you: ${video.title}.`;
    }

    if (result.type === "guide") {
      const guide = result.data as MediaGuide;
      addMessage(
        guide.steps?.length
          ? { role: "nexus", type: "guide", guide }
          : { role: "nexus", type: "error", text: "Guide data is incomplete. Please try again.", retryQuery: query },
      );
      return guide.steps?.length
        ? `Here is the ${guide.title} guide with ${guide.total_steps} steps.`
        : "I could not load that guide.";
    }

    addMessage({ role: "nexus", type: "guide_list", guideList: result.data as MediaGuideInfo[] });
    return "Here are the available visual wellness guides.";
  };

  const handleQuery = async (query: string, retryCount = 0, via: "text" | "voice" = "text") => {
    if (!query.trim() || loading) return;
    
    setInput("");
    addMessage({ role: "user", type: "text", text: query, via });
    setLoading(true);

    try {
      const result = mediaMode === "video"
        ? getFallbackMedia(query, "video")
        : await mediaApi.query(query, mediaMode);
      setOfflineMedia(false);
      const mediaSummary = pushMediaResult(result, query);
      let spokeResponse = false;

      // Text response from Nexus chat (optional, non-blocking)
      try {
        const chatController = new AbortController();
        const chatTimeoutId = setTimeout(() => chatController.abort(), 10000);
        try {
          const chat: NexusChatResponse = await nexus.chat(query);
          if (chat.response) {
            addMessage({ role: "nexus", type: "text", text: chat.response, via });
            if (via === "voice") {
              speakText(chat.response);
              spokeResponse = true;
            }
          }
        } finally {
          clearTimeout(chatTimeoutId);
        }
      } catch (chatErr) {
        // Chat is optional, fail silently
        console.debug("Chat response skipped:", chatErr);
      }
      if (via === "voice" && !spokeResponse) {
        speakText(mediaSummary);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      const fallback = getFallbackMedia(query, mediaMode);
      setOfflineMedia(true);
      const spoken = pushMediaResult(fallback, query);
      if (via === "voice") {
        speakText(spoken);
      }
      
      if (retryCount < 1 && mediaMode !== "auto" && (errorMessage.includes("Failed to fetch") || errorMessage.includes("timeout"))) {
        addMessage({ role: "nexus", type: "text", text: "Retrying your request..." });
        setTimeout(() => handleQuery(query, retryCount + 1), 1500);
      }

      console.warn("Media query fell back to local content.", { error, retryCount });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  useEffect(() => {
    if (!voiceQuery) {
      return;
    }
    void handleQuery(voiceQuery, 0, "voice");
    queueMicrotask(() => setVoiceQuery(null));
    // handleQuery intentionally reads the latest console state when the transcript arrives.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [voiceQuery]);

  const loadGuide = async (guideId: string) => {
    setLoading(true);
    addMessage({ role: "user", type: "text", text: `Show me the ${guideId.replace(/-/g, " ")} guide` });
    try {
      const guide = await mediaApi.guide(guideId, false);
      setOfflineMedia(false);
      if (guide.steps && guide.steps.length > 0) {
        addMessage({ role: "nexus", type: "guide", guide });
      } else {
        addMessage({ role: "nexus", type: "error", text: "Guide data is incomplete.", retryQuery: guideId });
      }
    } catch (error) {
      const fallbackGuide = getFallbackGuide(guideId);
      if (fallbackGuide) {
        setOfflineMedia(true);
        addMessage({ role: "nexus", type: "guide", guide: fallbackGuide });
        addMessage({
          role: "nexus",
          type: "text",
          text: "I could not reach the guide service, so I opened the local guide version.",
        });
        return;
      }
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      addMessage({ 
        role: "nexus", 
        type: "error", 
        text: `Could not load guide. ${errorMessage.substring(0, 50)}`,
        retryQuery: guideId 
      });
      console.warn("Guide load failed.", error);
    } finally {
      setLoading(false);
    }
  };

  const isBusy = loading || voice.isProcessing;
  const modeOptions: Array<{ id: MediaMode; label: string; icon: typeof Compass }> = [
    { id: "auto", label: "Auto", icon: Compass },
    { id: "image", label: "Images", icon: ImageIcon },
    { id: "video", label: "Videos", icon: Video },
    { id: "guide", label: "Guides", icon: BookOpen },
  ];

  return (
    <div className="flex flex-col h-[calc(100dvh-56px)] md:h-screen max-w-6xl mx-auto">
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
          ) : offlineMedia ? (
            <span className="flex items-center gap-1.5 text-xs text-amber-300 bg-amber-400/10 px-2 py-1 rounded-full">
              <WifiOff className="w-3 h-3" /> Local media
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

      <div className="flex items-center justify-between gap-3 px-4 pb-3 border-b border-white/5 flex-shrink-0">
        <div className="flex gap-1 rounded-2xl bg-white/[0.04] border border-white/10 p-1">
          {modeOptions.map((option) => {
            const Icon = option.icon;
            return (
              <button
                key={option.id}
                onClick={() => setMediaMode(option.id)}
                className={cn(
                  "flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium transition-all",
                  mediaMode === option.id
                    ? "bg-violet-600 text-white shadow-sm"
                    : "text-white/45 hover:text-white hover:bg-white/10",
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {option.label}
              </button>
            );
          })}
        </div>
        <button
          onClick={() => addMessage({ role: "nexus", type: "guide_list", guideList: fallbackGuideList() })}
          className="hidden sm:flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs text-white/55 hover:text-white hover:bg-white/10 transition-all"
        >
          <BookOpen className="w-3.5 h-3.5" />
          Browse guides
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 grid lg:grid-cols-[1fr_260px]">
      <div className="overflow-y-auto px-4 py-2 space-y-5 min-h-0">
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
                <div className="space-y-2 max-w-sm">
                  <div className="rounded-2xl px-4 py-3 text-sm bg-gradient-to-br from-rose-500/20 to-rose-500/10 border border-rose-500/30 text-rose-200 flex gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <span>{msg.text}</span>
                  </div>
                  {msg.retryQuery && (
                    <button
                      onClick={() => handleQuery(msg.retryQuery!)}
                      disabled={loading}
                      className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-medium bg-white/10 hover:bg-white/20 text-white/70 hover:text-white border border-white/10 transition-all disabled:opacity-50"
                    >
                      <RotateCcw className="w-3 h-3" /> Try Again
                    </button>
                  )}
                </div>
              )}
              {msg.type === "image" && msg.image && <ImageCard image={msg.image} />}
              {msg.type === "video" && msg.video && <VideoCard video={msg.video} />}
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

      <aside className="hidden lg:block border-l border-white/5 px-4 py-4 overflow-y-auto">
        <div className="space-y-5">
          <div>
            <p className="text-white/35 text-xs uppercase tracking-wider mb-3">Video picks</p>
            <div className="space-y-2">
              {fallbackVideos.map((video) => (
                <button
                  key={video.id}
                  onClick={() => {
                    addMessage({ role: "user", type: "text", text: video.title });
                    addMessage({ role: "nexus", type: "video", video });
                  }}
                  className="w-full text-left rounded-xl border border-white/10 bg-white/[0.04] p-3 hover:bg-white/10 hover:border-sky-400/30 transition-all"
                >
                  <div className="flex items-center gap-2 text-sky-300 text-xs font-medium">
                    <Video className="w-3.5 h-3.5" />
                    {video.duration}
                  </div>
                  <p className="mt-1 text-white/80 text-sm font-medium">{video.title}</p>
                  <p className="mt-1 text-white/35 text-xs line-clamp-2">{video.description}</p>
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-white/35 text-xs uppercase tracking-wider mb-3">Guide library</p>
            <GuideListCard guides={fallbackGuideList()} onSelect={loadGuide} />
          </div>
        </div>
      </aside>
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
