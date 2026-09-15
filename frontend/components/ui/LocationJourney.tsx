'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, CheckCircle2, Search, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { searchLocation, resolveLocation, resolveGps } from '@/lib/api';
import { LocationCandidate, LocationIdentity, Place } from '@/types';

interface LocationJourneyProps {
  onResolved: (location: LocationIdentity) => void;
  initialLocation?: any;
}

export default function LocationJourney({ onResolved, initialLocation }: LocationJourneyProps) {
  const [step, setStep] = useState<'detecting' | 'confirming' | 'resolving'>('detecting');
  const [candidates, setCandidates] = useState<LocationCandidate[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationCandidate | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    detectLocation();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.length >= 3) {
        handleSearch(searchQuery);
      } else {
        setCandidates([]);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

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
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            const resolved = await resolveGps(lat, lng);

            // Adapt LocationIdentity to LocationCandidate for the confirmation UI
            const candidate: LocationCandidate = {
              provider_id: resolved.provider_id,
              label: resolved.name,
              hierarchy: {
                state: resolved.state,
                district: resolved.district,
                village: resolved.name,
              },
              lat: resolved.coordinates.lat,
              lng: resolved.coordinates.lng,
              confidence: 1.0,
            };

            setSelectedLocation(candidate);
            setStep('confirming');
          } catch (e: any) {
            setError('Failed to resolve coordinates. Please search manually.');
            setStep('resolving');
          } finally {
            setIsLoading(false);
          }
        },
        (err) => {
          if (err.code === 1) {
            setError('Location access denied. Please enter your district manually.');
          } else if (err.code === 3) {
            setError('Location request timed out. Please search manually.');
          } else {
            setError('Unable to retrieve location. Please search manually.');
          }
          setStep('resolving');
          setIsLoading(false);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    } catch (e: unknown) {
      const error = e as Error;
      setError(error.message);
      setStep('resolving');
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!selectedLocation) return;
    setIsLoading(true);
    try {
      try {
        const finalLoc = await resolveLocation(selectedLocation.provider_id, 'gps');
        onResolved(finalLoc);
      } catch (resolveErr) {
        console.warn('Canonical resolution failed, using detected location as fallback:', resolveErr);
        onResolved({
          provider_id: selectedLocation.provider_id,
          name: selectedLocation.label,
          district: selectedLocation.hierarchy.district,
          state: selectedLocation.hierarchy.state,
          country: 'India',
          coordinates: { lat: selectedLocation.lat, lng: selectedLocation.lng },
          source: 'gps',
        });
      }
    } catch (e: any) {
      setError('Failed to confirm location. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCandidate = async (candidate: LocationCandidate) => {
    setSelectedLocation(candidate);
    setIsLoading(true);
    try {
      try {
        const finalLoc = await resolveLocation(candidate.provider_id, 'manual');
        onResolved(finalLoc);
      } catch (resolveErr) {
        console.warn('Canonical resolution failed, using candidate data as fallback:', resolveErr);
        onResolved({
          provider_id: candidate.provider_id,
          name: candidate.label,
          district: candidate.hierarchy.district,
          state: candidate.hierarchy.state,
          country: 'India',
          coordinates: { lat: candidate.lat, lng: candidate.lng },
          source: 'manual',
        });
      }
    } catch (e: any) {
      setError('Failed to resolve selected location.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    try {
      const results = await searchLocation(query);
      setCandidates(results);
    } catch (e: any) {
      setError('Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xl relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500" />

      <div className="text-center mb-6">
        <div className="flex items-center justify-center gap-2 mb-2">
          <MapPin size={18} className="text-[var(--accent)]" />
          <h3 className="text-lg font-bold tracking-tight text-[var(--text-primary]">Where is your venture?</h3>
        </div >
        <p className="text-sm text-[var(--text-secondary)]">
          We need your location to find the best subsidies and local market data.
        </p>
      </div >

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
              </div >
              <span className="text-sm font-medium text-[var(--text-secondary)]">Detecting your location...</span>
              <Button
                variant="ghost"
                onClick={() => setStep('resolving')}
                className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] underline underline-offset-4"
              >
                Search Manually
              </Button>
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
                <div className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)] mb-2">Detected Location</div >
                <div className="text-2xl font-black text-[var(--text-primary)] mb-1">
                  {selectedLocation.hierarchy.district}, {selectedLocation.hierarchy.state}
                </div >
                <div className="text-sm text-[var(--text-secondary)]">Is this the correct area for your business?</div>
              </div >
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
                  {isLoading ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                  {isLoading ? 'Resolving...' : 'Yes, correct'}
                </Button>
              </div >
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
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div >
              {error && <p className="text-xs text-red-500 text-center font-medium">{error}</p>}
              <div className="grid grid-cols-1 gap-2 max-h-60 overflow-y-auto pr-2">
                {isLoading && candidates.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-[var(--text-muted)]">
                    <Loader2 size={24} className="animate-spin mb-2" />
                    <span className="text-xs">Searching for locations...</span>
                  </div >
                ) : candidates.length > 0 ? (
                  candidates.map((c) => (
                    <button
                      key={c.provider_id}
                      onClick={() => handleSelectCandidate(c)}
                      className="flex items-center justify-between p-3 rounded-xl border bg-[var(--surface-0)] hover:border-[var(--accent)] transition-all text-left group"
                      style={{ borderColor: 'var(--border)' }}
                    >
                      <div className="flex-1">
                        <div className="text-sm font-bold text-[var(--text-primary)]">{c.hierarchy.district}</div>
                        <div className="text-xs text-[var(--text-muted)]">{c.hierarchy.state}</div>
                      </div >
                      <div className="text-[10px] font-mono text-[var(--text-muted)] group-hover:text-[var(--accent)] ml-2">
                        {Math.round(c.confidence * 100)}% Match
                      </div >
                    </button>
                  ))
                ) : (
                  !isLoading && (
                    <div className="text-center py-8 text-[var(--text-muted)]">
                      <p className="text-xs">No locations found. Try a different district name.</p>
                    </div >
                  )
                )}
              </div >
            </motion.div>
          )}
        </AnimatePresence>
      </div >
    </div >
  );
}
