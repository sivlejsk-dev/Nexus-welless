"use client";

/**
 * NexusFab — floating action button that opens a mini Nexus chat overlay.
 * Rendered in the app layout so it appears on every authenticated page.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { nexus } from "@/lib/api";
import { Sparkles, X, Send, Mic, MicOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessage {
  id: string;
  role: "user" | "nexus";
  text: string;
}

// Map pathnames to a context label Nexus uses to stay on-topic
function contextFromPath(path: string): string {
  if (path.startsWith("/meditation")) return "meditation";
  if (path.startsWith("/nutrition"))  return "nutrition";
  if (path.startsWith("/detox"))      return "detox";
  if (path.startsWith("/astrology"))  return "astrology";
  if (path.startsWith("/plant-kitchen")) return "plant-based cooking";
  if (path.startsWith("/console"))    return "wellness media";
  if (path.startsWith("/profile"))    return "wellness profile";
  return "wellness";
}

export function NexusFab() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  const context = contextFromPath(pathname);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Focus input when opened
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 120);
  }, [open]);

  // Seed a welcome message when first opened
  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([{
        id: "welcome",
        role: "nexus",
        text: `I'm Nexus. You're in ${context} — ask me anything and I'll give you personalised guidance.`,
      }]);
    }
  }, [open, context, messages.length]);

  const send = useCallback(async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setInput("");
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", text: msg };
    setMessages((p) => [...p, userMsg]);
    setLoading(true);
    try {
      const res = await nexus.chat(`[${context}] ${msg}`);
      setMessages((p) => [...p, { id: Date.now().toString() + "n", role: "nexus", text: res.response }]);
    } catch {
      setMessages((p) => [...p, { id: Date.now().toString() + "e", role: "nexus", text: "Something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, context]);

  const toggleVoice = useCallback(() => {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    const SR = w.webkitSpeechRecognition ?? w.SpeechRecognition;
    if (!SR) return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const rec: any = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    rec.onresult = (e: any) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const transcript = Array.from(e.results as any[]).map((r: any) => r[0].transcript).join(" ").trim();
      if (transcript) send(transcript);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  }, [listening, send]);

  // Don't show on login page
  if (pathname === "/login") return null;

  return (
    <>
      {/* Overlay panel */}
      {open && (
        <div className="fixed bottom-24 right-4 md:bottom-8 md:right-6 z-50 w-[min(360px,calc(100vw-2rem))] flex flex-col rounded-2xl overflow-hidden shadow-2xl shadow-black/60 border border-white/10"
          style={{ background: "rgba(10,10,20,0.96)", backdropFilter: "blur(24px)", maxHeight: "min(520px, 70dvh)" }}>

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/8 flex-shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-500/30">
                <Sparkles className="w-3.5 h-3.5 text-white" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm leading-none">Nexus</p>
                <p className="text-white/35 text-[10px] mt-0.5 capitalize">{context} assistant</p>
              </div>
            </div>
            <button onClick={() => setOpen(false)} className="p-1.5 rounded-lg text-white/30 hover:text-white/70 hover:bg-white/5 transition-all">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
            {messages.map((m) => (
              <div key={m.id} className={cn("flex gap-2", m.role === "user" ? "justify-end" : "justify-start")}>
                {m.role === "nexus" && (
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                )}
                <div className={cn(
                  "max-w-[85%] rounded-2xl px-3 py-2 text-xs leading-relaxed",
                  m.role === "user"
                    ? "bg-violet-600/30 border border-violet-500/30 text-white/90"
                    : "bg-white/6 border border-white/8 text-white/75"
                )}>
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <div className="bg-white/6 border border-white/8 rounded-2xl px-3 py-2 flex gap-1 items-center">
                  {[0, 1, 2].map((i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400/60 animate-bounce" style={{ animationDelay: `${i * 0.18}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="flex gap-2 px-3 py-3 border-t border-white/8 flex-shrink-0">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder={`Ask about ${context}…`}
              disabled={loading}
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-xs placeholder:text-white/25 focus:outline-none focus:border-violet-500/40 transition-colors disabled:opacity-40"
            />
            <button
              onClick={toggleVoice}
              className={cn(
                "w-8 h-8 rounded-xl flex items-center justify-center transition-all flex-shrink-0",
                listening ? "bg-red-600 text-white animate-pulse" : "bg-white/8 text-white/40 hover:text-white/70 hover:bg-white/12"
              )}
              title={listening ? "Stop listening" : "Speak"}
            >
              {listening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={() => send()}
              disabled={loading || !input.trim()}
              className="w-8 h-8 rounded-xl bg-violet-600 hover:bg-violet-500 flex items-center justify-center transition-all disabled:opacity-30 flex-shrink-0"
            >
              <Send className="w-3.5 h-3.5 text-white" />
            </button>
          </div>
        </div>
      )}

      {/* FAB button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "fixed bottom-20 right-4 md:bottom-6 md:right-6 z-50",
          "w-14 h-14 rounded-2xl shadow-xl transition-all duration-300 active:scale-95",
          "flex items-center justify-center",
          open
            ? "bg-white/10 border border-white/20 text-white/60 rotate-12"
            : "bg-gradient-to-br from-violet-600 to-indigo-600 shadow-violet-500/40 hover:shadow-violet-500/60 hover:scale-105"
        )}
        aria-label="Open Nexus assistant"
      >
        {open
          ? <X className="w-5 h-5 text-white/70" />
          : <Sparkles className="w-6 h-6 text-white" />
        }
        {!open && (
          <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#07070f] animate-pulse" />
        )}
      </button>
    </>
  );
}
