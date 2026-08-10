import { motion } from 'framer-motion';
import { Target, ArrowRight } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';

interface SocraticProbeCardProps {
  question: string;
  targetConcept?: string;
}

export default function SocraticProbeCard({
  question,
  targetConcept,
}: SocraticProbeCardProps) {
  const setChatInput = useSyntapseStore((s) => s.setChatInput);
  const sendChatMessage = useSyntapseStore((s) => s.sendChatMessage);

  const handleQuickReply = (reply: string) => {
    sendChatMessage(reply);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.15 }}
      className="mt-3 rounded-lg border p-3.5 glow-amber max-w-[95%] opacity-90 hover:opacity-100 transition-opacity"
      style={{
        background: 'var(--probe-bg)',
        borderColor: 'var(--probe-border)',
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <Target className="w-3.5 h-3.5 text-amber-c" />
        <span className="text-[10.5px] font-semibold text-amber-c uppercase tracking-wider">
          Socratic Probe
        </span>
        {targetConcept && (
          <span className="text-xs text-muted-c ml-auto font-mono">
            {targetConcept}
          </span>
        )}
      </div>
      <p className="text-[13px] text-primary-c leading-relaxed mb-3">
        {question}
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleQuickReply(question)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border hover:scale-[1.02] active:scale-[0.98]"
          style={{
            background: 'var(--probe-btn-bg)',
            borderColor: 'var(--probe-btn-border)',
            color: 'var(--probe-btn-text)',
          }}
        >
          Answer
          <ArrowRight className="w-3 h-3" />
        </button>
        <button
          onClick={() => handleQuickReply(`I'm not sure about: ${targetConcept || question}`)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-secondary-c text-xs transition-all"
          style={{
            background: 'var(--surface-2)',
            borderColor: 'var(--surface-border)',
          }}
          onMouseEnter={(e) => { 
            e.currentTarget.style.background = 'var(--surface-border)'; 
            e.currentTarget.style.color = 'var(--surface-0)'; 
          }}
          onMouseLeave={(e) => { 
            e.currentTarget.style.background = 'var(--surface-2)'; 
            e.currentTarget.style.color = 'var(--text-secondary)'; 
          }}
        >
          Need a hint
        </button>
        <button
          onClick={() => handleQuickReply('I would like to skip this question.')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-secondary-c text-xs transition-all"
          style={{
            background: 'var(--surface-2)',
            borderColor: 'var(--surface-border)',
          }}
          onMouseEnter={(e) => { 
            e.currentTarget.style.background = 'var(--surface-border)'; 
            e.currentTarget.style.color = 'var(--surface-0)'; 
          }}
          onMouseLeave={(e) => { 
            e.currentTarget.style.background = 'var(--surface-2)'; 
            e.currentTarget.style.color = 'var(--text-secondary)'; 
          }}
        >
          Skip
        </button>
      </div>
    </motion.div>
  );
}

