'use client';
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import LanguageSwitcher from '@/components/ui/LanguageSwitcher';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useApp } from '@/lib/AppContext';
import { User, LogIn, LayoutDashboard } from 'lucide-react';
import Image from 'next/image';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const { user, signInWithGoogle } = useApp();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div
        className="mx-auto px-4 sm:px-6 transition-all duration-[400ms] ease-[cubic-bezier(0.16,1,0.3,1)]"
        style={{
          maxWidth: '1280px',
        }}
      >
        <div
          className="mt-3 flex items-center justify-between px-4 sm:px-5 h-14 rounded-2xl transition-all duration-[400ms]"
          style={{
            backgroundColor: scrolled
              ? 'color-mix(in srgb, var(--surface-0) 88%, transparent)'
              : 'transparent',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: scrolled ? 'var(--border)' : 'transparent',
            backdropFilter: scrolled ? 'blur(16px)' : 'none',
            WebkitBackdropFilter: scrolled ? 'blur(16px)' : 'none',
            boxShadow: scrolled ? 'var(--shadow-md)' : 'none',
          }}
        >
          {/* Logo with Vibrant AI Gradient */}
          <Link href="/" className="group flex items-center gap-2.5 no-underline">
            <motion.div
              className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-black shadow-sm"
              style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)',
              }}
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            >
              G
            </motion.div>
            <span
              className="text-base font-extrabold tracking-tight transition-colors"
              style={{ color: 'var(--text-primary)' }}
            >
              GramNirnay<span className="ai-gradient-text font-black">.ai</span>
            </span>
          </Link>

          {/* Controls & User Account */}
          <div className="flex items-center gap-2 sm:gap-3">
            <LanguageSwitcher />
            <ThemeToggle />

            {/* Account Profile / Google Login */}
            {user ? (
              <Link
                href="/account"
                className="flex items-center gap-2 p-1 pl-2 pr-3 rounded-full border transition-all duration-200 hover:shadow-md"
                style={{
                  backgroundColor: 'var(--surface-1)',
                  borderColor: 'var(--border)',
                }}
              >
                <div className="relative w-6 h-6 rounded-full overflow-hidden border border-blue-400">
                  <Image
                    src={user.avatar}
                    alt={user.name}
                    fill
                    unoptimized
                    className="object-cover"
                  />
                </div>
                <span className="text-xs font-bold text-[var(--text-primary)] hidden sm:inline">
                  {user.name.split(' ')[0]}
                </span>
              </Link>
            ) : (
              <Link
                href="/account"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold transition-all duration-200 hover:scale-105 shadow-xs"
                style={{
                  backgroundColor: 'var(--surface-2)',
                  borderColor: 'var(--border)',
                  color: 'var(--text-primary)',
                }}
              >
                {/* Google "G" Icon */}
                <svg width="14" height="14" viewBox="0 0 24 24" className="shrink-0">
                  <path
                    fill="#4285F4"
                    d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17Z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.36 24 12 24Z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15Z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.36 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98Z"
                  />
                </svg>
                <span>Sign In</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.header>
  );
}
