"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { meditation, MeditationGuide } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Brain, Clock, Play, ChevronDown, ChevronUp } from "lucide-react";

const CATEGORIES = ["all", "breathwork", "body-scan", "visualization", "mantra"];
const CATEGORY_COLORS: Record<string, "violet" | "emerald" | "amber" | "rose" | "sky"> = {
  breathwork: "sky",
  "body-scan": "emerald",
  visualization: "violet",
  mantra: "amber",
  sleep: "rose",
};

export default function MeditationPage() {
  const searchParams = useSearchParams();
  const [guides, setGuides] = useState<MeditationGuide[]>([]);
  const [category, setCategory] = useState("all");
  const [expanded, setExpanded] = useState<string | null>(searchParams.get("guide"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = category !== "all" ? { category } : undefined;
    meditation.guides(params)
      .then(setGuides)
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Brain className="w-7 h-7 text-violet-400" /> Meditation
        </h1>
        <p className="text-white/40 mt-1">Guided sessions for every state of mind.</p>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              category === c
                ? "bg-violet-600 text-white"
                : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10"
            }`}
          >
            {c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>

      {/* Guides */}
      {loading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass rounded-2xl h-24 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {guides.map((guide) => (
            <Card key={guide.id} className="cursor-pointer hover:bg-white/8 transition-all">
              <div
                className="flex items-start gap-4"
                onClick={() => setExpanded(expanded === guide.id ? null : guide.id)}
              >
                <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                  <Brain className="w-5 h-5 text-violet-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-white font-semibold">{guide.title}</h3>
                      <p className="text-white/50 text-sm mt-0.5 line-clamp-1">{guide.description}</p>
                    </div>
                    {expanded === guide.id ? (
                      <ChevronUp className="w-4 h-4 text-white/30 flex-shrink-0 mt-1" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-white/30 flex-shrink-0 mt-1" />
                    )}
                  </div>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    <Badge variant={CATEGORY_COLORS[guide.category] ?? "default"}>
                      {guide.category}
                    </Badge>
                    <Badge variant="default">
                      <Clock className="w-3 h-3 mr-1" />
                      {guide.duration_minutes} min
                    </Badge>
                    <Badge variant="default">{guide.level}</Badge>
                    {guide.tags.slice(0, 2).map((t) => (
                      <Badge key={t} variant="default">{t}</Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Expanded script */}
              {expanded === guide.id && guide.script && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Guided Script</p>
                  <ol className="space-y-2">
                    {guide.script.map((step, i) => (
                      <li key={i} className="flex gap-3 text-sm text-white/70">
                        <span className="text-violet-400 font-mono text-xs mt-0.5 flex-shrink-0">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        {step}
                      </li>
                    ))}
                  </ol>
                  <Button className="mt-4" size="sm">
                    <Play className="w-3.5 h-3.5 mr-2" />
                    Begin Session
                  </Button>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
