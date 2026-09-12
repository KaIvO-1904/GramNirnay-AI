'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, RotateCcw, CheckCircle2, Loader2, Edit3, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { uploadVoice, confirmVoice, saveUserAnalysisBackend } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface VoiceInputProps {
  onComplete?: (data: any) => void;
}

export default function VoiceInput({ onComplete }: VoiceInputProps) {
  const [status, setStatus] = useState<'idle' | 'recording' | 'processing' | 'review'>('idle');
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        audioChunksRef.current = [];
        await handleUpload(audioBlob);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setStatus('recording');
    } catch (err: any) {
      setError('Microphone access denied. Please enable it in your browser settings.');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
  };

  const handleUpload = async (blob: Blob) => {
    setStatus('processing');
    try {
      const result = await uploadVoice(blob);
      setTranscript(result.normalized_text || result.raw_text);
      setStatus('review');
    } catch (err: any) {
      setError(err.message || 'Failed to process voice input.');
      setStatus('idle');
    }
  };

  const handleConfirm = async () => {
    setStatus('processing');
    try {
      const result = await confirmVoice(transcript);
      if (onComplete) {
        onComplete(result);
      } else {
        // Save analysis to localStorage for the report page
        localStorage.setItem('analysis_result', JSON.stringify(result));

        // Also save to backend
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user.id) {
          await saveUserAnalysisBackend(user.id, {
            businessIdea: transcript,
            district: result.marketAnalysis?.district || 'Unknown',
            state: result.marketAnalysis?.state || 'Unknown',
            score: result.viabilityScore || 0,
            recommendation: result.recommendation,
            projectCost: result.financials?.total_project_cost || 0,
            data: result
          });
        }
        router.push('/report');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to confirm transcription.');
      setStatus('review');
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xl backdrop-blur-md relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500" />

      <div className="text-center mb-8">
        <h3 className="text-xl font-bold tracking-tight text-[var(--text-primary)] mb-2">
          Voice Business Entry
        </h3>
        <p className="text-sm text-[var(--text-secondary)]">
          Describe your venture in your native tongue.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center gap-6">
        <AnimatePresence mode="wait">
          {status === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="relative group">
                <div className="absolute -inset-4 bg-indigo-500/20 rounded-full blur-xl group-hover:bg-indigo-500/30 transition-all duration-500" />
                <Button
                  onClick={startRecording}
                  className="relative w-20 h-20 rounded-full p-0 overflow-hidden shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95"
                  style={{ backgroundColor: 'var(--accent)' }}
                >
                  <Mic size={32} className="text-white" />
                </Button>
              </div>
              <span className="text-sm font-bold text-[var(--text-muted)] animate-pulse">
                Tap to start speaking
              </span>
            </motion.div>
          )}

          {status === 'recording' && (
            <motion.div
              key="recording"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-6"
            >
              <div className="relative flex items-center justify-center w-24 h-24">
                <motion.div
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                  className="absolute inset-0 rounded-full bg-red-500/40"
                />
                <motion.div
                  animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0.1, 0.3] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                  className="absolute inset-0 rounded-full bg-red-400/30"
                />
                <Button
                  onClick={stopRecording}
                  className="relative w-16 h-16 rounded-full p-0 shadow-lg"
                  style={{ backgroundColor: '#ef4444' }}
                >
                  <Square size={24} className="text-white fill-white" />
                </Button>
              </div>
              <div className="flex flex-col items-center gap-2">
                <span className="text-sm font-bold text-red-500 animate-pulse uppercase tracking-widest">
                  Recording...
                </span>
                <div className="flex gap-1 h-4 items-center">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      animate={{ height: [4, 16, 4] }}
                      transition={{ repeat: Infinity, duration: 0.5 + i * 0.1 }}
                      className="w-1 bg-red-500 rounded-full"
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {status === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="relative">
                <Loader2 size={48} className="text-[var(--accent)] animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Volume2 size={16} className="text-[var(--accent)]" />
                </div>
              </div>
              <span className="text-sm font-medium text-[var(--text-secondary)]">
                Analyzing your voice...
              </span>
            </motion.div>
          )}

          {status === 'review' && (
            <motion.div
              key="review"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full space-y-4"
            >
              <div className="flex items-center gap-2 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mb-1">
                <Edit3 size={14} /> Review Transcription
              </div>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="w-full p-4 h-32 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)] text-[var(--text-primary)] text-sm leading-relaxed focus:ring-2 focus:ring-[var(--accent)] outline-none resize-none transition-all"
                placeholder="Transcription will appear here..."
              />
              <div className="flex gap-3">
                <Button
                  onClick={() => setStatus('idle')}
                  variant="outline"
                  className="flex-1 gap-2 rounded-xl h-11"
                >
                  <RotateCcw size={16} /> Retry
                </Button>
                <Button
                  onClick={handleConfirm}
                  variant="primary"
                  className="flex-1 gap-2 rounded-xl h-11 bg-[var(--accent)] hover:bg-[var(--accent)]/90 text-white font-bold"
                >
                  Confirm <CheckCircle2 size={16} />
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs text-red-500 font-medium text-center mt-2 bg-red-500/10 px-3 py-1 rounded-full"
          >
            {error}
          </motion.div>
        )}
      </div>
    </div>
  );
}