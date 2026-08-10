import { motion } from 'framer-motion';
import { MessageSquare, Archive, BookOpen, Clock, Trash2 } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import type { Chamber } from '@/types';

function statusConfig(status: string) {
  switch (status) {
    case 'active':
      return { color: 'var(--accent-mint)', dot: 'var(--accent-mint)', label: 'Active' };
    case 'saved':
      return { color: 'var(--accent-amber)', dot: 'var(--accent-amber)', label: 'Saved' };
    default:
      return { color: 'var(--text-muted)', dot: 'var(--text-faint)', label: 'Archived' };
  }
}

function formatDate(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const hrs = Math.floor(diff / 3600000);
  if (hrs < 1) return 'just now';
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function SessionHistoryList() {
  const sessionsList = useSyntapseStore((s) => s.sessionsList);
  const hydrateChamber = useSyntapseStore((s) => s.hydrateChamber);
  const deleteChamber = useSyntapseStore((s) => s.deleteChamber);
  const activeSessionId = useSyntapseStore((s) => s.activeSessionId);

  return (
    <div className="flex flex-col gap-2">
      {sessionsList.length === 0 && (
        <div className="text-center py-8 px-4">
          <BookOpen className="w-8 h-8 mx-auto mb-3 text-faint-c" />
          <p className="text-sm text-muted-c">
            No chambers yet. Initialize your first one to begin.
          </p>
        </div>
      )}

      {sessionsList.map((chamber: Chamber, i) => {
        const cfg = statusConfig(chamber.status);
        const isActive = chamber.id === activeSessionId;
        return (
          <motion.div
            key={chamber.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="group flex flex-col p-3 rounded-xl border transition-all duration-200 shadow-sm relative cursor-pointer"
            onClick={() => hydrateChamber(chamber.id)}
            style={{
              background: isActive
                ? 'color-mix(in srgb, var(--accent-amber) 12%, var(--surface-1))'
                : 'transparent',
              borderColor: isActive
                ? 'var(--accent-amber)'
                : 'var(--surface-border)',
              borderWidth: isActive ? '2px' : '1px',
            }}
          >
            <div className="flex items-start gap-2">
              <div
                className="mt-1.5 w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ background: cfg.dot }}
              />
              <div className="flex-1 min-w-0 pr-6">
                <p className="text-sm font-semibold truncate text-primary-c">
                  {chamber.topic_name}
                </p>
                <div className="flex items-center gap-3 mt-1.5 text-xs text-secondary-c font-medium">
                  <span className="flex items-center gap-1 font-bold whitespace-nowrap" style={{ color: cfg.color }}>
                    {chamber.status === 'archived' ? (
                      <Archive className="w-3 h-3" />
                    ) : (
                      <MessageSquare className="w-3 h-3" />
                    )}
                    {cfg.label}
                  </span>
                  <span className="flex items-center gap-1 whitespace-nowrap">
                    Turn {chamber.turn_count}
                  </span>
                  <span className="flex items-center gap-1 text-muted-c whitespace-nowrap">
                    <Clock className="w-3 h-3" />
                    {formatDate(chamber.updated_at)}
                  </span>
                </div>
              </div>
            </div>
            
            <button
              className="absolute top-2.5 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 text-muted-c hover:text-red-500 rounded-md hover:bg-black/5 dark:hover:bg-white/5"
              title="Delete Chamber"
              onClick={(e) => {
                e.stopPropagation();
                deleteChamber(chamber.id);
              }}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </motion.div>
        );
      })}
    </div>
  );
}
