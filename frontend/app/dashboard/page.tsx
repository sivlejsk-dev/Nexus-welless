"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { astrology, meditation, detox, nexus, Horoscope, MeditationGuide, DetoxProtocol } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Brain, Leaf, Star, Droplets, Sparkles, Clock, Zap, ChefHat,
  Monitor, ArrowRight, User, LogOut, RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

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
  const { user, logout } = useAuth();
  const router = useRouter();
  const [horoscope, setHoroscope] = useState<Horoscope | null>(null);
  const [guides, setGuides] = useState<MeditationGuide[]>([]);
  const [protocol, setProtocol] = useState<DetoxProtocol | null>(null);
  const [nexusGreeting, setNexusGreeting] = useState<string | null>(null);
  const [greetingLoading, setGreetingLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [greeting, setGreeting] = useState("Good day");

  useEffect(() => {
    const h = new Date().getHours();
    setGreeting(h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening");
  }, []);

  useEffect(() => {
    Promise.allSettled([
      meditation.guides({ category: "breathwork" }).then((g) => setGuides(g.slice(0, 3))),
      detox.protocols("gentle").then((p) => setProtocol(p[0] ?? null)),
      astrology.myHoroscope().then(setHoroscope).catch(() =>
        astrology.horoscope("Aries").then(setHoroscope).catch(() => {})),
    ]).finally(() => setLoaded(true));
  }, []);

  useEffect(() => {
    const name = user?.full_name?.split(" ")[0] ?? "Seeker";
    nexus.chat(`Give me a single uplifting, personalised wellness greeting for ${name} to start their day. Keep it to 2 sentences max. Be warm, specific, and motivating.`)
      .then((r) => setNexusGreeting(r.response))
      .catch(() => setNexusGreeting(null))
      .finally(() => setGreetingLoading(false));
  }, [user]);

  const refreshGreeting = () => {
    setGreetingLoading(true);
    setNexusGreeting(null);
    const name = user?.full_name?.split(" ")[0] ?? "Seeker";
    nexus.chat(`Give me a fresh, different uplifting wellness greeting for ${name}. 2 sentences, warm and specific.`)
      .then((r) => setNexusGreeting(r.response))
      .catch(() => setNexusGreeting(null))
      .finally(() => setGreetingLoading(false));
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const name = user?.full_name?.split(" ")[0] ?? "Seeker";

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-up">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="pt-2 flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="pulse-dot" />
            <span className="text-white/30 text-xs uppercase tracking-widest font-medium">Live session</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            <span className="text-white">{greeting}, </span>
            <span className="text-gradient">{name}</span>
          </h1>
          <p className="text-white/35 mt-1.5 text-sm">Your wellness intelligence is ready.</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Link href="/profile">
            <button className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/40 hover:text-white/80 transition-all" title="Profile">
              <User className="w-4 h-4" />
            </button>
          </Link>
          <button onClick={handleLogout} className="p-2.5 rounded-xl bg-white/5 hover:bg-rose-500/15 text-white/40 hover:text-rose-400 transition-all" title="Sign out">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Nexus daily greeting ─────────────────────────────────────────── */}
      <div className="glass-card p-5 border border-violet-500/15 bg-gradient-to-r from-violet-500/5 to-indigo-500/5">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-violet-500/30 mt-0.5">
            <Sparkles className="w-4.5 h-4.5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-2">
              <p className="text-white/50 text-xs font-semibold uppercase tracking-widest">Nexus · Daily Insight</p>
              <button onClick={refreshGreeting} disabled={greetingLoading}
                className="p-1 rounded-lg text-white/25 hover:text-white/60 hover:bg-white/5 transition-all disabled:opacity-30">
                <RefreshCw className={cn("w-3.5 h-3.5", greetingLoading && "animate-spin")} />
              </button>
            </div>
            {greetingLoading ? (
              <div className="space-y-2">
                <SkeletonLine /><SkeletonLine w="4/5" />
              </div>
            ) : nexusGreeting ? (
              <p className="text-white/80 text-sm leading-relaxed">{nexusGreeting}</p>
            ) : (
              <p className="text-white/40 text-sm">Your wellness intelligence is standing by. Ask Nexus anything.</p>
            )}
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-white/5 flex gap-2">
          <Link href="/nexus" className="flex-1">
            <Button variant="secondary" size="sm" className="w-full">
              <Sparkles className="w-3.5 h-3.5" /> Chat with Nexus
            </Button>
          </Link>
          <Link href="/console" className="flex-1">
            <Button variant="ghost" size="sm" className="w-full">
              <Monitor className="w-3.5 h-3.5" /> Open Console
            </Button>
          </Link>
        </div>
      </div>

      {/* ── Module grid ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 stagger">
        {MODULE_CARDS.map(({ href, label, icon: Icon, gradient, glow, desc }) => (
          <Link key={href} href={href} className="animate-fade-up">
            <div className="glass-card p-4 cursor-pointer group h-full flex flex-col gap-3">
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

        {/* Horoscope */}
        <div className="lg:col-span-3 glass-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-500/15 flex items-center justify-center">
                <Star className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <p className="text-white/90 font-semibold text-sm">Today&apos;s Cosmic Guidance</p>
                <p className="text-white/30 text-xs">{new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}</p>
              </div>
            </div>
            {horoscope && <Badge variant="amber" dot>{horoscope.sign}</Badge>}
          </div>

          {!loaded ? (
            <div className="space-y-2.5"><SkeletonLine /><SkeletonLine w="5/6" /><SkeletonLine w="4/6" /></div>
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
                    <p className="text-white/55 text-xs leading-relaxed line-clamp-3">{text}</p>
                  </div>
                ))}
              </div>
              <div className="flex gap-4 pt-2 border-t border-white/5 items-center justify-between">
                <div className="flex gap-4">
                  <span className="text-white/25 text-xs">Lucky #{horoscope.lucky_number}</span>
                  <span className="text-white/25 text-xs">Color: {horoscope.lucky_color}</span>
                </div>
                <Link href="/astrology">
                  <button className="text-amber-400/60 hover:text-amber-400 text-xs flex items-center gap-1 transition-colors">
                    Full reading <ArrowRight className="w-3 h-3" />
                  </button>
                </Link>
              </div>
            </>
          ) : (
            <p className="text-white/25 text-sm">Cosmic data unavailable.</p>
          )}
        </div>

        {/* Right column */}
        <div className="lg:col-span-2 space-y-4">

          {/* Quick meditate */}
          <div className="glass-card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-violet-500/15 flex items-center justify-center">
                  <Brain className="w-3.5 h-3.5 text-violet-400" />
                </div>
                <p className="text-white/80 font-semibold text-sm">Quick Meditate</p>
              </div>
              <Link href="/meditation">
                <button className="text-white/25 hover:text-white/60 transition-colors">
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </Link>
            </div>
            <div className="space-y-1">
              {!loaded ? (
                [1,2,3].map((i) => <div key={i} className="skeleton h-10 rounded-xl" />)
              ) : guides.length > 0 ? (
                guides.map((g) => (
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
          </div>

          {/* Featured detox */}
          {protocol && (
            <div className="glass-card p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-xl bg-cyan-500/15 flex items-center justify-center">
                    <Zap className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                  <p className="text-white/80 font-semibold text-sm">Featured Detox</p>
                </div>
                <Link href="/detox">
                  <button className="text-white/25 hover:text-white/60 transition-colors">
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </Link>
              </div>
              <div>
                <p className="text-white/85 font-medium text-sm">{protocol.name}</p>
                <p className="text-white/40 text-xs mt-1 line-clamp-2">{protocol.description}</p>
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
