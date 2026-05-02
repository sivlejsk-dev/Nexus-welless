"use client";

/**
 * NexusInsight — reusable Nexus AI panel used on every section page.
 *
 * Usage:
 *   <NexusInsight context="meditation" prompt="Give me a meditation insight for stress relief" />
 *
 * The component fetches a Nexus chat response on mount (or on demand) and
 * renders it with a consistent glass-card style. It also exposes a text input
 * so the user can ask follow-up questions in context.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { nexus } from "@/lib/api";
import { Sparkles, RefreshCw, Send, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface NexusInsightProps {
  /** Short label shown in the header, e.g. "Meditation" */
  context: string;
  /** Initial prompt sent to Nexus on mount */
  prompt: string;
  /** Accent colour class for the icon ring, defaults to violet */
  accentClass?: string;
  /** If true, don't auto-fetch on mount — wait for user to click */
  lazy?: boolean;
  /** Extra className on the outer wrapper */
  className?: string;
}

export function NexusInsight({
  context,
  prompt,
  accentClass = "bg-violet-500/15 text-violet-400",
  lazy = false,
  className,
}: NexusInsightProps) {
  const [insight, setInsight] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [followUp, setFollowUp] = useState("");
  const [collapsed, setCollapsed] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const fetch = useCallback(async (q: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await nexus.chat(q);
      setInsight(res.response);
    } catch {
      setError("Nexus is unavailable right now. Try again in a moment.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!lazy) fetch(prompt);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendFollowUp = () => {
    const q = followUp.trim();
    if (!q || loading) return;
    setFollowUp("");
    fetch(`[${context}] ${q}`);
  };

  return (
    <div className={cn("glass-card overflow-hidden", className)}>
      {/* Header */}
      <button
        onClick={() => setCollapsed((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/3 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={cn("w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0", accentClass)}>
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="text-left">
            <p className="text-white/90 font-semibold text-sm leading-none">Nexus AI Insight</p>
            <p className="text-white/35 text-xs mt-0.5">{context} · personalised guidance</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!loading && insight && (
            <button
              onClick={(e) => { e.stopPropagation(); fetch(prompt); }}
              className="p-1.5 rounded-lg text-white/25 hover:text-white/60 hover:bg-white/5 transition-all"
              title="Refresh insight"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
          {collapsed
            ? <ChevronDown className="w-4 h-4 text-white/30" />
            : <ChevronUp className="w-4 h-4 text-white/30" />
          }
        </div>
      </button>

      {!collapsed && (
        <div className="px-5 pb-5 space-y-4 border-t border-white/5">
          {/* Content */}
          <div className="pt-4 min-h-[60px]">
            {loading && (
              <div className="space-y-2.5">
                {[1, 0.85, 0.7].map((w, i) => (
                  <div
                    key={i}
                    className="h-3 rounded-full bg-white/8 animate-pulse"
                    style={{ width: `${w * 100}%`, animationDelay: `${i * 0.12}s` }}
                  />
                ))}
              </div>
            )}
            {!loading && error && (
              <p className="text-rose-400/80 text-sm">{error}</p>
            )}
            {!loading && !error && !insight && lazy && (
              <button
                onClick={() => fetch(prompt)}
                className="flex items-center gap-2 text-violet-400 text-sm hover:text-violet-300 transition-colors"
              >
                <Sparkles className="w-4 h-4" />
                Ask Nexus for {context} guidance
              </button>
            )}
            {!loading && insight && (
              <p className="text-white/75 text-sm leading-relaxed whitespace-pre-line">{insight}</p>
            )}
          </div>

          {/* Follow-up input */}
          {(insight || !lazy) && (
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={followUp}
                onChange={(e) => setFollowUp(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendFollowUp()}
                placeholder={`Ask Nexus about ${context}…`}
                disabled={loading}
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-xs placeholder:text-white/25 focus:outline-none focus:border-violet-500/40 transition-colors disabled:opacity-40"
              />
              <button
                onClick={sendFollowUp}
                disabled={loading || !followUp.trim()}
                className="w-8 h-8 rounded-xl bg-violet-600 hover:bg-violet-500 flex items-center justify-center transition-all disabled:opacity-30 flex-shrink-0"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
