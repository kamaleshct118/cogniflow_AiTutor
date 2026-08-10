import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Dna, Sparkles, Brain, Check, Trash2 } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import MesmerizingLoader from '@/components/three/MesmerizingLoader';
import ProfileRadarCard from './ProfileRadarCard';

export default function CognitiveModal() {
  const [essay, setEssay] = useState('');
  const isCognitiveModalOpen = useSyntapseStore((s) => s.isCognitiveModalOpen);
  const toggleCognitiveModal = useSyntapseStore((s) => s.toggleCognitiveModal);
  const calibrate = useSyntapseStore((s) => s.calibrate);
  const deleteCognitiveProfile = useSyntapseStore((s) => s.deleteCognitiveProfile);
  const isCalibrating = useSyntapseStore((s) => s.isCalibrating);
  const cognitiveProfile = useSyntapseStore((s) => s.cognitiveProfile);
  const statusMessage = useSyntapseStore((s) => s.statusMessage);

  if (!isCognitiveModalOpen) return null;

  const handleSubmit = async () => {
    if (wordCount <= 25 || isCalibrating) return;
    await calibrate(essay.trim());
  };

  const handleDelete = async () => {
    await deleteCognitiveProfile();
    setEssay('');
  };

  const wordCount = essay.trim().split(/\s+/).filter(Boolean).length;

  return (
    <AnimatePresence>
      {/* Centered Backdrop with Flex Centering */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-md p-4"
        style={{ background: 'var(--backdrop)' }}
        onClick={() => toggleCognitiveModal(false)}
      >
        {/* Glassmorphic Modal Dialog */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          className="w-full max-w-3xl p-7 md:p-8 pb-10 md:pb-12 rounded-2xl shadow-2xl max-h-[90vh] overflow-y-auto chat-scroll min-h-[520px]"
          style={{
            background: 'var(--surface-2)',
            borderColor: 'var(--surface-border)',
            borderWidth: '2px',
            borderStyle: 'solid',
          }}
          onClick={(e) => e.stopPropagation()}
        >
        {/* Header */}
        <div className="flex items-center justify-between pb-5 mb-5 border-b surface-border">
          <div className="flex items-center gap-3.5">
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center border surface-border"
              style={{
                background: 'var(--surface-1)',
              }}
            >
              <Dna className="w-5 h-5 text-amber-c" />
            </div>
            <div>
              <h2 className="text-xl font-bold font-serif text-primary-c flex items-center gap-2">
                Cognitive Footprint Settings
                {cognitiveProfile && (
                  <span className="text-xs font-sans px-2.5 py-0.5 rounded-md border font-medium text-mint-c border-mint-c flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" /> Footprint Active
                  </span>
                )}
              </h2>
              <p className="text-xs text-secondary-c font-sans mt-0.5">
                Reverse-engineer implicit mental models for personalized Socratic teaching
              </p>
            </div>
          </div>
          <button
            onClick={() => toggleCognitiveModal(false)}
            className="p-2 rounded-xl text-primary-c transition-all surface-border border hover:bg-surface-1"
            style={{ background: 'var(--surface-1)' }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Existing Profile Overview */}
        {cognitiveProfile && (
          <div className="mb-7">
            <ProfileRadarCard profile={cognitiveProfile} />
          </div>
        )}

        {/* Calibration Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-base font-semibold text-primary-c flex items-center gap-2 font-serif">
              <Brain className="w-4.5 h-4.5 text-amber-c" />
              {cognitiveProfile ? 'Re-calibrate Cognitive Footprint' : 'Calibrate Your Mental Model'}
            </label>
            <span className="text-xs text-muted-c font-mono px-2 py-0.5 rounded border surface-border" style={{ background: 'var(--surface-1)' }}>
              {wordCount} words
            </span>
          </div>
          <p className="text-xs text-secondary-c mb-4 leading-relaxed">
            Write a detailed explanation of a technical concept you ALREADY understand well (e.g., database indices, B-Trees, recursion). Our forensic engine parses your mental model.
          </p>

          <textarea
            value={essay}
            onChange={(e) => setEssay(e.target.value)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') handleSubmit();
            }}
            placeholder="In B-Trees, data is structured in balanced multi-way search trees where nodes maintain sorted keys. I think of this like a library catalog system where each card narrows location..."
            className="w-full h-72 smooth-input rounded-xl p-5 text-sm font-serif resize-none shadow-inner"
            style={{
              background: 'var(--surface-1)',
            }}
          />

          <div className="flex items-center justify-between mt-5 pb-6">
            <p className="text-xs text-muted-c font-medium">
              {wordCount <= 25
                ? 'Write more than 25 words to enable mapping'
                : 'Cmd / Ctrl + Enter to submit'}
            </p>
            <div className="flex items-center gap-3">
              {cognitiveProfile && (
                <button
                  onClick={handleDelete}
                  disabled={isCalibrating}
                  className="flex items-center gap-1.5 px-4 py-3 rounded-xl font-medium text-xs border border-red-500/40 text-red-500 hover:bg-red-500/10 transition-all active:scale-95 cursor-pointer"
                  title="Delete active Cognitive Footprint to test fresh calibration"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete Footprint</span>
                </button>
              )}
              <button
                onClick={handleSubmit}
                disabled={wordCount <= 25 || isCalibrating}
                className="flex items-center gap-2 px-7 py-3 rounded-xl font-bold text-sm btn-action-primary transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed shadow-md hover:scale-[1.02] active:scale-[0.98]"
              >
                <Sparkles className="w-4 h-4" />
                <span>Save Cognitive Footprint</span>
              </button>
            </div>
          </div>

          {/* Calibration Processing Overlay */}
          <AnimatePresence>
            {isCalibrating && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute inset-0 z-30 flex flex-col items-center justify-center p-6 backdrop-blur-lg surface-1 rounded-2xl"
                style={{ background: 'var(--backdrop)' }}
              >
                <div className="relative mb-6">
                  <div className="w-20 h-20 rounded-full flex items-center justify-center surface-2 border surface-border shadow-inner">
                    <MesmerizingLoader size={44} />
                  </div>
                  <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 7, repeat: Infinity, ease: 'linear' }}
                    className="absolute -inset-2 rounded-full border-2 border-dashed border-violet-c/50 pointer-events-none"
                  />
                </div>

                <h3 className="font-serif text-xl font-bold text-primary-c mb-1">
                  Mapping Cognitive DNA
                </h3>
                <p className="text-xs text-secondary-c mb-5 font-sans max-w-sm text-center">
                  Reverse-engineering implicit mental schema & forensic vectors from your text explanation...
                </p>

                {/* Progress bar */}
                <div className="w-full max-w-xs h-2 rounded-full surface-2 overflow-hidden border surface-border mb-3">
                  <motion.div
                    initial={{ width: '10%' }}
                    animate={{ width: ['15%', '50%', '85%', '98%'] }}
                    transition={{ duration: 4, ease: 'easeInOut' }}
                    className="h-full bg-amber-c rounded-full glow-amber"
                  />
                </div>

                <p className="text-xs text-amber-c font-mono animate-pulse font-semibold">
                  {statusMessage || 'Executing forensic NLP pipeline…'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  </AnimatePresence>
  );
}
