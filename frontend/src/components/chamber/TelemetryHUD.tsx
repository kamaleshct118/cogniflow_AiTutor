import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Cpu, Globe, Shield, Brain, Scale, CheckCircle2, SearchCode } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';

const AGENT_ICONS: Record<string, typeof Activity> = {
  'Agent 1': Cpu,
  'Agent 2': Brain,
  'Agent 3A': CheckCircle2,
  'Agent 3B': SearchCode,
  'Agent 3C': Scale,
  'Agent 4': Activity,
  'Agent 5': Shield,
  'Agent 6': Globe,
};

const AGENT_COLORS: Record<string, string> = {
  'Agent 1': 'var(--accent-violet-glow)',
  'Agent 2': 'var(--accent-violet-glow)',
  'Agent 3A': 'var(--accent-mint-glow)',
  'Agent 3B': 'var(--accent-amber)',
  'Agent 3C': 'var(--accent-terracotta-glow)',
  'Agent 4': 'var(--accent-amber)',
  'Agent 5': 'var(--accent-terracotta-glow)',
  'Agent 6': 'var(--accent-mint-glow)',
};

export default function TelemetryHUD() {
  const isAgentThinking = useSyntapseStore((s) => s.isAgentThinking);
  const activeAgentNode = useSyntapseStore((s) => s.activeAgentNode);
  const statusMessage = useSyntapseStore((s) => s.statusMessage);
  const telemetrySteps = useSyntapseStore((s) => s.telemetrySteps);

  return (
    <div
      className="border-b px-4 py-2.5"
      style={{ borderColor: 'var(--surface-border)' }}
    >
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-1.5">
          <motion.div
            animate={{
              scale: isAgentThinking ? [1, 1.3, 1] : 1,
              opacity: isAgentThinking ? [0.5, 1, 0.5] : 0.3,
            }}
            transition={{ duration: 1.2, repeat: isAgentThinking ? Infinity : 0 }}
            className="w-2 h-2 rounded-full"
            style={{ background: isAgentThinking ? 'var(--accent-amber)' : 'var(--text-faint)' }}
          />
          <span className="text-xs font-mono uppercase tracking-wider text-muted-c">
            Telemetry
          </span>
        </div>

        <AnimatePresence mode="wait">
          {isAgentThinking && activeAgentNode && (
            <motion.div
              key={activeAgentNode}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="flex items-center gap-2"
            >
              {(() => {
                const Icon = AGENT_ICONS[activeAgentNode] || Activity;
                const color = AGENT_COLORS[activeAgentNode] || 'var(--accent-amber)';
                return <Icon className="w-3.5 h-3.5" style={{ color }} />;
              })()}
              <span
                className="text-xs font-mono"
                style={{ color: AGENT_COLORS[activeAgentNode] || 'var(--accent-amber)' }}
              >
                {activeAgentNode}
              </span>
              <span className="text-xs text-faint-c">|</span>
              <span className="text-xs text-secondary-c">{statusMessage}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {!isAgentThinking && telemetrySteps.length > 0 && (
          <div className="flex items-center gap-2 text-xs text-faint-c">
            <span>Last: {telemetrySteps[telemetrySteps.length - 1]?.agent}</span>
            <span>·</span>
            <span>{telemetrySteps[telemetrySteps.length - 1]?.label}</span>
          </div>
        )}

        {!isAgentThinking && telemetrySteps.length === 0 && (
          <span className="text-xs text-faint-c">Idle — awaiting input</span>
        )}
      </div>
    </div>
  );
}
