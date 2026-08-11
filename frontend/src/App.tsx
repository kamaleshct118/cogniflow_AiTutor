/**
 * ===============================================================================
 * SYNAPSE FRONTEND — Master Application Shell (App.tsx)
 * ===============================================================================
 * Purpose:
 *   • Main UI layout controller managing view transitions, global state hydration,
 *     theme toggles, and modal rendering.
 *
 * Core Logic & Hierarchy:
 *   ├── Three.js Background   : NeuralBackground interactive Canvas
 *   ├── Navigation Header     : Theme toggles, Cognitive DNA pill, Focus mode switch
 *   ├── View Switcher         :
 *   │     ├── CALIBRATION     : CalibrationGate (Agent 1 onboarding essay)
 *   │     ├── DASHBOARD       : ChamberDashboard (Chamber creation & selection)
 *   │     └── CHAMBER_IDE     : ActiveChamberIDE (Interactive learning chamber)
 *   └── Global Modals         : CognitiveModal (DNA view & profile inspection)
 * ===============================================================================
 */

import { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Dna, Sun, Moon, FlaskConical, Zap } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import { buildDnaTag } from '@/types';
import NeuralBackground from '@/components/three/NeuralBackground';
import CalibrationGate from '@/components/calibration/CalibrationGate';
import ChamberDashboard from '@/components/dashboard/ChamberDashboard';
import ActiveChamberIDE from '@/components/chamber/ActiveChamberIDE';

import CognitiveModal from '@/components/calibration/CognitiveModal';

function App() {
  const currentView = useSyntapseStore((s) => s.currentView);
  const theme = useSyntapseStore((s) => s.theme);
  const toggleTheme = useSyntapseStore((s) => s.toggleTheme);
  const toggleGapDrawer = useSyntapseStore((s) => s.toggleGapDrawer);
  const toggleFocusMode = useSyntapseStore((s) => s.toggleFocusMode);
  const toggleCognitiveModal = useSyntapseStore((s) => s.toggleCognitiveModal);
  const isGapDrawerOpen = useSyntapseStore((s) => s.isGapDrawerOpen);
  const hydrateChamber = useSyntapseStore((s) => s.hydrateChamber);
  const activeSessionId = useSyntapseStore((s) => s.activeSessionId);
  const cognitiveProfile = useSyntapseStore((s) => s.cognitiveProfile);
  const setView = useSyntapseStore((s) => s.setView);

  useEffect(() => {
    if (theme === 'sepia') {
      document.body.classList.add('sepia');
      document.documentElement.classList.remove('dark');
    } else {
      document.body.classList.remove('sepia');
      document.documentElement.classList.add('dark');
    }
  }, [theme]);

  useEffect(() => {
    if (activeSessionId && currentView === 'chamber') {
      hydrateChamber(activeSessionId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === 'g') {
        e.preventDefault();
        if (currentView === 'chamber') toggleGapDrawer();
      }
      if (mod && e.key === 'b') {
        e.preventDefault();
        if (currentView === 'chamber') toggleFocusMode();
      }
      if (e.key === 'Escape') {
        if (isGapDrawerOpen) toggleGapDrawer(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [currentView, isGapDrawerOpen, toggleGapDrawer, toggleFocusMode]);

  const showHeader = currentView !== 'chamber';
  const dnaTag = buildDnaTag(cognitiveProfile);

  return (
    <div className="relative h-screen w-screen overflow-hidden flex flex-col surface-0">
      <NeuralBackground />

      {/* Top Header Bar — changes per screen */}
      {showHeader && (
        <header
          className="h-16 flex-shrink-0 z-30 flex items-center gap-3 px-5 py-3 border-b"
          style={{
            background: 'var(--header-bg)',
            backdropFilter: 'blur(12px)',
            borderColor: 'var(--surface-border)',
          }}
        >
          {currentView === 'calibration' && (
            <div className="flex items-center gap-2 flex-1">
              <Dna className="w-5 h-5" style={{ color: 'var(--accent-violet-glow)' }} />
              <span className="font-serif text-xl font-bold tracking-tight text-primary-c">
                Cogniflow
              </span>
              <span className="hidden sm:inline text-sm font-serif italic tracking-wide text-secondary-c ml-1">
                // your tutor your style
              </span>
              <span className="hidden md:inline ml-auto text-xs font-mono text-muted-c">
                [ Footprint: {cognitiveProfile ? 'Calibrated' : 'Uncalibrated'} ]
              </span>
            </div>
          )}

          {currentView === 'dashboard' && (
            <div className="flex items-center gap-2 flex-1">
              <FlaskConical className="w-5 h-5" style={{ color: 'var(--accent-amber)' }} />
              <span className="font-serif text-xl font-bold tracking-tight text-primary-c">
                Cogniflow
              </span>
              <span className="hidden sm:inline text-sm font-serif italic tracking-wide text-secondary-c ml-1">
                // your tutor your style
              </span>
              <span className="hidden md:inline ml-auto text-xs font-mono text-muted-c">
                [ Footprint: {dnaTag} {cognitiveProfile ? 'Active' : ''} ]
              </span>
            </div>
          )}

          <div className="ml-auto flex items-center gap-3">
            <button
              onClick={() => toggleCognitiveModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border text-xs font-bold text-primary-c transition-all duration-200 hover:border-amber-c hover:scale-105 active:scale-95 shadow-sm"
              style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
              title="Cognitive Footprint Settings"
            >
              <Dna className="w-4 h-4 text-amber-c" />
              <span>Cognitive Footprint</span>
            </button>

            <button
              onClick={(e) => toggleTheme(e)}
              className="p-2 rounded-xl border transition-all duration-200 text-primary-c hover:border-amber-c hover:scale-105 active:scale-95 shadow-sm"
              style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-c" />
              ) : (
                <Moon className="w-4 h-4 text-primary-c" />
              )}
            </button>
          </div>
        </header>
      )}

      {/* Screen Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex-1 flex flex-col h-full overflow-hidden"
          >
            {currentView === 'calibration' && <CalibrationGate />}
            {currentView === 'dashboard' && <ChamberDashboard />}
            {currentView === 'chamber' && <ActiveChamberIDE />}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Global Cognitive DNA Modal */}
      <CognitiveModal />
    </div>
  );
}

export default App;
