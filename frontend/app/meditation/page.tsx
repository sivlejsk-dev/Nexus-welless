"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { meditation, MeditationGuide } from "@/lib/api";
import { getFallbackMeditationGuides } from "@/lib/meditation-fallback";
import { Card } from "@/components/ui/card";
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

type VoiceSegment = { time: number; text: string; duration?: number };
type AmbientAudio = {
  audioCtx: AudioContext;
  oscillators: OscillatorNode[];
  gainNode: GainNode;
};
type WindowWithWebkitAudio = Window & typeof globalThis & {
  webkitAudioContext?: typeof AudioContext;
};

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
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ambientAudioRef = useRef<AmbientAudio | null>(null);
  const timeoutIds = useRef<number[]>([]);

  const clearScheduled = () => {
    timeoutIds.current.forEach((id) => window.clearTimeout(id));
    timeoutIds.current = [];
  };

  const stopAmbientFallback = () => {
    if (!ambientAudioRef.current) {
      return;
    }

    ambientAudioRef.current.oscillators.forEach((oscillator) => {
      try {
        oscillator.stop();
      } catch {
        // Oscillators may already be stopped during rapid session changes.
      }
    });
    ambientAudioRef.current.audioCtx.close().catch(() => undefined);
    ambientAudioRef.current = null;
  };

  const stopSession = () => {
    setIsPlaying(false);
    setActiveGuide(null);
    setCurrentSegment(null);
    clearScheduled();
    stopAmbientFallback();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.removeAttribute("src");
      audioRef.current.load();
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  };

  const createAmbientFallback = () => {
    const AudioContextCtor = window.AudioContext || (window as WindowWithWebkitAudio).webkitAudioContext;
    if (!AudioContextCtor) {
      return;
    }

    const audioCtx = new AudioContextCtor();
    const gainNode = audioCtx.createGain();
    gainNode.gain.setValueAtTime(0.045, audioCtx.currentTime);
    gainNode.connect(audioCtx.destination);

    const frequencies = [110, 165, 220];
    const oscillators = frequencies.map((frequency) => {
      const oscillator = audioCtx.createOscillator();
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime);
      oscillator.connect(gainNode);
      oscillator.start();
      return oscillator;
    });

    ambientAudioRef.current = { audioCtx, oscillators, gainNode };
  };

  const playBackgroundMusic = async (guide: MeditationGuide) => {
    stopAmbientFallback();

    if (!audioRef.current || !guide.background_music) {
      createAmbientFallback();
      return;
    }

    audioRef.current.src = guide.background_music;
    audioRef.current.loop = true;
    audioRef.current.volume = 0.35;

    try {
      await audioRef.current.play();
    } catch (err) {
      console.warn("Background music could not be played; using ambient fallback.", err);
      createAmbientFallback();
    }
  };

  const getVoiceSegments = (guide: MeditationGuide): VoiceSegment[] => {
    return guide.voice_guidance?.segments?.length
      ? guide.voice_guidance.segments
      : guide.script?.map((text, index) => ({ time: index * 5, text, duration: 4 })) ?? [];
  };

  const speakSegment = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.88;
    utterance.pitch = 1;
    utterance.volume = 1;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find((voice) =>
      /female|samantha|victoria|zira|english/i.test(`${voice.name} ${voice.lang}`),
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    window.speechSynthesis.resume();
    window.speechSynthesis.speak(utterance);
  };

  const playVoiceGuidance = (guide: MeditationGuide) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    const segments = getVoiceSegments(guide);

    if (segments.length === 0) {
      console.warn("No voice guidance segments available for guide:", guide.id);
      return;
    }

    clearScheduled();
    window.speechSynthesis.cancel();

    segments.forEach((segment, index) => {
      const playSegment = () => {
        setCurrentSegment(segment.text);
        speakSegment(segment.text);

        if (index === segments.length - 1) {
          const finishId = window.setTimeout(() => {
            stopSession();
          }, (segment.duration ?? 3) * 1000 + 500);
          timeoutIds.current.push(finishId);
        }
      };

      if (segment.time <= 0) {
        playSegment();
        return;
      }

      const id = window.setTimeout(playSegment, segment.time * 1000);
      timeoutIds.current.push(id);
    });
  };

  const startSession = (guide: MeditationGuide) => {
    stopSession();
    setActiveGuide(guide);
    setIsPlaying(true);
    setExpanded(guide.id);
    void playBackgroundMusic(guide);
    playVoiceGuidance(guide);
  };

  useEffect(() => {
    let cancelled = false;
    queueMicrotask(() => setLoading(true));
    const params = category !== "all" ? { category } : undefined;

    meditation.guides(params)
      .then((nextGuides) => {
        if (!cancelled) {
          setGuides(nextGuides);
        }
      })
      .catch(() => {
        console.warn("Meditation guides API unavailable; using local guides.");
        if (!cancelled) {
          setGuides(getFallbackMeditationGuides(params));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [category]);

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      clearScheduled();
      stopAmbientFallback();
      if (audio) {
        audio.pause();
        audio.removeAttribute("src");
        audio.load();
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <audio ref={audioRef} className="hidden" preload="auto" />

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
          {activeGuide && (
            <Card className="border border-white/10 p-4 bg-slate-950/60">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <p className="text-sm text-white/40">Now playing</p>
                  <p className="text-white font-semibold">{activeGuide.title}</p>
                  {currentSegment && <p className="text-white/70 mt-1">{currentSegment}</p>}
                </div>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" onClick={stopSession}>
                    Stop Session
                  </Button>
                </div>
              </div>
            </Card>
          )}
          {guides.map((guide) => {
            const guideSteps = guide.script?.length
              ? guide.script
              : getVoiceSegments(guide).map((segment) => segment.text);
            const canStartSession = guideSteps.length > 0 || Boolean(guide.background_music);

            return (
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
                {expanded === guide.id && canStartSession && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Guided Script</p>
                    {guideSteps.length > 0 && (
                      <ol className="space-y-2">
                        {guideSteps.map((step, i) => (
                          <li key={i} className="flex gap-3 text-sm text-white/70">
                            <span className="text-violet-400 font-mono text-xs mt-0.5 flex-shrink-0">
                              {String(i + 1).padStart(2, "0")}
                            </span>
                            {step}
                          </li>
                        ))}
                      </ol>
                    )}
                    <Button
                      className={guideSteps.length > 0 ? "mt-4" : ""}
                      size="sm"
                      onClick={() => startSession(guide)}
                    >
                      <Play className="w-3.5 h-3.5 mr-2" />
                      {isPlaying && activeGuide?.id === guide.id ? "Restart Session" : "Begin Session"}
                    </Button>
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
