import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "violet" | "emerald" | "amber" | "rose" | "sky";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        {
          "bg-white/10 text-white/70": variant === "default",
          "bg-violet-500/20 text-violet-300": variant === "violet",
          "bg-emerald-500/20 text-emerald-300": variant === "emerald",
          "bg-amber-500/20 text-amber-300": variant === "amber",
          "bg-rose-500/20 text-rose-300": variant === "rose",
          "bg-sky-500/20 text-sky-300": variant === "sky",
        },
        className
      )}
      {...props}
    />
  );
}
