"use client";

import { useState } from "react";
import { nexus, NexusResponse } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles, Send, Brain, Leaf, Star, Droplets } from "lucide-react";

const MODULES = [
  { id: "nutrition", label: "Nutrition", icon: Leaf, color: "emerald" as const },
  { id: "meditation", label: "Meditation", icon: Brain, color: "violet" as const },
  { id: "detox", label: "Detox", icon: Droplets, color: "sky" as const },
  { id: "astrology", label: "Astrology", icon: Star, color: "amber" as const },
  { id: "general", label: "General", icon: Sparkles, color: "rose" as const },
];

interface Message {
  role: "user" | "nexus";
  content: string;
  module?: string;
  action_items?: string[];
}

export default function NexusPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "nexus",
      content: "I am Nexus — your personal wellness intelligence. Ask me anything about nutrition, meditation, detox, astrology, or your overall wellbeing. I'll provide guidance tailored to your unique profile.",
    },
  ]);
  const [input, setInput] = useState("");
  const [module, setModule] = useState("general");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res: NexusResponse = await nexus.recommend(module, {}, userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "nexus",
          content: res.recommendation,
          module: res.module,
          action_items: res.action_items,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "nexus", content: "I'm unable to connect right now. Please ensure the Nexus API is configured." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-4rem)] space-y-4">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Sparkles className="w-7 h-7 text-violet-400" /> Nexus AI
        </h1>
        <p className="text-white/40 mt-1">Your personal wellness intelligence engine.</p>
      </div>

      {/* Module selector */}
      <div className="flex gap-2 flex-wrap">
        {MODULES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setModule(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              module === id
                ? "bg-violet-600 text-white"
                : "bg-white/5 text-white/50 hover:text-white"
            }`}
          >
            <Icon className="w-3 h-3" />
            {label}
          </button>
        ))}
      </div>

      {/* Chat window */}
      <div className="flex-1 overflow-y-auto space-y-4 min-h-0">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "nexus" && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mr-3 mt-1">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] ${msg.role === "user" ? "order-first" : ""}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-violet-600 text-white ml-auto"
                    : "glass text-white/80"
                }`}
              >
                {msg.content}
              </div>
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
        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white animate-pulse" />
            </div>
            <div className="glass rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-3 pb-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder={`Ask Nexus about ${module}…`}
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder:text-white/20 focus:outline-none focus:border-violet-500/50 transition-colors"
        />
        <Button onClick={sendMessage} disabled={loading || !input.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
