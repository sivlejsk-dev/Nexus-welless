import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "violet" | "emerald" | "amber" | "rose" | "sky";
  dot?: boolean;
}

export function Badge({ className, variant = "default", dot, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium tracking-wide",
        {
          "bg-white/8 text-white/60 border border-white/8":           variant === "default",
          "bg-violet-500/15 text-violet-300 border border-violet-500/20": variant === "violet",
          "bg-emerald-500/15 text-emerald-300 border border-emerald-500/20": variant === "emerald",
          "bg-amber-500/15 text-amber-300 border border-amber-500/20":   variant === "amber",
          "bg-rose-500/15 text-rose-300 border border-rose-500/20":     variant === "rose",
          "bg-sky-500/15 text-sky-300 border border-sky-500/20":       variant === "sky",
        },
        className
      )}
      {...props}
    >
      {dot && (
        <span className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0", {
          "bg-white/40":    variant === "default",
          "bg-violet-400":  variant === "violet",
          "bg-emerald-400": variant === "emerald",
          "bg-amber-400":   variant === "amber",
          "bg-rose-400":    variant === "rose",
          "bg-sky-400":     variant === "sky",
        })} />
      )}
      {children}
    </span>
  );
}
