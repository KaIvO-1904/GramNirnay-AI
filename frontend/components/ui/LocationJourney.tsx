'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, CheckCircle2, Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface LocationCandidate {
  provider_id: string;
  source: string;
  name: string;
  district: string;
  state: string;
  confidence: number;
}

interface LocationJourneyProps {
  onResolved: (location: any) => void;
  initialLocation?: any;
}

export default function LocationJourney({ onResolved, initialLocation }: LocationJourneyProps) {
  const [step, setStep] = useState<'detecting' | 'confirming' | 'resolving'>('detecting');
  const [candidates, setCandidates] = useState<LocationCandidate[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationCandidate | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    detectLocation();
  }, []);

  const detectLocation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (!navigator.geolocation) {
        throw new Error('Geolocation is not supported by your browser');
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            // In a real app, this would call the backend /api/location/gps
            // For now, we simulate the flow for the demo
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            // Simulated backend response
            const mockResolved = {
              provider_id: 'mock_1',
              source: 'GOOGLE',
              name: 'Ramanagara',
              district: 'Ramanagara',
              state: 'Karnataka',
              confidence: 0.95
            };

            setSelectedLocation(mockResolved);
            setStep('confirming');
          } catch (e: any) {
            setError('Failed to resolve coordinates.');
          } finally {
            setIsLoading(false);
          }
        },
        (err) => {
          setError('Location access denied. Please enter your district manually.');
          setStep('resolving');
          setIsLoading(false);
        }
      );
    } catch (e: any) {
      setError(e.message);
      setStep('resolving');
      setIsLoading(false);
    }
  };

  const handleConfirm = () => {
    if (selectedLocation) {
      onResolved(selectedLocation);
    }
  };

  const handleSelectCandidate = (candidate: LocationCandidate) => {
    setSelectedLocation(candidate);
    onResolved(candidate);
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xl relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500" />

      <div className="text-center mb-6">
        <div className="flex items-center justify-center gap-2 mb-2">
          <MapPin size={18} className="text-[var(--accent)]" />
          <h3 className="text-lg font-bold tracking-tight text-[var(--text-primary)]">Where is your venture?</h3>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">
          We need your location to find the best subsidies and local market data.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center gap-4">
        <AnimatePresence mode="wait">
          {step === 'detecting' && (
            <motion.div
              key="detecting"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4 py-8"
            >
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-4 border-t-[var(--accent)] animate-spin" />
                <MapPin size={20} className="absolute inset-0 m-auto text-[var(--accent)]" />
              </div>
              <span className="text-sm font-medium text-[var(--text-secondary)]">Detecting your location...</span>
            </motion.div>
          )}

          {step === 'confirming' && selectedLocation && (
            <motion.div
              key="confirming"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full space-y-6 text-center"
            >
              <div className="p-6 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)]">
                <div className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)] mb-2">Detected Location</div>
                <div className="text-2xl font-black text-[var(--text-primary)] mb-1">
                  {selectedLocation.district}, {selectedLocation.state}
                </div>
                <div className="text-sm text-[var(--text-secondary)]">Is this the correct area for your business?</div>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setStep('resolving')}
                  className="flex-1 rounded-xl h-11"
                >
                  No, change it
                </Button>
                <Button
                  variant="primary"
                  onClick={handleConfirm}
                  className="flex-1 rounded-xl h-11 bg-[var(--accent)] text-white font-bold gap-2"
                >
                  Yes, correct <CheckCircle2 size={16} />
                </Button>
              </div>
            </motion.div>
          )}

          {step === 'resolving' && (
            <motion.div
              key="resolving"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full space-y-4"
            >
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" size={18} />
                <input
                  type="text"
                  placeholder="Search for your district..."
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-[var(--surface-1)] border border-[var(--border)] text-[var(--text-primary)] outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all"
                  onChange={(e) => {
                    // Mock search results
                    if (e.target.value.length > 2) {
                      setCandidates([
                        { provider_id: '1', source: 'GOOGLE', name: 'District A', district: 'District A', state: 'State X', confidence: 0.9 },
                        { provider_id: '2', source: 'GOOGLE', name: 'District B', district: 'District B', state: 'State X', confidence: 0.7 },
                      ]);
                    } else {
                      setCandidates([]);
                    }
                  }}
                />
              </div>

              {error && <p className="text-xs text-red-500 text-center font-medium">{error}</p>}

              <div className="grid grid-cols-1 gap-2 max-h-60 overflow-y-auto pr-2">
                {candidates.map((c) => (
                  <button
                    key={c.provider_id}
                    onClick={() => handleSelectCandidate(c)}
                    className="flex items-center justify-between p-3 rounded-xl border bg-[var(--surface-0)] hover:border-[var(--accent)] transition-all text-left group"
                    style={{ borderColor: 'var(--border)' }}
                  >
                    <div>
                      <div className="text-sm font-bold text-[var(--text-primary)]">{c.district}</div>
                      <div className="text-xs text-[var(--text-muted)]">{c.state}</div>
                    </div>
                    <div className="text-[10px] font-mono text-[var(--text-muted)] group-hover:text-[var(--accent)]">
                      {Math.round(c.confidence * 100)}% Match
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
