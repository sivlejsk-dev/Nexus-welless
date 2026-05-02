"use client";

import { useEffect, useState } from "react";
import { astrology, Horoscope, BirthChart, SignProfile } from "@/lib/api";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Star, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const SIGNS = [
  "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
];

const SIGN_SYMBOLS: Record<string, string> = {
  Aries:"♈",Taurus:"♉",Gemini:"♊",Cancer:"♋",Leo:"♌",Virgo:"♍",
  Libra:"♎",Scorpio:"♏",Sagittarius:"♐",Capricorn:"♑",Aquarius:"♒",Pisces:"♓",
};

export default function AstrologyPage() {
  const [activeTab, setActiveTab] = useState<"horoscope" | "chart" | "signs">("horoscope");
  const [selectedSign, setSelectedSign] = useState("Aries");
  const [horoscope, setHoroscope] = useState<Horoscope | null>(null);
  const [chart, setChart] = useState<BirthChart | null>(null);
  const [signs, setSigns] = useState<SignProfile[]>([]);
  const [loading, setLoading] = useState(false);

  const loadHoroscope = async (sign: string) => {
    setLoading(true);
    try { setHoroscope(await astrology.horoscope(sign)); }
    finally { setLoading(false); }
  };

  const loadChart = async () => {
    setLoading(true);
    try { setChart(await astrology.myChart()); }
    catch {
      setChart({
        sun:     { planet: "Sun",       sign: "Leo",       degree: 15.0, house: 1,  retrograde: false },
        moon:    { planet: "Moon",      sign: "Scorpio",   degree: 22.5, house: 4,  retrograde: false },
        rising:  { planet: "Ascendant", sign: "Aquarius",  degree: 5.0,  house: 1,  retrograde: false },
        planets: [
          { planet: "Mercury", sign: "Leo",         degree: 8.0,  house: 1,  retrograde: false },
          { planet: "Venus",   sign: "Libra",       degree: 19.0, house: 3,  retrograde: false },
          { planet: "Mars",    sign: "Aries",       degree: 11.0, house: 7,  retrograde: false },
          { planet: "Jupiter", sign: "Sagittarius", degree: 27.0, house: 4,  retrograde: false },
          { planet: "Saturn",  sign: "Capricorn",   degree: 3.0,  house: 10, retrograde: true  },
        ],
        houses: [],
        aspects: [
          { planet1: "Sun", planet2: "Moon",    aspect: "Trine",   orb: 2.5 },
          { planet1: "Sun", planet2: "Jupiter", aspect: "Sextile", orb: 1.8 },
        ],
      });
    }
    finally { setLoading(false); }
  };

  const loadSigns = async () => {
    setLoading(true);
    try { setSigns(await astrology.signs()); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadHoroscope(selectedSign); }, [selectedSign]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Star className="w-7 h-7 text-amber-400" /> Astrology
        </h1>
        <p className="text-white/40 mt-1">Cosmic intelligence for your wellness journey.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/5 rounded-xl p-1">
        {(["horoscope", "chart", "signs"] as const).map((tab) => (
          <button key={tab} onClick={() => {
            setActiveTab(tab);
            if (tab === "chart" && !chart) loadChart();
            if (tab === "signs" && signs.length === 0) loadSigns();
          }}
            className={cn("flex-1 py-2 rounded-lg text-sm font-medium transition-all",
              activeTab === tab ? "bg-amber-600 text-white" : "text-white/40 hover:text-white")}>
            {tab === "horoscope" ? "Daily Horoscope" : tab === "chart" ? "Birth Chart" : "All Signs"}
          </button>
        ))}
      </div>

      {/* Horoscope */}
      {activeTab === "horoscope" && (
        <div className="space-y-5">
          {/* Sign picker */}
          <div className="flex gap-2 flex-wrap">
            {SIGNS.map((s) => (
              <button key={s} onClick={() => setSelectedSign(s)}
                className={cn("px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5",
                  selectedSign === s ? "bg-amber-600 text-white" : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10")}>
                <span>{SIGN_SYMBOLS[s]}</span>{s}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="glass rounded-2xl h-64 animate-pulse" />
          ) : horoscope ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl">{SIGN_SYMBOLS[horoscope.sign]}</span>
                      {horoscope.sign} — {horoscope.date}
                    </CardTitle>
                    <div className="flex gap-2">
                      <Badge variant="amber">Lucky #{horoscope.lucky_number}</Badge>
                      <Badge variant="default">{horoscope.lucky_color}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-white/80 leading-relaxed">{horoscope.general}</p>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  { label: "Love & Relationships", text: horoscope.love,   color: "rose"    as const },
                  { label: "Career & Purpose",     text: horoscope.career, color: "sky"     as const },
                  { label: "Health & Vitality",    text: horoscope.health, color: "emerald" as const },
                ].map(({ label, text, color }) => (
                  <Card key={label}>
                    <CardHeader><CardTitle className="text-sm">{label}</CardTitle></CardHeader>
                    <CardContent><p className="text-xs leading-relaxed">{text}</p></CardContent>
                  </Card>
                ))}
              </div>

              {/* Nexus cosmic insight */}
              <NexusInsight
                context="astrology"
                prompt={`I'm a ${horoscope.sign}. Today's horoscope says: "${horoscope.general}". Give me a deeper wellness interpretation — how should I align my nutrition, meditation, and energy practices with today's cosmic energy?`}
                accentClass="bg-amber-500/15 text-amber-400"
              />
            </div>
          ) : null}
        </div>
      )}

      {/* Birth Chart */}
      {activeTab === "chart" && (
        <div className="space-y-4">
          {loading ? (
            <div className="glass rounded-2xl h-64 animate-pulse" />
          ) : chart ? (
            <>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: "☀️ Sun",      pos: chart.sun    },
                  { label: "🌙 Moon",     pos: chart.moon   },
                  { label: "⬆️ Rising",   pos: chart.rising },
                ].map(({ label, pos }) => (
                  <Card key={label}>
                    <CardHeader><CardTitle className="text-sm">{label}</CardTitle></CardHeader>
                    <CardContent>
                      <p className="text-white text-lg font-bold">{pos.sign}</p>
                      <p className="text-white/40 text-xs">{pos.degree}°{pos.retrograde ? " ℞" : ""}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardHeader><CardTitle>Planetary Positions</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {chart.planets.map((p) => (
                      <div key={p.planet} className="flex items-center justify-between bg-white/5 rounded-lg px-3 py-2">
                        <span className="text-white/60 text-xs">{p.planet}</span>
                        <div className="text-right">
                          <span className="text-white text-xs font-medium">{p.sign}</span>
                          {p.retrograde && <span className="text-amber-400 text-xs ml-1">℞</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {chart.aspects.length > 0 && (
                <Card>
                  <CardHeader><CardTitle>Key Aspects</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {chart.aspects.map((a, i) => (
                        <div key={i} className="flex items-center gap-3 text-sm">
                          <span className="text-white/70">{a.planet1}</span>
                          <Badge variant="violet">{a.aspect}</Badge>
                          <span className="text-white/70">{a.planet2}</span>
                          <span className="text-white/30 text-xs ml-auto">{a.orb}° orb</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <NexusInsight
                context="astrology"
                prompt={`My birth chart: Sun in ${chart.sun.sign}, Moon in ${chart.moon.sign}, Rising in ${chart.rising.sign}. Give me a deep wellness interpretation of this combination — what are my natural strengths, challenges, and the best wellness practices for my chart?`}
                accentClass="bg-amber-500/15 text-amber-400"
              />
            </>
          ) : (
            <div className="text-center py-12 space-y-3">
              <Button onClick={loadChart}>
                <Sparkles className="w-4 h-4 mr-2" />Calculate My Birth Chart
              </Button>
              <p className="text-white/30 text-xs">Update your profile with birth details for accuracy</p>
            </div>
          )}
        </div>
      )}

      {/* All Signs */}
      {activeTab === "signs" && (
        <div className="space-y-4">
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {Array(12).fill(0).map((_, i) => <div key={i} className="glass rounded-2xl h-32 animate-pulse" />)}
            </div>
          ) : signs.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {signs.map((s) => (
                  <Card key={s.sign}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <span>{SIGN_SYMBOLS[s.sign]}</span>{s.sign}
                        </CardTitle>
                        <div className="flex gap-1">
                          <Badge variant="amber">{s.element}</Badge>
                          <Badge variant="default">{s.modality}</Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-white/50 text-xs mb-1">Body area: {s.body_area}</p>
                      <p className="text-white/60 text-xs leading-relaxed">{s.healing_focus}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
              <NexusInsight
                context="astrology"
                prompt="Give me a brief overview of how each zodiac sign relates to wellness — what are the key health themes and healing practices for each element (Fire, Earth, Air, Water)?"
                accentClass="bg-amber-500/15 text-amber-400"
                lazy
              />
            </>
          ) : (
            <div className="text-center py-12">
              <Button onClick={loadSigns}>Load All Signs</Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
