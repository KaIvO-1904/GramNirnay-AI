import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'danger'
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: [
        "bg-[var(--text-primary)] text-[var(--surface-0)]",
        "border border-[var(--text-primary)]",
      ].join(' '),
      secondary: [
        "bg-[var(--surface-2)] text-[var(--text-secondary)]",
        "border border-[var(--border)]",
      ].join(' '),
      outline: [
        "bg-transparent text-[var(--text-primary)]",
        "border border-[var(--border-strong)]",
      ].join(' '),
      success: [
        "bg-[var(--success-bg)] text-[var(--success)]",
        "border border-[var(--success-border)]",
      ].join(' '),
      warning: [
        "bg-[var(--warning-bg)] text-[var(--warning)]",
        "border border-[var(--warning-border)]",
      ].join(' '),
      danger: [
        "bg-[var(--danger-bg)] text-[var(--danger)]",
        "border border-[var(--danger-border)]",
      ].join(' '),
    }

    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
          "transition-colors duration-[var(--duration-fast)]",
          variants[variant],
          className
        )}
        {...props}
      />
    )
  }
)
Badge.displayName = "Badge"

export { Badge }
