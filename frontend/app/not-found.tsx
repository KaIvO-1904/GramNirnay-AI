'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}
    >
      {/* Background */}
      <div
        className="pointer-events-none fixed inset-0 opacity-25"
        aria-hidden="true"
        style={{
          backgroundImage: 'url(/media/grid-pattern.svg)',
          backgroundSize: '280px 280px',
          backgroundRepeat: 'repeat',
          color: 'var(--border)',
        }}
      />

      <div className="relative z-10 text-center max-w-lg">
        {/* 404 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <div
            className="text-[120px] md:text-[160px] font-black leading-none tracking-tighter select-none mb-2"
            style={{ color: 'var(--surface-3)' }}
          >
            404
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2
            className="text-2xl font-black uppercase tracking-tight mb-3"
            style={{ color: 'var(--text-primary)' }}
          >
            Page Not Found
          </h2>
          <p
            className="text-base leading-relaxed mb-10"
            style={{ color: 'var(--text-secondary)' }}
          >
            The page you&apos;re looking for doesn&apos;t exist or has been moved to a new location.
          </p>

          <Link href="/">
            <Button variant="primary" size="lg" className="gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              Return Home
            </Button>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
