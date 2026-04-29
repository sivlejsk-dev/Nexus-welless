"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { astrology, meditation, detox, Horoscope, MeditationGuide, DetoxProtocol } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Brain, Leaf, Star, Droplets, Sparkles, Clock, Zap } from "lucide-react";

const MODULE_CARDS = [
  { href: "/meditation", label: "Meditation", icon: Brain, color: "from-violet-500 to-purple-600", desc: "Guided sessions & breathwork" },
  { href: "/nutrition", label: "Nutrition", icon: Leaf, color: "from-emerald-500 to-teal-600", desc: "Food as medicine" },
  { href: "/astrology", label: "Astrology", icon: Star, color: "from-amber-500 to-orange-600", desc: "Birth charts & horoscopes" },
  { href: "/detox", label: "Detox", icon: Droplets, color: "from-sky-500 to-blue-600", desc: "Cleanse protocols" },
  { href: "/nexus", label: "Nexus AI", icon: Sparkles, color: "from-rose-500 to-pink-600", desc: "Personalized AI guidance" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [horoscope, setHoroscope] = useState<Horoscope | null>(null);
  const [guides, setGuides] = useState<MeditationGuide[]>([]);
  const [protocol, setProtocol] = useState<DetoxProtocol | null>(null);

  useEffect(() => {
    meditation.guides({ category: "breathwork" }).then((g) => setGuides(g.slice(0, 2))).catch(() => {});
    detox.protocols("gentle").then((p) => setProtocol(p[0] ?? null)).catch(() => {});
    // Horoscope requires auth — try after mount
    astrology.myHoroscope().then(setHoroscope).catch(() => {
      astrology.horoscope("Aries").then(setHoroscope).catch(() => {});
    });
  }, []);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">
          {greeting()}, {user?.full_name?.split(" ")[0] ?? "Seeker"} ✦
        </h1>
        <p className="text-white/40 mt-1">Your daily wellness journey awaits.</p>
      </div>

      {/* Module grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {MODULE_CARDS.map(({ href, label, icon: Icon, color, desc }) => (
          <Link key={href} href={href}>
            <div className="glass rounded-2xl p-5 hover:bg-white/8 transition-all duration-200 cursor-pointer group h-full">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <p className="text-white font-semibold text-sm">{label}</p>
              <p className="text-white/40 text-xs mt-0.5">{desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Horoscope */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-amber-400" />
                  Today&apos;s Cosmic Guidance
                </CardTitle>
                {horoscope && <Badge variant="amber">{horoscope.sign}</Badge>}
              </div>
            </CardHeader>
            <CardContent>
              {horoscope ? (
                <div className="space-y-3">
                  <p className="text-white/80 leading-relaxed">{horoscope.general}</p>
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    {[
                      { label: "Love", text: horoscope.love },
                      { label: "Career", text: horoscope.career },
                      { label: "Health", text: horoscope.health },
                    ].map(({ label, text }) => (
                      <div key={label} className="bg-white/5 rounded-xl p-3">
                        <p className="text-white/40 text-xs mb-1">{label}</p>
                        <p className="text-white/70 text-xs leading-relaxed line-clamp-3">{text}</p>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-4 mt-2 pt-3 border-t border-white/5">
                    <span className="text-white/40 text-xs">Lucky #{horoscope.lucky_number}</span>
                    <span className="text-white/40 text-xs">Color: {horoscope.lucky_color}</span>
                  </div>
                </div>
              ) : (
                <p className="text-white/30 text-sm">Loading cosmic data…</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Brain className="w-4 h-4 text-violet-400" />
                Quick Meditate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {guides.map((g) => (
                  <Link key={g.id} href={`/meditation?guide=${g.id}`}>
                    <div className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
                      <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                        <Clock className="w-3.5 h-3.5 text-violet-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-white text-xs font-medium truncate">{g.title}</p>
                        <p className="text-white/40 text-xs">{g.duration_minutes} min</p>
                      </div>
                    </div>
                  </Link>
                ))}
                <Link href="/meditation">
                  <Button variant="ghost" size="sm" className="w-full mt-1">View all guides →</Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {protocol && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Zap className="w-4 h-4 text-sky-400" />
                  Featured Detox
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-white font-medium text-sm">{protocol.name}</p>
                <p className="text-white/50 text-xs mt-1 line-clamp-2">{protocol.description}</p>
                <div className="flex gap-2 mt-3">
                  <Badge variant="sky">{protocol.duration_days} days</Badge>
                  <Badge variant="default">{protocol.intensity}</Badge>
                </div>
                <Link href="/detox">
                  <Button variant="secondary" size="sm" className="w-full mt-3">Start Protocol</Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
