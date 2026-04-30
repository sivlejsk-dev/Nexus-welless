"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Brain, Leaf, Star, Droplets, Sparkles, ChefHat, Monitor,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard",     label: "Dashboard",    icon: LayoutDashboard },
  { href: "/meditation",    label: "Meditation",   icon: Brain           },
  { href: "/nutrition",     label: "Nutrition",    icon: Leaf            },
  { href: "/astrology",     label: "Astrology",    icon: Star            },
  { href: "/detox",         label: "Detox",        icon: Droplets        },
  { href: "/plant-kitchen", label: "Plant Kitchen",icon: ChefHat         },
  { href: "/console",       label: "Console",      icon: Monitor         },
  { href: "/nexus",         label: "Nexus AI",     icon: Sparkles        },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* ── Desktop sidebar (hidden on mobile) ── */}
      <aside className="hidden md:flex fixed left-0 top-0 h-full w-64 bg-black/40 backdrop-blur-xl border-r border-white/10 flex-col z-40">
        {/* Logo */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-lg leading-none">Nexus</p>
              <p className="text-white/40 text-xs">Wellness Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  active
                    ? "bg-gradient-to-r from-violet-600/30 to-indigo-600/30 text-white border border-violet-500/30"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                )}
              >
                <Icon className={cn("w-4 h-4", active ? "text-violet-400" : "")} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* ── Mobile bottom nav (hidden on desktop) ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-t border-white/10 flex items-center justify-around px-2 py-2 safe-area-pb">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex flex-col items-center gap-0.5 px-2 py-1 rounded-xl transition-all min-w-0",
                active ? "text-violet-400" : "text-white/40"
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="text-[10px] font-medium truncate">{label}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}
