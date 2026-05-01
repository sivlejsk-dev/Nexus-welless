"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { astrology, meditation, detox, Horoscope, MeditationGuide, DetoxProtocol } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Brain, Leaf, Star, Droplets, Sparkles, Clock, Zap, ChefHat, Monitor, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const MODULE_CARDS = [
  { href: "/nexus",         label: "Nexus AI",      icon: Sparkles,  gradient: "from-violet-500 to-indigo-600",  glow: "shadow-violet-500/25",  desc: "AI wellness guidance"    },
  { href: "/meditation",    label: "Meditation",    icon: Brain,     gradient: "from-sky-500 to-blue-600",       glow: "shadow-sky-500/25",     desc: "Guided sessions"         },
  { href: "/nutrition",     label: "Nutrition",     icon: Leaf,      gradient: "from-emerald-500 to-teal-600",   glow: "shadow-emerald-500/25", desc: "Food as medicine"        },
  { href: "/plant-kitchen", label: "Plant Kitchen", icon: ChefHat,   gradient: "from-green-500 to-emerald-600",  glow: "shadow-green-500/25",   desc: "Plant-based recipes"     },
  { href: "/astrology",     label: "Astrology",     icon: Star,      gradient: "from-amber-500 to-orange-500",   glow: "shadow-amber-500/25",   desc: "Cosmic guidance"         },
  { href: "/detox",         label: "Detox",         icon: Droplets,  gradient: "from-cyan-500 to-sky-600",       glow: "shadow-cyan-500/25",    desc: "Cleanse protocols"       },
  { href: "/console",       label: "Console",       icon: Monitor,   gradient: "from-indigo-500 to-violet-600",  glow: "shadow-indigo-500/25",  desc: "Visual intelligence"     },
];

