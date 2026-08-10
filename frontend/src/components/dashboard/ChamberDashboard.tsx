import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, PanelLeftClose, PanelLeft } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import SessionHistoryList from './SessionHistoryList';
import RoomInitializer from './RoomInitializer';

export default function ChamberDashboard() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const loadChambers = useSyntapseStore((s) => s.loadChambers);
  const sessionsList = useSyntapseStore((s) => s.sessionsList);
  const resetForNewChamber = useSyntapseStore((s) => s.resetForNewChamber);

  useEffect(() => {
    loadChambers();
  }, [loadChambers]);

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] flex items-stretch relative overflow-hidden w-full">
      {/* Floating Toggle Button when Sidebar is Closed */}
      {!isSidebarOpen && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={() => setIsSidebarOpen(true)}
          className="fixed top-20 left-4 z-40 p-2.5 rounded-xl border shadow-lg transition-all hover:scale-105"
          style={{
            background: 'var(--surface-1)',
            borderColor: 'var(--surface-border)',
            color: 'var(--text-primary)',
          }}
          title="Open Session History Sidebar"
        >
          <PanelLeft className="w-5 h-5" />
        </motion.button>
      )}

      {/* Collapsible Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300, opacity: 0, width: 0 }}
            animate={{ x: 0, opacity: 1, width: 288 }}
            exit={{ x: -300, opacity: 0, width: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className="flex-shrink-0 border-r p-4 flex flex-col h-full overflow-hidden"
            style={{
              background: 'var(--surface-1)',
              borderColor: 'var(--surface-border)',
              height: '100%',
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-serif text-xs font-semibold uppercase tracking-wider text-secondary-c">
                Chamber History ({sessionsList.length})
              </h3>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="p-1.5 rounded-lg text-secondary-c hover:text-primary-c hover:bg-surface-2 transition-colors"
                title="Collapse Sidebar"
              >
                <PanelLeftClose className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={resetForNewChamber}
              className="flex items-center gap-2 w-full px-3 py-2.5 rounded-xl border text-sm font-semibold transition-all mb-4 hover:glow-amber"
              style={{
                background: 'color-mix(in srgb, var(--accent-amber) 15%, transparent)',
                borderColor: 'var(--surface-border)',
                color: 'var(--text-primary)',
              }}
            >
              <Plus className="w-4 h-4 text-amber-c" />
              <span>New Learning Chamber</span>
            </button>

            <div className="flex-1 overflow-y-auto no-scrollbar">
              <SessionHistoryList />
            </div>

            <div className="pt-3 mt-auto border-t" style={{ borderColor: 'var(--surface-border)' }}>
              <button
                onClick={() => useSyntapseStore.getState().toggleCognitiveModal(true)}
                className="flex items-center gap-2.5 w-full px-3 py-2.5 rounded-xl border text-xs font-bold text-primary-c transition-all duration-200 hover:border-amber-c hover:bg-surface-2 shadow-sm"
                style={{
                  background: 'var(--surface-2)',
                  borderColor: 'var(--surface-border)',
                }}
              >
                <span className="w-2 h-2 rounded-full bg-violet-c animate-pulse" />
                Cognitive Footprint Settings
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Workspace */}
      <main className="flex-1 overflow-y-auto p-6 md:p-10 flex justify-center items-start min-h-0">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="w-full"
        >
          <RoomInitializer />
        </motion.div>
      </main>
    </div>
  );
}
