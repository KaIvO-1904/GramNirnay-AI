import * as React from "react"
import { cn } from "@/lib/utils"

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-[var(--radius-md)] px-4 py-2.5 text-base",
          "bg-[var(--surface-0)] text-[var(--text-primary)]",
          "border border-[var(--border)]",
          "placeholder:text-[var(--text-muted)]",
          "transition-all duration-[var(--duration-base)]",
          "hover:border-[var(--border-strong)]",
          "focus-visible:outline-none focus-visible:border-[var(--border-focus)]",
          "focus-visible:ring-3 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-0",
          "focus-visible:shadow-[0_0_0_3px_rgba(26,86,219,0.12)]",
          "dark:focus-visible:shadow-[0_0_0_3px_rgba(77,130,245,0.15)]",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium",
          "disabled:cursor-not-allowed disabled:opacity-50",
          // Auto-fill styling reset
          "[&:-webkit-autofill]:bg-[var(--surface-0)]",
          "[&:-webkit-autofill]:text-[var(--text-primary)]",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
