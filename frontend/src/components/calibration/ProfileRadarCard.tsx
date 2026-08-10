import { motion } from 'framer-motion';
import { CheckCircle2, TrendingUp, Layers, Clock, Network, GitBranch } from 'lucide-react';
import type { CognitiveProfile } from '@/types';
import { buildDnaTag } from '@/types';

interface ProfileRadarCardProps {
  profile: CognitiveProfile;
}

const TRAITS = [
  { key: 'causal_strategy', label: 'Causal Strategy', icon: GitBranch, color: 'var(--accent-violet-glow)' },
  { key: 'pacing', label: 'Pacing', icon: Clock, color: 'var(--accent-amber)' },
  { key: 'complexity', label: 'Complexity', icon: Layers, color: 'var(--accent-terracotta-glow)' },
  { key: 'analogy_style', label: 'Analogy Style', icon: Network, color: 'var(--accent-mint-glow)' },
  { key: 'structural_depth', label: 'Structural Depth', icon: TrendingUp, color: 'var(--accent-violet-glow)' },
] as const;

export default function ProfileRadarCard({ profile }: ProfileRadarCardProps) {
  return (
    <div className="glass-panel p-7 md:p-8 shadow-xl">
      <div className="flex items-center gap-2 mb-6">
        <CheckCircle2 className="w-5 h-5 text-mint-c" />
        <h3 className="font-serif text-xl font-semibold text-primary-c">
          Cognitive DNA Extracted
        </h3>
        <span className="ml-auto text-xs font-mono text-muted-c">
          {buildDnaTag(profile)}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {TRAITS.map((trait, i) => {
          const Icon = trait.icon;
          return (
            <motion.div
              key={trait.key}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-3.5 px-4 py-4 min-h-[76px] rounded-xl border transition-all hover:border-amber-c/50"
              style={{
                background: 'var(--surface-2)',
                borderColor: 'var(--surface-border)',
              }}
            >
              <div className="p-2 rounded-lg" style={{ background: `color-mix(in srgb, ${trait.color} 12%, var(--surface-1))` }}>
                <Icon className="w-4 h-4" style={{ color: trait.color }} />
              </div>
              <div>
                <p className="text-xs text-muted-c font-medium">{trait.label}</p>
                <p className="text-sm font-semibold capitalize text-primary-c">
                  {String(profile[trait.key as keyof CognitiveProfile])}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-5 p-4 rounded-xl border"
        style={{
          background: 'color-mix(in srgb, var(--accent-mint) 10%, transparent)',
          borderColor: 'color-mix(in srgb, var(--accent-mint) 25%, transparent)',
        }}
      >
        <p className="text-sm text-mint-glow-c font-medium">
          Profile active. You can now initialize learning chambers calibrated
          to your cognitive style.
        </p>
      </motion.div>
    </div>
  );
}
