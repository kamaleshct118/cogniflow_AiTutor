import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated } from '@react-spring/web';
import { Sparkles, BookOpen, Lightbulb, ArrowRight } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import { buildDnaTag } from '@/types';
import MesmerizingLoader from '@/components/three/MesmerizingLoader';

export default function RoomInitializer() {
  const [topic, setTopic] = useState('');
  const [context, setContext] = useState('');
  const startNewSession = useSyntapseStore((s) => s.startNewSession);
  const isStartingSession = useSyntapseStore((s) => s.isStartingSession);
  const cognitiveProfile = useSyntapseStore((s) => s.cognitiveProfile);

  const [orbSprings] = useSpring(() => ({
    scale: 1,
    config: { tension: 250, friction: 18 },
  }));

  const handleStart = () => {
    if (topic.trim().length < 3 || isStartingSession) return;
    startNewSession(topic.trim(), context.trim() || null);
  };

  const dnaTag = buildDnaTag(cognitiveProfile);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <div
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-medium mb-4"
          style={{
            background: 'color-mix(in srgb, var(--accent-mint) 10%, transparent)',
            borderColor: 'color-mix(in srgb, var(--accent-mint) 25%, transparent)',
            color: 'var(--accent-mint-glow)',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: 'var(--accent-mint)' }}
          />
          Profile: {dnaTag} {cognitiveProfile ? 'Active' : ''}
        </div>
        <h2 className="font-serif text-3xl font-semibold mb-2 text-primary-c">
          Initialize New Chamber
        </h2>
        <p className="text-secondary-c">
          Choose a topic you want to master. Add optional context to help the
          agents calibrate their teaching approach.
        </p>
      </div>

      {/* Topic Input */}
      <div
        className="p-5 mb-4 rounded-2xl border shadow-sm"
        style={{
          background: 'var(--surface-1)',
          borderColor: 'var(--surface-border)',
          borderWidth: '1px',
        }}
      >
        <label className="flex items-center gap-2 text-sm font-semibold mb-2 text-primary-c font-serif">
          <BookOpen className="w-4 h-4 text-amber-c" />
          Target Topic
        </label>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') handleStart();
          }}
          placeholder="Transformer Attention Mechanisms"
          className="w-full smooth-input rounded-xl px-4 py-3 text-primary-c font-medium shadow-inner"
        />
      </div>

      {/* Context Input */}
      <div
        className="p-5 mb-6 rounded-2xl border shadow-sm"
        style={{
          background: 'var(--surface-1)',
          borderColor: 'var(--surface-border)',
          borderWidth: '1px',
        }}
      >
        <label className="flex items-center gap-2 text-sm font-semibold mb-2 text-primary-c font-serif">
          <Lightbulb className="w-4 h-4 text-violet-glow-c" />
          Optional Context
          <span className="text-xs font-normal text-secondary-c">
            (what you know / what you struggle with)
          </span>
        </label>
        <textarea
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="I know matrix dot products, but struggle with Q, K, V projections..."
          className="w-full h-28 smooth-input rounded-xl px-4 py-3 text-primary-c font-medium resize-none shadow-inner"
        />

        {/* Suggestion Chips */}
        <div className="mt-4 pt-3 border-t flex flex-wrap items-center gap-2" style={{ borderColor: 'var(--surface-border)' }}>
          <span className="text-xs font-medium text-secondary-c">Suggestions:</span>
          {[
            'Transformer Attention Mechanics',
            'B-Tree Indexing & Database Pages',
            'Async IO & Event Loops',
            'C++ Virtual Tables & Polymorphism',
          ].map((sugg) => (
            <button
              key={sugg}
              type="button"
              onClick={() => setTopic(sugg)}
              className="text-xs px-3 py-1.5 rounded-lg border font-medium text-primary-c transition-all duration-200 hover:border-amber-c hover:bg-surface-1 active:scale-95"
              style={{
                background: 'var(--surface-2)',
                borderColor: 'var(--surface-border)',
              }}
            >
              {sugg}
            </button>
          ))}
        </div>
      </div>

      {/* 3D Orb Submit */}
      <div className="flex flex-col items-center gap-3">
        <animated.button
          style={{
            ...orbSprings,
          }}
          onMouseDown={() => orbSprings.scale.start(0.95)}
          onMouseUp={() => orbSprings.scale.start(1)}
          onMouseLeave={() => orbSprings.scale.start(1)}
          onClick={handleStart}
          disabled={topic.trim().length < 3 || isStartingSession}
          className="relative group flex items-center gap-3 px-8 py-4 rounded-2xl font-bold btn-action-primary shadow-xl transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Sparkles className="w-5 h-5" />
          <span>Initialize Chamber</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </animated.button>
      </div>

      {/* Dedicated Chamber Processing Modal Card Popup */}
      <AnimatePresence>
        {isStartingSession && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-md"
            style={{ background: 'var(--backdrop)' }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.88, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.88, y: 20 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
              className="w-full max-w-md p-8 rounded-3xl shadow-2xl border flex flex-col items-center text-center relative overflow-hidden surface-1 border-surface-border"
              style={{
                background: 'var(--surface-1)',
                borderColor: 'var(--surface-border)',
                borderWidth: '1px',
              }}
            >
              {/* Animated Orbit around 3D Loader */}
              <div className="relative mb-6">
                <div className="w-24 h-24 rounded-full flex items-center justify-center surface-2 border surface-border shadow-inner">
                  <MesmerizingLoader size={52} />
                </div>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                  className="absolute -inset-2 rounded-full border-2 border-dashed border-amber-c/40 pointer-events-none"
                />
              </div>

              <h3 className="font-serif text-2xl font-bold text-primary-c mb-2">
                Initializing Chamber
              </h3>

              <div className="px-3.5 py-1 rounded-full text-xs font-mono mb-5 text-amber-c surface-2 border surface-border">
                Topic: {topic || 'Custom Learning Topic'}
              </div>

              {/* Progress Shimmer Bar */}
              <div className="w-full h-2 rounded-full overflow-hidden surface-2 mb-4 border surface-border">
                <motion.div
                  initial={{ width: '5%' }}
                  animate={{ width: ['10%', '45%', '80%', '98%'] }}
                  transition={{ duration: 3.5, ease: 'easeInOut' }}
                  className="h-full bg-amber-c rounded-full glow-amber"
                />
              </div>

              <p className="text-xs text-secondary-c animate-pulse font-mono">
                Spinning up agent network & pre-fetching knowledge graph…
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
