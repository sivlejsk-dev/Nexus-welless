"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Brain, Leaf, Star, Droplets, Sparkles, ChefHat, Monitor,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard",     label: "Dashboard",     icon: LayoutDashboard, color: "text-violet-400" },
  { href: "/nexus",         label: "Nexus AI",      icon: Sparkles,        color: "text-violet-400" },
  { href: "/console",       label: "Console",       icon: Monitor,         color: "text-indigo-400" },
  { href: "/meditation",    label: "Meditation",    icon: Brain,           color: "text-sky-400"    },
  { href: "/nutrition",     label: "Nutrition",     icon: Leaf,            color: "text-emerald-400"},
  { href: "/plant-kitchen", label: "Plant Kitchen", icon: ChefHat,         color: "text-emerald-400"},
  { href: "/detox",         label: "Detox",         icon: Droplets,        color: "text-cyan-400"   },
  { href: "/astrology",     label: "Astrology",     icon: Star,            color: "text-amber-400"  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* ── Desktop sidebar ─────────────────────────────────────────────── */}
      <aside className="hidden md:flex fixed left-0 top-0 h-full w-60 flex-col z-40"
        style={{ background: "rgba(7,7,15,0.85)", backdropFilter: "blur(24px)", borderRight: "1px solid rgba(255,255,255,0.06)" }}>

        {/* Logo */}
        <div className="px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
              <Sparkles className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-base leading-none tracking-tight">Nexus</p>
              <p className="text-white/30 text-[11px] mt-0.5 tracking-wide uppercase">Wellness</p>
            </div>
          </div>
        </div>

        {/* Section label */}
        <p className="px-5 mb-2 text-[10px] font-semibold uppercase tracking-widest text-white/20">Navigation</p>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto scrollbar-none">
          {NAV_ITEMS.map(({ href, label, icon: Icon, color }) => {
            const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  active
                    ? "nav-active text-white"
                    : "text-white/40 hover:text-white/80 hover:bg-white/4"
                )}
              >
                <Icon className={cn("w-4 h-4 flex-shrink-0 transition-colors", active ? color : "group-hover:text-white/60")} />
                <span className="truncate">{label}</span>
                {active && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-violet-400 flex-shrink-0" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-white/5">
          <div className="flex items-center gap-2">
            <div className="pulse-dot flex-shrink-0" />
            <span className="text-white/30 text-xs">All systems operational</span>
          </div>
        </div>
      </aside>

      {/* ── Mobile bottom nav ───────────────────────────────────────────── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around px-1 py-2 safe-area-pb"
        style={{ background: "rgba(7,7,15,0.92)", backdropFilter: "blur(24px)", borderTop: "1px solid rgba(255,255,255,0.07)" }}>
        {NAV_ITEMS.map(({ href, label, icon: Icon, color }) => {
          const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl transition-all min-w-0",
                active ? "bg-white/6" : ""
              )}
            >
              <Icon className={cn("w-5 h-5 flex-shrink-0 transition-colors", active ? color : "text-white/30")} />
              <span className={cn("text-[9px] font-medium truncate transition-colors", active ? "text-white/80" : "text-white/30")}>
                {label}
              </span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}
