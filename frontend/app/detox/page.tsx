"use client";

import { useEffect, useState } from "react";
import { detox, DetoxProtocol, DayGuidance } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Droplets, ChevronRight, CheckCircle, XCircle, Zap, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const INTENSITY_COLORS: Record<string, "emerald" | "amber" | "rose"> = {
  gentle: "emerald", moderate: "amber", intensive: "rose",
};

export default function DetoxPage() {
  const [protocols, setProtocols] = useState<DetoxProtocol[]>([]);
  const [selected, setSelected] = useState<DetoxProtocol | null>(null);
  const [dayGuidance, setDayGuidance] = useState<DayGuidance | null>(null);
  const [currentDay, setCurrentDay] = useState(1);
  const [loading, setLoading] = useState(true);
  const [dayLoading, setDayLoading] = useState(false);
  const [showNexus, setShowNexus] = useState(false);

  useEffect(() => {
    detox.protocols().then(setProtocols).finally(() => setLoading(false));
  }, []);

  const selectProtocol = async (p: DetoxProtocol) => {
    setSelected(p);
    setCurrentDay(1);
    setShowNexus(false);
    setDayLoading(true);
    try {
      const guidance = await detox.dayGuidance(p.id, 1);
      setDayGuidance(guidance);
    } finally {
      setDayLoading(false);
    }
  };

  const loadDay = async (day: number) => {
    if (!selected) return;
    setCurrentDay(day);
    setDayLoading(true);
    try {
      const guidance = await detox.dayGuidance(selected.id, day);
      setDayGuidance(guidance);
    } finally {
      setDayLoading(false);
    }
  };

  if (selected && (dayGuidance || dayLoading)) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Breadcrumb */}
        <div className="flex items-center gap-3">
          <button onClick={() => { setSelected(null); setDayGuidance(null); setShowNexus(false); }}
            className="text-white/40 hover:text-white text-sm transition-colors">← Protocols</button>
          <ChevronRight className="w-4 h-4 text-white/20" />
          <span className="text-white font-medium">{selected.name}</span>
        </div>

        {/* Protocol header */}
        <div className="glass-card p-5 space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-white font-bold text-xl">{selected.name}</h2>
              <p className="text-white/50 text-sm mt-1">{selected.description}</p>
            </div>
            <div className="flex gap-2 flex-wrap justify-end">
              <Badge variant={INTENSITY_COLORS[selected.intensity]}>{selected.intensity}</Badge>
              <Badge variant="sky">{selected.duration_days} days</Badge>
            </div>
          </div>
          <div>
            <p className="text-white/30 text-xs mb-1.5">Key supplements</p>
            <div className="flex gap-1.5 flex-wrap">
              {selected.supplements.map((s) => <Badge key={s} variant="default">{s}</Badge>)}
            </div>
          </div>
          <button onClick={() => setShowNexus((v) => !v)}
            className={cn("flex items-center gap-2 text-xs font-medium transition-colors px-3 py-1.5 rounded-lg",
              showNexus ? "bg-violet-500/15 text-violet-300" : "text-white/40 hover:text-white/70 hover:bg-white/5")}>
            <Sparkles className="w-3.5 h-3.5" />
            {showNexus ? "Hide Nexus insight" : "Ask Nexus about this protocol"}
          </button>
        </div>

        {/* Nexus insight for this protocol */}
        {showNexus && (
          <NexusInsight
            context="detox"
            prompt={`I'm starting the "${selected.name}" detox protocol (${selected.duration_days} days, ${selected.intensity} intensity). Give me personalised guidance on what to expect, how to prepare, and how to maximise results.`}
            accentClass="bg-cyan-500/15 text-cyan-400"
          />
        )}

        {/* Day selector */}
        <div>
          <p className="text-white/40 text-xs uppercase tracking-wider mb-2">Select Day</p>
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
            {Array.from({ length: selected.duration_days }, (_, i) => i + 1).map((d) => (
              <button key={d} onClick={() => loadDay(d)}
                className={cn("w-10 h-10 rounded-xl text-sm font-medium flex-shrink-0 transition-all",
                  currentDay === d ? "bg-sky-600 text-white shadow-lg shadow-sky-500/30" : "bg-white/5 text-white/40 hover:text-white hover:bg-white/10")}>
                {d}
              </button>
            ))}
          </div>
        </div>

        {dayLoading ? (
          <div className="space-y-4">{[1,2,3].map((i) => <div key={i} className="glass rounded-2xl h-32 animate-pulse" />)}</div>
        ) : dayGuidance && (
          <>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Day {currentDay} — {dayGuidance.phase}</CardTitle>
                  <Badge variant="sky">Phase {dayGuidance.phase}</Badge>
                </div>
                <p className="text-white/50 text-sm mt-1">{dayGuidance.focus}</p>
              </CardHeader>
            </Card>

            <div className="grid sm:grid-cols-2 gap-4">
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2 text-base"><CheckCircle className="w-4 h-4 text-emerald-400" />Eat Today</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5">
                    {dayGuidance.eat.map((f) => (
                      <li key={f} className="text-white/70 text-sm flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />{f}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2 text-base"><XCircle className="w-4 h-4 text-rose-400" />Avoid Today</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5">
                    {dayGuidance.avoid.map((f) => (
                      <li key={f} className="text-white/70 text-sm flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 flex-shrink-0" />{f}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Zap className="w-4 h-4 text-amber-400" />Daily Practices</CardTitle></CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {dayGuidance.practices.map((p) => (
                    <li key={p} className="text-white/70 text-sm flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />{p}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <div className="grid sm:grid-cols-2 gap-4">
              <Card>
                <CardHeader><CardTitle className="text-base">Supplements</CardTitle></CardHeader>
                <CardContent><div className="flex flex-wrap gap-2">{dayGuidance.supplements.map((s) => <Badge key={s} variant="sky">{s}</Badge>)}</div></CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle className="text-base text-amber-400">Expected Symptoms</CardTitle></CardHeader>
                <CardContent><div className="flex flex-wrap gap-2">{dayGuidance.expected_symptoms.map((s) => <Badge key={s} variant="amber">{s}</Badge>)}</div></CardContent>
              </Card>
            </div>

            {/* Day-specific Nexus insight */}
            <NexusInsight
              context="detox"
              prompt={`I'm on Day ${currentDay} of the "${selected.name}" detox. Today's focus is "${dayGuidance.focus}". Give me specific guidance for today — what to prioritise, how to manage any symptoms, and what to watch for.`}
              accentClass="bg-cyan-500/15 text-cyan-400"
              lazy
            />
          </>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Droplets className="w-7 h-7 text-sky-400" /> Detox Protocols
        </h1>
        <p className="text-white/40 mt-1">Science-backed cleanse programs for deep renewal.</p>
      </div>

      <NexusInsight
        context="detox"
        prompt="Which detox protocol would you recommend for me right now, and why? Consider my overall wellness goals and give me a clear, personalised recommendation."
        accentClass="bg-cyan-500/15 text-cyan-400"
      />

      {loading ? (
        <div className="space-y-4">{[1,2,3].map((i) => <div key={i} className="glass rounded-2xl h-40 animate-pulse" />)}</div>
      ) : (
        <div className="space-y-4">
          {protocols.map((p) => (
            <Card key={p.id} className="hover:bg-white/8 transition-all cursor-pointer" onClick={() => selectProtocol(p)}>
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <CardTitle>{p.name}</CardTitle>
                    <p className="text-white/50 text-sm mt-1">{p.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-white/30 flex-shrink-0 mt-1" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 flex-wrap mb-3">
                  <Badge variant={INTENSITY_COLORS[p.intensity]}>{p.intensity}</Badge>
                  <Badge variant="sky">{p.duration_days} days</Badge>
                  <Badge variant="default">{p.phases.length} phases</Badge>
                </div>
                <div>
                  <p className="text-white/30 text-xs mb-1">Key supplements</p>
                  <div className="flex gap-1 flex-wrap">
                    {p.supplements.slice(0, 4).map((s) => <Badge key={s} variant="default">{s}</Badge>)}
                    {p.supplements.length > 4 && <span className="text-white/25 text-xs self-center">+{p.supplements.length - 4}</span>}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
