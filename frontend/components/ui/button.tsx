import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-all duration-200",
          "disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.97]",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 focus-visible:ring-offset-1 focus-visible:ring-offset-transparent",
          {
            // Primary — gradient with glow
            "bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-xl shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30 hover:from-violet-500 hover:to-indigo-500":
              variant === "primary",
            // Secondary — glass
            "glass-2 text-white/80 rounded-xl hover:text-white hover:border-white/20":
              variant === "secondary",
            // Ghost — transparent
            "text-white/50 rounded-xl hover:text-white hover:bg-white/6":
              variant === "ghost",
            // Danger
            "bg-rose-500/15 text-rose-400 border border-rose-500/25 rounded-xl hover:bg-rose-500/25":
              variant === "danger",
          },
          {
            "px-3 py-1.5 text-xs gap-1.5": size === "sm",
            "px-4 py-2.5 text-sm gap-2":   size === "md",
            "px-6 py-3 text-sm gap-2":     size === "lg",
          },
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
