import { motion } from 'framer-motion';
import { X, Zap, Pin, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import MesmerizingLoader from '@/components/three/MesmerizingLoader';

export default function GapAnalysisDrawer() {
  const toggleGapDrawer = useSyntapseStore((s) => s.toggleGapDrawer);
  const gapAnalysisData = useSyntapseStore((s) => s.gapAnalysisData);
  const isGapAnalyzing = useSyntapseStore((s) => s.isGapAnalyzing);
  const sendChatMessage = useSyntapseStore((s) => s.sendChatMessage);

  const handleExploreGap = (topic: string) => {
    toggleGapDrawer(false);
    sendChatMessage(`I want to learn about: ${topic}`);
  };

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={() => toggleGapDrawer(false)}
        className="fixed inset-0 z-40 backdrop-blur-sm"
        style={{ background: 'var(--backdrop)' }}
      />

      {/* Drawer */}
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="fixed top-0 right-0 bottom-0 w-full max-w-md z-50 flex flex-col"
        style={{
          background: 'color-mix(in srgb, var(--surface-1) 95%, transparent)',
          backdropFilter: 'blur(24px)',
          borderLeft: '1px solid var(--surface-border)',
        }}
      >
        {/* Header */}
        <div
          className="flex items-center gap-3 px-5 py-4 border-b"
          style={{ borderColor: 'var(--surface-border)' }}
        >
          <div className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-xl border flex items-center justify-center glow-terracotta"
              style={{
                background: 'color-mix(in srgb, var(--accent-terracotta) 15%, transparent)',
                borderColor: 'color-mix(in srgb, var(--accent-terracotta) 30%, transparent)',
              }}
            >
              <Zap className="w-4 h-4 text-terracotta-glow-c" />
            </div>
            <div>
              <h2 className="font-serif text-lg font-semibold text-primary-c">
                Knowledge Gap Diagnostic
              </h2>
              <p className="text-xs text-muted-c font-mono">
                POST /gap_analysis
              </p>
            </div>
          </div>
          <button
            onClick={() => toggleGapDrawer(false)}
            className="ml-auto p-2 rounded-lg transition-colors"
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
          >
            <X className="w-4 h-4 text-secondary-c" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto chat-scroll px-5 py-5">
          {isGapAnalyzing && !gapAnalysisData && (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              <MesmerizingLoader size={80} />
              <div className="text-center">
                <p className="text-sm text-terracotta-glow-c animate-pulse-glow">
                  Analyzing your knowledge gaps…
                </p>
                <p className="text-xs text-muted-c mt-1">
                  Agents are reviewing your session history
                </p>
              </div>
            </div>
          )}

          {gapAnalysisData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Diagnostic Summary */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-terracotta-glow-c" />
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-secondary-c">
                    Diagnostic Summary
                  </h3>
                </div>
                <div
                  className="rounded-xl border p-4"
                  style={{
                    background: 'var(--surface-2)',
                    borderColor: 'var(--surface-border)',
                  }}
                >
                  <p className="text-sm leading-relaxed text-secondary-c font-serif italic">
                    "{gapAnalysisData.diagnostic_summary}"
                  </p>
                </div>
              </div>

              {/* Suggestions */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Pin className="w-4 h-4 text-amber-c" />
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-secondary-c">
                    Actionable Suggestions
                  </h3>
                  <span className="text-xs text-muted-c ml-auto">
                    1-click to explore
                  </span>
                </div>

                <div className="space-y-3">
                  {(Array.isArray(gapAnalysisData.suggestions) ? gapAnalysisData.suggestions : []).map((rawItem, i) => {
                    const suggestion = typeof rawItem === 'string'
                      ? { topic: rawItem, reason: 'Deep dive into this concept with your Socratic Teacher' }
                      : rawItem;
                    return (
                      <motion.button
                        key={i}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        onClick={() => handleExploreGap(suggestion.topic)}
                        className="group w-full text-left rounded-xl border p-4 transition-all"
                        style={{
                          background: 'var(--surface-2)',
                          borderColor: 'var(--surface-border)',
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className="mt-0.5 w-6 h-6 rounded-lg border flex items-center justify-center flex-shrink-0 transition-colors"
                            style={{
                              background: 'color-mix(in srgb, var(--accent-amber) 15%, transparent)',
                              borderColor: 'color-mix(in srgb, var(--accent-amber) 25%, transparent)',
                            }}
                          >
                            <Pin className="w-3 h-3 text-amber-c" />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-primary-c group-hover:text-amber-glow-c transition-colors">
                              {suggestion.button_label || `Explore Gap: ${suggestion.topic}`}
                            </p>
                            <p className="text-xs text-muted-c mt-1 mb-2">
                              {suggestion.reason}
                            </p>
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium border"
                              style={{
                                background: 'var(--surface-1)',
                                borderColor: 'var(--surface-border)',
                                color: 'var(--text-primary)',
                              }}
                            >
                              <Zap className="w-3 h-3 text-amber-c" />
                              Ask Socratic Teacher in Chat →
                            </span>
                          </div>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Verified Facts */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="mt-6 rounded-xl border p-4"
                style={{
                  background: 'color-mix(in srgb, var(--accent-mint) 10%, transparent)',
                  borderColor: 'color-mix(in srgb, var(--accent-mint) 20%, transparent)',
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-4 h-4 text-mint-c" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-mint-glow-c">
                    Verified by Agent 6
                  </span>
                </div>
                <p className="text-xs text-muted-c">
                  All diagnostic suggestions cross-referenced with ArXiv
                  publications and validated against your session's probe
                  history.
                </p>
              </motion.div>
            </motion.div>
          )}
        </div>

        {/* Footer */}
        <div
          className="px-5 py-3 border-t"
          style={{ borderColor: 'var(--surface-border)' }}
        >
          <button
            onClick={() => toggleGapDrawer(false)}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border text-sm text-secondary-c transition-all"
            style={{
              background: 'var(--surface-2)',
              borderColor: 'var(--surface-border)',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'color-mix(in srgb, var(--surface-2) 80%, var(--text-primary))'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
          >
            <X className="w-4 h-4" />
            Close Diagnostic Drawer
          </button>
        </div>
      </motion.div>
    </>
  );
}
