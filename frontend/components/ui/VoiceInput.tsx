'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, RotateCcw, CheckCircle2, Loader2, Edit3, Volume2, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { uploadVoice, confirmVoice, saveUserAnalysisBackend } from '@/lib/api';
import { useRouter } from 'next/navigation';

import { useLanguage } from '@/lib/LanguageContext';

interface VoiceInputProps {
  onComplete?: (data: any) => void;
}

export default function VoiceInput({ onComplete }: VoiceInputProps) {
  const { lang, voicePreference, setVoicePreference, setLang } = useLanguage();
  const [status, setStatus] = useState<'idle' | 'recording' | 'processing' | 'review'>('idle');
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const router = useRouter();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      // Stop AI speech immediately on component unmount/route change
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const speakWelcome = () => {
    if (!window.speechSynthesis) {
      console.warn("Speech synthesis not supported");
      return;
    }

    window.speechSynthesis.cancel();

    setIsSpeaking(true);
    const msg = new SpeechSynthesisUtterance();

    const messages: Record<string, string> = {
      'en-US': "Welcome to Gram Nirnay AI. Please describe your business idea in your native tongue. I am listening!",
      'hi-IN': "ग्राम निर्णय ए बोर्ड एआई में आपका स्वागत है। कृपया अपने व्यावसायिक विचार को अपनी मातृभाषा में बताएं। मैं सुन रहा हूँ!",
      'kn-IN': "ಗ್ರಾಮ್ ನಿರ್ಣಯ AI ಗೆ ಸ್ವಾಗತ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವ್ಯವಹಾರದ ಆಲೋಚನೆಯನ್ನು ನಿಮ್ಮ ಮಾತೃಭಾಷೆಯಲ್ಲಿ ವಿವರಿಸಿ. ನಾನು ಕೇಳುತ್ತಿದ್ದೇನೆ!",
    };

    msg.text = messages[lang] || messages['en-US'];
    msg.lang = lang;

    const voices = window.speechSynthesis.getVoices();

    // 1. Try to find a voice that matches BOTH language and preference
    let selectedVoice = voices.find(v =>
      v.lang.startsWith(lang.split('-')[0]) &&
      (voicePreference === 'female'
        ? (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('google') && v.name.toLowerCase().includes('female'))
        : (v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('google') && v.name.toLowerCase().includes('male')))
    );

    // 2. Fallback: match language only
    if (!selectedVoice) {
      selectedVoice = voices.find(v => v.lang.startsWith(lang.split('-')[0]));
    }

    // 3. Final fallback: any voice
    if (!selectedVoice && voices.length > 0) {
      selectedVoice = voices[0];
    }

    if (selectedVoice) msg.voice = selectedVoice;
    msg.rate = 0.9;
    msg.pitch = voicePreference === 'female' ? 1.2 : 0.8;

    msg.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(msg);
  };

  useEffect(() => {
    // Handle async loading of voices in some browsers
    const handleVoicesChanged = () => {
      speakWelcome();
    };

    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = handleVoicesChanged;
    }

    const timer = setTimeout(() => {
      speakWelcome();
    }, 500);
    return () => {
      clearTimeout(timer);
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, [voicePreference]);

  const startRecording = async () => {
    // Stop AI speaking immediately when user starts recording
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);

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
      setTranscript(result.normalized_text || result.raw_text || result.text);
      setStatus('review');
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to process voice input.');
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
          // Map AnalysisResult to AnalysisHistoryItem
          await saveUserAnalysisBackend(user.id, {
            id: `analysis-${Date.now()}`,
            businessIdea: transcript,
            district: result.location?.district || 'Unknown',
            state: result.location?.state || 'Unknown',
            date: new Date().toISOString().split('T')[0],
            score: result.viabilityScore,
            recommendation: result.recommendation,
            projectCost: result.financials?.total_project_cost || 0,
            data: result
          });
        }
        router.push('/report');
      }
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to confirm transcription.');
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
        <div className="flex flex-col gap-3 mb-6">
          <div className="flex gap-2 p-1 rounded-full bg-[var(--surface-1)] border border-[var(--border)] w-fit">
            <button
              onClick={() => setVoicePreference('female')}
              className={`px-3 py-1 rounded-full text-[10px] font-bold transition-all ${
                voicePreference === 'female' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              Female Voice
            </button>
            <button
              onClick={() => setVoicePreference('male')}
              className={`px-3 py-1 rounded-full text-[10px] font-bold transition-all ${
                voicePreference === 'male' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              Male Voice
            </button>
          </div>

          <div className="flex gap-2 p-1 rounded-full bg-[var(--surface-1)] border border-[var(--border)] w-fit">
            {(['en-US', 'hi-IN', 'kn-IN'] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-3 py-1 rounded-full text-[10px] font-bold transition-all ${
                  lang === l ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                {l === 'en-US' ? 'English' : l === 'hi-IN' ? 'Hindi' : 'Kannada'}
              </button>
            ))}
          </div>
        </div>

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