function SkeletonLine({ w = "full" }: { w?: string }) {
  return <div className={cn("skeleton h-3 rounded-full", `w-${w}`)} />;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [horoscope, setHoroscope] = useState<Horoscope | null>(null);
  const [guides, setGuides] = useState<MeditationGuide[]>([]);
  const [protocol, setProtocol] = useState<DetoxProtocol | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      meditation.guides({ category: "breathwork" }).then(g => setGuides(g.slice(0, 3))),
      detox.protocols("gentle").then(p => setProtocol(p[0] ?? null)),
      astrology.myHoroscope().then(setHoroscope).catch(() =>
        astrology.horoscope("Aries").then(setHoroscope).catch(() => {})),
    ]).finally(() => setLoaded(true));
  }, []);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  const name = user?.full_name?.split(" ")[0] ?? "Seeker";

  return (
    <div className="max-w-5xl mx-auto space-y-8 p-4 md:p-0 animate-fade-up">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-1">
          <div className="pulse-dot" />
          <span className="text-white/30 text-xs uppercase tracking-widest font-medium">Live session</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
          <span className="text-white">{greeting()}, </span>
          <span className="text-gradient">{name}</span>
        </h1>
        <p className="text-white/35 mt-1.5 text-sm">Your wellness intelligence is ready.</p>
      </div>

      {/* ── Module grid ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 stagger">
        {MODULE_CARDS.map(({ href, label, icon: Icon, gradient, glow, desc }) => (
          <Link key={href} href={href} className="animate-fade-up">
            <div className={cn(
              "glass-card p-4 cursor-pointer group h-full flex flex-col gap-3",
            )}>
              <div className={cn(
                "w-10 h-10 rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-lg flex-shrink-0 transition-transform duration-300 group-hover:scale-110",
                gradient, glow
              )}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <div className="min-w-0">
                <p className="text-white/90 font-semibold text-sm leading-tight">{label}</p>
                <p className="text-white/35 text-xs mt-0.5 leading-snug">{desc}</p>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-white/15 group-hover:text-white/40 group-hover:translate-x-0.5 transition-all mt-auto self-end" />
            </div>
          </Link>
        ))}
      </div>

      {/* ── Content row ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

        {/* Horoscope — spans 3 cols */}
        <div className="lg:col-span-3 glass-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-500/15 flex items-center justify-center">
                <Star className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <p className="text-white/90 font-semibold text-sm">Today's Cosmic Guidance</p>
                <p className="text-white/30 text-xs">{new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}</p>
              </div>
            </div>
            {horoscope && <Badge variant="amber" dot>{horoscope.sign}</Badge>}
          </div>

          {!loaded ? (
            <div className="space-y-2.5">
              <SkeletonLine /><SkeletonLine w="5/6" /><SkeletonLine w="4/6" />
            </div>
          ) : horoscope ? (
            <>
              <p className="text-white/70 text-sm leading-relaxed">{horoscope.general}</p>
              <div className="grid grid-cols-3 gap-2.5">
                {[
                  { label: "Love",   text: horoscope.love,   color: "text-rose-400",    bg: "bg-rose-500/8"    },
                  { label: "Career", text: horoscope.career, color: "text-sky-400",     bg: "bg-sky-500/8"     },
                  { label: "Health", text: horoscope.health, color: "text-emerald-400", bg: "bg-emerald-500/8" },
                ].map(({ label, text, color, bg }) => (
                  <div key={label} className={cn("rounded-xl p-3 border border-white/5", bg)}>
                    <p className={cn("text-xs font-semibold mb-1.5", color)}>{label}</p>
                    <p className="text-white/55 text-xs leading-relaxed truncate-2">{text}</p>
                  </div>
                ))}
              </div>
              <div className="flex gap-4 pt-2 border-t border-white/5">
                <span className="text-white/25 text-xs">Lucky #{horoscope.lucky_number}</span>
                <span className="text-white/25 text-xs">Color: {horoscope.lucky_color}</span>
              </div>
            </>
          ) : (
            <p className="text-white/25 text-sm">Cosmic data unavailable.</p>
          )}
        </div>

        {/* Right column — spans 2 cols */}
        <div className="lg:col-span-2 space-y-4">

          {/* Quick meditate */}
          <div className="glass-card p-4 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-xl bg-violet-500/15 flex items-center justify-center">
                <Brain className="w-3.5 h-3.5 text-violet-400" />
              </div>
              <p className="text-white/80 font-semibold text-sm">Quick Meditate</p>
            </div>
            <div className="space-y-1">
              {!loaded ? (
                [1,2,3].map(i => <div key={i} className="skeleton h-10 rounded-xl" />)
              ) : guides.length > 0 ? (
                guides.map(g => (
                  <Link key={g.id} href={`/meditation?guide=${g.id}`}>
                    <div className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-colors cursor-pointer group">
                      <div className="w-7 h-7 rounded-lg bg-violet-500/15 flex items-center justify-center flex-shrink-0">
                        <Clock className="w-3 h-3 text-violet-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-white/80 text-xs font-medium truncate">{g.title}</p>
                        <p className="text-white/30 text-xs">{g.duration_minutes} min</p>
                      </div>
                      <ArrowRight className="w-3 h-3 text-white/15 group-hover:text-white/40 flex-shrink-0 transition-colors" />
                    </div>
                  </Link>
                ))
              ) : null}
            </div>
            <Link href="/meditation">
              <Button variant="ghost" size="sm" className="w-full text-white/40 hover:text-white/70">
                All guides <ArrowRight className="w-3 h-3" />
              </Button>
            </Link>
          </div>

          {/* Featured detox */}
          {protocol && (
            <div className="glass-card p-4 space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-cyan-500/15 flex items-center justify-center">
                  <Zap className="w-3.5 h-3.5 text-cyan-400" />
                </div>
                <p className="text-white/80 font-semibold text-sm">Featured Detox</p>
              </div>
              <div>
                <p className="text-white/85 font-medium text-sm">{protocol.name}</p>
                <p className="text-white/40 text-xs mt-1 truncate-2">{protocol.description}</p>
              </div>
              <div className="flex gap-2 flex-wrap">
                <Badge variant="sky" dot>{protocol.duration_days} days</Badge>
                <Badge variant="default">{protocol.intensity}</Badge>
              </div>
              <Link href="/detox">
                <Button variant="secondary" size="sm" className="w-full">Start Protocol</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
