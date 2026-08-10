import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated } from '@react-spring/web';
import { Dna, Sparkles, ArrowRight, Brain } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import MesmerizingLoader from '@/components/three/MesmerizingLoader';
import ProfileRadarCard from './ProfileRadarCard';

export default function CalibrationGate() {
  const [essay, setEssay] = useState('');
  const calibrate = useSyntapseStore((s) => s.calibrate);
  const isCalibrating = useSyntapseStore((s) => s.isCalibrating);
  const cognitiveProfile = useSyntapseStore((s) => s.cognitiveProfile);
  const statusMessage = useSyntapseStore((s) => s.statusMessage);

  const [buttonSprings] = useSpring(() => ({
    scale: 1,
    config: { tension: 300, friction: 15 },
  }));

  const handleSubmit = () => {
    if (essay.trim().length < 20 || isCalibrating) return;
    calibrate(essay.trim());
  };

  const wordCount = essay.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-3xl w-full"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-medium mb-6"
            style={{
              background: 'color-mix(in srgb, var(--accent-violet) 10%, transparent)',
              borderColor: 'color-mix(in srgb, var(--accent-violet) 30%, transparent)',
              color: 'var(--accent-violet-glow)',
            }}
          >
            <Dna className="w-3.5 h-3.5" />
            Phase 0 — Cognitive DNA Onboarding
          </div>
          <h1 className="font-serif text-4xl md:text-5xl font-semibold leading-tight mb-4 text-primary-c">
            Calibrate Your{' '}
            <span className="text-amber-c text-glow-amber">Learning DNA</span>
          </h1>
          <p className="text-secondary-c text-lg leading-relaxed max-w-2xl mx-auto">
            Explain a complex concept you already understand. Syntapse will
            reverse-engineer your preferred analogies, pacing, and structural
            depth — then teach you everything else the way you learn best.
          </p>
        </div>

        {/* Essay Canvas */}
        <div className="glass-panel p-3 md:p-4 mb-6 shadow-xl transition-all duration-300 focus-within:border-amber-c focus-within:ring-2 focus-within:ring-amber-500/20">
          <div
            className="flex items-center gap-2 px-4 py-3 border-b surface-border"
          >
            <Brain className="w-4.5 h-4.5 text-amber-c" />
            <span className="text-sm font-semibold text-primary-c font-serif">
              Editorial Essay Canvas
            </span>
            <span className="ml-auto text-xs text-muted-c font-mono px-2 py-0.5 rounded border surface-border" style={{ background: 'var(--surface-1)' }}>
              {wordCount} words
            </span>
          </div>
          <textarea
            value={essay}
            onChange={(e) => setEssay(e.target.value)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') handleSubmit();
            }}
            placeholder="In B-Trees, data is structured in balanced multi-way search trees where nodes maintain sorted keys. I think of this like a library catalog system..."
            className="w-full h-64 bg-transparent px-4 py-4 text-primary-c font-serif text-lg leading-relaxed resize-none focus:outline-none transition-colors duration-200"
            style={{ '::placeholder': { color: 'var(--text-faint)' } } as React.CSSProperties}
          />
        </div>

        {/* Submit Button */}
        <div className="flex flex-col items-center gap-4">
          <animated.button
            style={{
              ...buttonSprings,
              background: 'linear-gradient(135deg, var(--accent-amber), var(--accent-terracotta), var(--accent-violet))',
              color: 'var(--surface-0)',
            }}
            onMouseDown={() => buttonSprings.scale.start(0.95)}
            onMouseUp={() => buttonSprings.scale.start(1)}
            onMouseLeave={() => buttonSprings.scale.start(1)}
            onClick={handleSubmit}
            disabled={essay.trim().length < 20 || isCalibrating}
            className="relative group flex items-center gap-3 px-9 py-4 rounded-2xl font-bold text-base shadow-2xl transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-amber-500/20"
          >
            {isCalibrating ? (
              <>
                <MesmerizingLoader size={32} />
                <span className="ml-2">Mapping Cognition…</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Initiate Cognitive Mapping</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </animated.button>

          {essay.trim().length < 20 && !isCalibrating && (
            <p className="text-xs text-muted-c">
              Write at least 20 words to enable calibration
            </p>
          )}

          <AnimatePresence>
            {isCalibrating && statusMessage && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-sm text-amber-c animate-pulse-glow"
              >
                {statusMessage}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        {/* Radar Card appears after calibration */}
        <AnimatePresence>
          {cognitiveProfile && (
            <motion.div
              initial={{ opacity: 0, y: 40, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-8"
            >
              <ProfileRadarCard profile={cognitiveProfile} />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
