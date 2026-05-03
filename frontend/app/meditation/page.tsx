"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { meditation, MeditationGuide } from "@/lib/api";
import { getFallbackMeditationGuides } from "@/lib/meditation-fallback";
import { NexusInsight } from "@/components/ui/nexus-insight";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Brain, Clock, Play, Square, ChevronDown, ChevronUp, CheckCircle2, Smile, Meh, Frown } from "lucide-react";
import { cn } from "@/lib/utils";

const CATEGORIES = ["all", "breathwork", "body-scan", "visualization", "mantra"];
const CATEGORY_COLORS: Record<string, "violet" | "emerald" | "amber" | "rose" | "sky"> = {
  breathwork: "sky", "body-scan": "emerald", visualization: "violet", mantra: "amber", sleep: "rose",
};

type VoiceSegment = { time: number; text: string; duration?: number };
type AmbientAudio = { audioCtx: AudioContext; oscillators: OscillatorNode[]; gainNode: GainNode };
type WindowWithWebkitAudio = Window & typeof globalThis & { webkitAudioContext?: typeof AudioContext };

function MoodPicker({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  const moods = [
    { v: 1, icon: Frown,  color: "text-rose-400",    bg: "bg-rose-500/15 border-rose-500/30"    },
    { v: 2, icon: Frown,  color: "text-orange-400",  bg: "bg-orange-500/15 border-orange-500/30"},
    { v: 3, icon: Meh,    color: "text-amber-400",   bg: "bg-amber-500/15 border-amber-500/30"  },
    { v: 4, icon: Smile,  color: "text-lime-400",    bg: "bg-lime-500/15 border-lime-500/30"    },
    { v: 5, icon: Smile,  color: "text-emerald-400", bg: "bg-emerald-500/15 border-emerald-500/30"},
  ];
  return (
    <div>
      <p className="text-white/40 text-xs mb-2">{label}</p>
      <div className="flex gap-2">
        {moods.map(({ v, icon: Icon, color, bg }) => (
          <button key={v} onClick={() => onChange(v)}
            className={cn("w-9 h-9 rounded-xl border flex items-center justify-center transition-all",
              value === v ? bg : "bg-white/5 border-white/10 hover:bg-white/10")}>
            <Icon className={cn("w-4 h-4", value === v ? color : "text-white/30")} />
          </button>
        ))}
      </div>
    </div>
  );
}

export default function MeditationPage() {
  return (
    <Suspense fallback={<div className="glass rounded-2xl h-24 animate-pulse" />}>
      <MeditationContent />
    </Suspense>
  );
}

function MeditationContent() {
  const searchParams = useSearchParams();
  const [guides, setGuides] = useState<MeditationGuide[]>([]);
  const [category, setCategory] = useState("all");
  const [expanded, setExpanded] = useState<string | null>(searchParams.get("guide"));
  const [loading, setLoading] = useState(true);
  const [activeGuide, setActiveGuide] = useState<MeditationGuide | null>(null);
  const [currentSegment, setCurrentSegment] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sessionDone, setSessionDone] = useState(false);
  const [moodBefore, setMoodBefore] = useState(3);
  const [moodAfter, setMoodAfter] = useState(3);
  const [logSaving, setLogSaving] = useState(false);
  const [logSaved, setLogSaved] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const sessionStartRef = useRef<number>(0);
  const timerRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ambientAudioRef = useRef<AmbientAudio | null>(null);
  const timeoutIds = useRef<number[]>([]);

  const clearScheduled = () => { timeoutIds.current.forEach((id) => window.clearTimeout(id)); timeoutIds.current = []; };

  const stopAmbientFallback = () => {
    if (!ambientAudioRef.current) return;
    ambientAudioRef.current.oscillators.forEach((o) => { try { o.stop(); } catch { /* already stopped */ } });
    ambientAudioRef.current.audioCtx.close().catch(() => undefined);
    ambientAudioRef.current = null;
  };

  const stopTimer = () => {
    if (timerRef.current) { window.clearInterval(timerRef.current); timerRef.current = null; }
  };

  const stopSession = useCallback((markDone = false) => {
    stopTimer();
    if (markDone && activeGuide) {
      setSessionSeconds(Math.round((Date.now() - sessionStartRef.current) / 1000));
      setSessionDone(true);
    } else {
      setSessionDone(false);
    }
    setIsPlaying(false);
    setCurrentSegment(null);
    clearScheduled();
    stopAmbientFallback();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.removeAttribute("src");
      audioRef.current.load();
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    if (!markDone) setActiveGuide(null);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeGuide]);

  const createAmbientFallback = () => {
    const AudioContextCtor = window.AudioContext || (window as WindowWithWebkitAudio).webkitAudioContext;
    if (!AudioContextCtor) return;
    const audioCtx = new AudioContextCtor();
    const gainNode = audioCtx.createGain();
    gainNode.gain.setValueAtTime(0.045, audioCtx.currentTime);
    gainNode.connect(audioCtx.destination);
    const oscillators = [110, 165, 220].map((freq) => {
      const osc = audioCtx.createOscillator();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      osc.connect(gainNode);
      osc.start();
      return osc;
    });
    ambientAudioRef.current = { audioCtx, oscillators, gainNode };
  };

  const playBackgroundMusic = async (guide: MeditationGuide) => {
    stopAmbientFallback();
    if (!audioRef.current || !guide.background_music) { createAmbientFallback(); return; }
    audioRef.current.src = guide.background_music;
    audioRef.current.loop = true;
    audioRef.current.volume = 0.35;
    try { await audioRef.current.play(); } catch { createAmbientFallback(); }
  };

  const getVoiceSegments = (guide: MeditationGuide): VoiceSegment[] =>
    guide.voice_guidance?.segments?.length
      ? guide.voice_guidance.segments
      : guide.script?.map((text, i) => ({ time: i * 5, text, duration: 4 })) ?? [];

  const speakSegment = (text: string) => {
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.88; utt.pitch = 1; utt.volume = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find((v) => /female|samantha|victoria|zira|english/i.test(`${v.name} ${v.lang}`));
    if (preferred) utt.voice = preferred;
    window.speechSynthesis.resume();
    window.speechSynthesis.speak(utt);
  };

  const playVoiceGuidance = (guide: MeditationGuide) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const segments = getVoiceSegments(guide);
    if (!segments.length) return;
    clearScheduled();
    window.speechSynthesis.cancel();
    segments.forEach((seg, i) => {
      const play = () => {
        setCurrentSegment(seg.text);
        speakSegment(seg.text);
        if (i === segments.length - 1) {
          const id = window.setTimeout(() => stopSession(true), (seg.duration ?? 3) * 1000 + 500);
          timeoutIds.current.push(id);
        }
      };
      if (seg.time <= 0) { play(); return; }
      const id = window.setTimeout(play, seg.time * 1000);
      timeoutIds.current.push(id);
    });
  };

  const startSession = (guide: MeditationGuide) => {
    stopSession(false);
    setSessionDone(false);
    setLogSaved(false);
    setActiveGuide(guide);
    setIsPlaying(true);
    setExpanded(guide.id);
    sessionStartRef.current = Date.now();
    timerRef.current = window.setInterval(() => {
      setSessionSeconds(Math.round((Date.now() - sessionStartRef.current) / 1000));
    }, 1000);
    void playBackgroundMusic(guide);
    playVoiceGuidance(guide);
  };

  const logSession = async () => {
    if (!activeGuide) return;
    setLogSaving(true);
    try {
      await meditation.logSession({
        guide_id: activeGuide.id,
        duration_seconds: sessionSeconds,
        completed: true,
        mood_before: moodBefore,
        mood_after: moodAfter,
      });
      setLogSaved(true);
    } catch { /* non-critical */ } finally {
      setLogSaving(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const params = category !== "all" ? { category } : undefined;
    meditation.guides(params)
      .then((g) => { if (!cancelled) setGuides(g); })
      .catch(() => { if (!cancelled) setGuides(getFallbackMeditationGuides(params)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [category]);

  useEffect(() => {
    return () => {
      stopTimer();
      clearScheduled();
      stopAmbientFallback();
      if (audioRef.current) { audioRef.current.pause(); audioRef.current.removeAttribute("src"); audioRef.current.load(); }
      if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatTime = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <audio ref={audioRef} className="hidden" preload="auto" />

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Brain className="w-7 h-7 text-violet-400" /> Meditation
          </h1>
          <p className="text-white/40 mt-1">Guided sessions for every state of mind.</p>
        </div>
      </div>

      <NexusInsight
        context="meditation"
        prompt="Give me a brief, personalised meditation insight for today — what practice would most benefit my mind and nervous system right now?"
        accentClass="bg-violet-500/15 text-violet-400"
      />

      {isPlaying && activeGuide && (
        <div className="glass-card p-4 border border-violet-500/20 bg-violet-500/5">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-violet-400 animate-pulse flex-shrink-0" />
              <div>
                <p className="text-white font-semibold text-sm">{activeGuide.title}</p>
                {currentSegment && <p className="text-white/60 text-xs mt-0.5 max-w-xs truncate">{currentSegment}</p>}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-violet-300 font-mono text-sm">{formatTime(sessionSeconds)}</span>
              <Button variant="danger" size="sm" onClick={() => stopSession(true)}>
                <Square className="w-3 h-3 mr-1.5" /> End
              </Button>
            </div>
          </div>
        </div>
      )}

      {sessionDone && activeGuide && !logSaved && (
        <div className="glass-card p-5 border border-emerald-500/20 bg-emerald-500/5 space-y-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <p className="text-white font-semibold">Session complete — {formatTime(sessionSeconds)}</p>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <MoodPicker label="Mood before" value={moodBefore} onChange={setMoodBefore} />
            <MoodPicker label="Mood after" value={moodAfter} onChange={setMoodAfter} />
          </div>
          <Button onClick={logSession} disabled={logSaving} size="sm">
            {logSaving ? "Saving…" : "Log Session"}
          </Button>
        </div>
      )}
      {sessionDone && logSaved && (
        <div className="glass-card p-4 border border-emerald-500/20 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <p className="text-emerald-300 text-sm">Session logged. Great work.</p>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map((c) => (
          <button key={c} onClick={() => setCategory(c)}
            className={cn("px-4 py-1.5 rounded-full text-sm font-medium transition-all",
              category === c ? "bg-violet-600 text-white" : "bg-white/5 text-white/50 hover:text-white hover:bg-white/10")}>
            {c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid gap-4">{[1,2,3].map((i) => <div key={i} className="glass rounded-2xl h-24 animate-pulse" />)}</div>
      ) : (
        <div className="space-y-3">
          {guides.map((guide) => {
            const segments = getVoiceSegments(guide);
            const canStart = segments.length > 0 || Boolean(guide.background_music);
            const isActive = activeGuide?.id === guide.id;
            return (
              <Card key={guide.id} className={cn("cursor-pointer transition-all", isActive && "border-violet-500/30 bg-violet-500/5")}>
                <div className="flex items-start gap-4" onClick={() => setExpanded(expanded === guide.id ? null : guide.id)}>
                  <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0", isActive ? "bg-violet-500/30" : "bg-violet-500/15")}>
                    <Brain className={cn("w-5 h-5", isActive ? "text-violet-300" : "text-violet-400")} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-white font-semibold">{guide.title}</h3>
                        <p className="text-white/50 text-sm mt-0.5 line-clamp-1">{guide.description}</p>
                      </div>
                      {expanded === guide.id ? <ChevronUp className="w-4 h-4 text-white/30 flex-shrink-0 mt-1" /> : <ChevronDown className="w-4 h-4 text-white/30 flex-shrink-0 mt-1" />}
                    </div>
                    <div className="flex gap-2 mt-2 flex-wrap">
                      <Badge variant={CATEGORY_COLORS[guide.category] ?? "default"}>{guide.category}</Badge>
                      <Badge variant="default"><Clock className="w-3 h-3 mr-1" />{guide.duration_minutes} min</Badge>
                      <Badge variant="default">{guide.level}</Badge>
                      {guide.tags.slice(0, 2).map((t) => <Badge key={t} variant="default">{t}</Badge>)}
                    </div>
                  </div>
                </div>
                {expanded === guide.id && (
                  <div className="mt-4 pt-4 border-t border-white/10 space-y-4">
                    {segments.length > 0 && (
                      <div>
                        <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Guided Script</p>
                        <ol className="space-y-2">
                          {segments.slice(0, 6).map((seg, i) => (
                            <li key={i} className="flex gap-3 text-sm text-white/70">
                              <span className="text-violet-400 font-mono text-xs mt-0.5 flex-shrink-0">{String(i + 1).padStart(2, "0")}</span>
                              {seg.text}
                            </li>
                          ))}
                          {segments.length > 6 && <li className="text-white/30 text-xs pl-8">+{segments.length - 6} more segments…</li>}
                        </ol>
                      </div>
                    )}
                    {canStart && (
                      <Button size="sm" onClick={() => startSession(guide)}>
                        <Play className="w-3.5 h-3.5 mr-2" />
                        {isPlaying && isActive ? "Restart Session" : "Begin Session"}
                      </Button>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
