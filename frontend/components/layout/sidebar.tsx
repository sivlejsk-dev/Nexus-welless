"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import {
  LayoutDashboard,
  Brain,
  Leaf,
  Star,
  Droplets,
  Sparkles,
  LogOut,
  User,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/meditation", label: "Meditation", icon: Brain },
  { href: "/nutrition", label: "Nutrition", icon: Leaf },
  { href: "/astrology", label: "Astrology", icon: Star },
  { href: "/detox", label: "Detox", icon: Droplets },
  { href: "/nexus", label: "Nexus AI", icon: Sparkles },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-black/40 backdrop-blur-xl border-r border-white/10 flex flex-col z-40">
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

      {/* User footer */}
      <div className="p-4 border-t border-white/10">
        <Link
          href="/profile"
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-white/50 hover:text-white hover:bg-white/5 transition-all mb-1"
        >
          <User className="w-4 h-4" />
          <span className="truncate">{user?.full_name ?? user?.email ?? "Profile"}</span>
        </Link>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-white/40 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
