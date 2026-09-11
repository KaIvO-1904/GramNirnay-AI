import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"
import { cn } from "@/lib/utils"

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex w-full touch-none select-none items-center group",
      className
    )}
    {...props}
  >
    <SliderPrimitive.Track
      className={cn(
        "relative h-1.5 w-full grow overflow-hidden rounded-full",
        "bg-[var(--surface-3)] transition-all duration-[var(--duration-base)]",
        "group-hover:bg-[var(--border)]"
      )}
    >
      <SliderPrimitive.Range
        className="absolute h-full rounded-full bg-[var(--accent)] transition-all duration-[var(--duration-base)]"
      />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb
      className={cn(
        "block h-4 w-4 rounded-full border-2 border-[var(--accent)] bg-[var(--surface-0)]",
        "shadow-[var(--shadow-sm)]",
        "transition-all duration-[var(--duration-base)]",
        "hover:scale-125 hover:shadow-[0_0_0_4px_rgba(26,86,219,0.15)]",
        "dark:hover:shadow-[0_0_0_4px_rgba(77,130,245,0.2)]",
        "focus-visible:outline-none",
        "focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2",
        "focus-visible:ring-offset-[var(--surface-0)]",
        "focus-visible:scale-125",
        "active:scale-110",
        "disabled:cursor-not-allowed disabled:opacity-50"
      )}
    />
  </SliderPrimitive.Root>
))
Slider.displayName = SliderPrimitive.Root.displayName

export { Slider }
