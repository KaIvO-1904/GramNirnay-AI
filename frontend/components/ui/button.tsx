import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';

    const variants = {
      primary: [
        "bg-[var(--accent)] text-white border border-[var(--accent)]",
        "hover:bg-[var(--accent-hover)] hover:border-[var(--accent-hover)]",
        "hover:shadow-[0_4px_16px_rgba(26,86,219,0.3)]",
        "dark:hover:shadow-[0_4px_16px_rgba(77,130,245,0.25)]",
        "focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2",
        "focus-visible:ring-offset-[var(--surface-0)]",
      ].join(' '),
      secondary: [
        "bg-[var(--surface-2)] text-[var(--text-primary)] border border-[var(--border)]",
        "hover:bg-[var(--surface-3)] hover:border-[var(--border-strong)]",
        "hover:shadow-[var(--shadow-sm)]",
      ].join(' '),
      outline: [
        "bg-transparent text-[var(--text-primary)] border border-[var(--border-strong)]",
        "hover:bg-[var(--surface-2)] hover:border-[var(--border-strong)]",
        "hover:shadow-[var(--shadow-sm)]",
      ].join(' '),
      ghost: [
        "bg-transparent text-[var(--text-secondary)] border border-transparent",
        "hover:bg-[var(--surface-2)] hover:text-[var(--text-primary)]",
      ].join(' '),
      danger: [
        "bg-[var(--danger)] text-white border border-[var(--danger)]",
        "hover:opacity-90 hover:shadow-[0_4px_12px_rgba(192,57,43,0.3)]",
      ].join(' '),
    }

    const sizes = {
      sm: "px-3.5 py-2 text-sm h-8",
      md: "px-5 py-2.5 text-sm h-10",
      lg: "px-7 py-3 text-base h-12",
      icon: "p-2 h-9 w-9",
    }

    return (
      <Comp
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-semibold rounded-[var(--radius-full)]",
          "transition-all duration-[var(--duration-base)]",
          "active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
          "select-none whitespace-nowrap",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
