'use client';

import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

/* Bezier tuple type for Framer Motion */
type Bezier = [number, number, number, number];
const EASE_OUT: Bezier = [0.16, 1, 0.3, 1];
const EASE_SPRING: Bezier = [0.34, 1.56, 0.64, 1];

/* ====================================================
   FADE IN
   Simple opacity entrance with optional y-offset
   ==================================================== */
interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
  style?: React.CSSProperties;
}

export function FadeIn({ children, delay = 0, duration = 0.5, y = 16, className, style }: FadeInProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration, delay, ease: EASE_OUT }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

/* ====================================================
   REVEAL
   Scroll-triggered entrance using IntersectionObserver
   ==================================================== */
interface RevealProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
  style?: React.CSSProperties;
  once?: boolean;
}

export function Reveal({ children, delay = 0, duration = 0.6, y = 24, className, style, once = true }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, margin: '-10% 0px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y }}
      transition={{ duration, delay, ease: EASE_OUT }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

/* ====================================================
   STAGGER
   Wraps children with staggered entrance
   ==================================================== */
interface StaggerProps {
  children: React.ReactNode;
  stagger?: number;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
  once?: boolean;
}

const staggerContainer = {
  hidden: {},
  visible: (stagger: number) => ({
    transition: { staggerChildren: stagger },
  }),
};

const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: EASE_OUT as Bezier },
  },
};

export function Stagger({ children, stagger = 0.08, delay = 0, className, style, once = true }: StaggerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, margin: '-10% 0px' });

  return (
    <motion.div
      ref={ref}
      className={className}
      style={style}
      variants={staggerContainer}
      custom={stagger}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      transition={{ delayChildren: delay }}
    >
      {React.Children.map(children, (child, i) => (
        <motion.div key={i} variants={staggerItem}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}

/* ====================================================
   HOVER LIFT
   Card elevation on hover
   ==================================================== */
interface HoverLiftProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  scale?: number;
  y?: number;
}

export function HoverLift({ children, className, style, scale = 1, y = -4 }: HoverLiftProps) {
  return (
    <motion.div
      className={className}
      style={style}
      whileHover={{ y, scale, transition: { duration: 0.2, ease: EASE_OUT as Bezier } }}
      whileTap={{ scale: 0.98, transition: { duration: 0.1 } }}
    >
      {children}
    </motion.div>
  );
}

/* ====================================================
   MAGNETIC BUTTON
   Subtle cursor-follow effect on primary CTAs
   ==================================================== */
interface MagneticButtonProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  strength?: number;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export function MagneticButton({
  children,
  className,
  style,
  strength = 0.25,
  ...rest
}: MagneticButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - rect.width / 2) * strength;
    const y = (e.clientY - rect.top - rect.height / 2) * strength;
    ref.current.style.transform = `translate(${x}px, ${y}px)`;
  };

  const handleMouseLeave = () => {
    if (!ref.current) return;
    ref.current.style.transform = 'translate(0, 0)';
    ref.current.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
  };

  return (
    <motion.button
      ref={ref}
      className={className}
      style={{ transition: 'transform 0.1s ease', ...style }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileTap={{ scale: 0.96 }}
      {...rest}
    >
      {children}
    </motion.button>
  );
}

/* ====================================================
   PAGE TRANSITION
   AnimatePresence wrapper for route transitions
   ==================================================== */
interface PageTransitionProps {
  children: React.ReactNode;
}

export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35, ease: EASE_OUT }}
    >
      {children}
    </motion.div>
  );
}

/* ====================================================
   SCALE IN
   Simple scale + fade entrance for modals/cards
   ==================================================== */
interface ScaleInProps {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
}

export function ScaleIn({ children, delay = 0, className, style }: ScaleInProps) {
  return (
    <motion.div
      className={className}
      style={style}
      initial={{ opacity: 0, scale: 0.94 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.45, delay, ease: EASE_SPRING }}
    >
      {children}
    </motion.div>
  );
}
