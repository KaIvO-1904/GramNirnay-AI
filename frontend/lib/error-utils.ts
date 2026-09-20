'use client';

import { z } from 'zod';

export type ErrorSource = 'api' | 'validation' | 'system' | 'unknown';

export interface NormalizedError {
  message: string;
  source: ErrorSource;
  originalError: any;
}

/**
 * Normalizes various error formats into a human-readable string.
 * Prevents [object Object] from reaching the UI.
 */
export function normalizeError(error: any): string {
  if (!error) return 'An unexpected error occurred.';

  // 1. String: Return as is
  if (typeof error === 'string') return error;

  // 2. Error Object: Use message property
  if (error instanceof Error) return error.message;

  // 3. Object: Handle various common API error shapes
  if (typeof error === 'object') {
    // FastAPI / Standard API: { detail: "..." }
    if ('detail' in error && typeof error.detail === 'string') {
      return error.detail;
    }

    // FastAPI Validation: { detail: [ { msg: "...", loc: [...] }, ... ] }
    if ('detail' in error && Array.isArray(error.detail)) {
      return error.detail.map((d: any) => d.msg || 'Invalid input').join(', ');
    }

    // Standard API: { message: "..." }
    if ('message' in error && typeof error.message === 'string') {
      return error.message;
    }

    // Wrapped error: { error: { message: "..." } }
    if ('error' in error && typeof error.error === 'object' && error.error !== null) {
      return normalizeError(error.error);
    }

    // Generic object fallback: try to find any string value
    const values = Object.values(error);
    for (const val of values) {
      if (typeof val === 'string' && val.length > 0) return val;
    }
  }

  // 4. Final fallback: never return [object Object]
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Wraps an error for use in state or toasts, ensuring it's normalized.
 */
export function wrapError(error: any, source: ErrorSource = 'system'): NormalizedError {
  return {
    message: normalizeError(error),
    source,
    originalError: error,
  };
}
