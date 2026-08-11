/**
 * ===============================================================================
 * SYNAPSE FRONTEND — Active Chamber IDE View (ActiveChamberIDE.tsx)
 * ===============================================================================
 * Purpose:
 *   • Main workspace component featuring chat stream, Socratic probe input,
 *     research catalog viewer, and Agent 3B Gap Analysis drawer.
 *
 * Core Logic & Hierarchy:
 *   ├── Chamber Header        : Topic title, active research badge, session ID
 *   ├── Chat Message Stream   : Rendered markdown teacher explanations & probes
 *   ├── Floating Action (FAB) : Gap Analysis button triggering Agent 3B drawer
 *   └── Side Drawers          : Gap Analysis Diagnostic Drawer & Research Catalog
 * ===============================================================================
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated } from '@react-spring/web';
import { ArrowLeft, Zap, Eye, EyeOff, Activity, Layers, Sun, Moon, Dna, Download } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import { buildDnaTag } from '@/types';


import ChatTerminal from './ChatTerminal';
import Sticky3DGapButton from '@/components/three/Sticky3DGapButton';
import GapAnalysisDrawer from '@/components/gap_analysis/GapAnalysisDrawer';
import { jsPDF } from 'jspdf';

export default function ActiveChamberIDE() {
  const topicName = useSyntapseStore((s) => s.topicName);
  const setView = useSyntapseStore((s) => s.setView);
  const focusMode = useSyntapseStore((s) => s.focusMode);
  const toggleFocusMode = useSyntapseStore((s) => s.toggleFocusMode);
  const toggleCognitiveModal = useSyntapseStore((s) => s.toggleCognitiveModal);
  const isGapDrawerOpen = useSyntapseStore((s) => s.isGapDrawerOpen);
  const explanationDepth = useSyntapseStore((s) => s.explanationDepth);
  const cognitiveProfile = useSyntapseStore((s) => s.cognitiveProfile);
  const theme = useSyntapseStore((s) => s.theme);
  const toggleTheme = useSyntapseStore((s) => s.toggleTheme);
  const messages = useSyntapseStore((s) => s.messages);

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text(`Syntapse Notes: ${topicName}`, 15, 20);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    
    let yPos = 30;
    messages.forEach((msg) => {
      if (yPos > 270) {
        doc.addPage();
        yPos = 20;
      }
      
      const role = msg.role === 'user' ? 'YOU:' : 'TEACHER:';
      doc.setFont("helvetica", "bold");
      doc.text(role, 15, yPos);
      yPos += 7;
      
      doc.setFont("helvetica", "normal");
      const lines = doc.splitTextToSize(msg.content, 180);
      doc.text(lines, 15, yPos);
      yPos += (lines.length * 6) + 10;
    });
    
    doc.save(`Syntapse_Notes_${topicName?.replace(/ /g, '_')}.pdf`);
  };



  return (
    <div className="h-screen flex flex-col">
      {/* Chamber Header — matches wireframe */}
      <header
        className="h-16 flex-shrink-0 z-30 flex items-center justify-between gap-3 px-5 py-3 border-b min-w-0"
        style={{
          background: 'var(--header-bg)',
          backdropFilter: 'blur(8px)',
          borderColor: 'var(--surface-border)',
        }}
      >
        {/* Left Section: Back Button + Topic Title */}
        <div className="flex items-center gap-2.5 min-w-0 flex-1 overflow-hidden">
          <button
            onClick={() => setView('dashboard')}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-sm text-secondary-c flex-shrink-0 whitespace-nowrap"
            style={{ background: 'transparent' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Chambers</span>
          </button>

          <div className="h-5 w-px flex-shrink-0" style={{ background: 'var(--surface-border)' }} />

          <div className="flex items-center gap-2 min-w-0 flex-1 overflow-hidden">
            <Zap className="w-4 h-4 text-amber-c flex-shrink-0" />
            <h1
              className="font-serif text-sm sm:text-base md:text-lg font-bold truncate text-primary-c min-w-0"
              title={`Cogniflow // ${topicName}`}
            >
              Cogniflow // {topicName}
            </h1>
          </div>
        </div>

        {/* Right Section: Badges & Control Buttons */}
        <div className="flex items-center gap-2 flex-shrink-0 whitespace-nowrap ml-auto">
          <span
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border text-primary-c whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            <Layers className="w-3 h-3 text-amber-c flex-shrink-0" />
            Depth: {explanationDepth || 'Deep'}
          </span>
          <span
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border text-primary-c whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            <Activity className="w-3 h-3 text-mint-c flex-shrink-0" />
            Agent: Active
          </span>
          <span
            className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono font-medium border text-primary-c whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            [ {buildDnaTag(cognitiveProfile)} ]
          </span>
          <button
            onClick={toggleFocusMode}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-colors text-xs font-semibold text-primary-c whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Toggle Focus Mode (Cmd/Ctrl+B)"
          >
            {focusMode ? (
              <EyeOff className="w-3.5 h-3.5" />
            ) : (
              <Eye className="w-3.5 h-3.5" />
            )}
          </button>
          <button
            onClick={handleDownloadPDF}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-xs font-semibold text-primary-c border whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Download Session as PDF"
          >
            <Download className="w-3.5 h-3.5 text-mint-c flex-shrink-0" />
            <span className="hidden md:inline">Export PDF</span>
          </button>
          <button
            onClick={() => toggleCognitiveModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-xs font-semibold text-primary-c border whitespace-nowrap flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Cognitive Footprint Settings"
          >
            <Dna className="w-3.5 h-3.5 text-amber-c flex-shrink-0" />
            <span className="hidden md:inline">Footprint</span>
          </button>
          <button
            onClick={(e) => toggleTheme(e)}
            className="p-1.5 rounded-lg border transition-colors text-primary-c flex-shrink-0"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="w-3.5 h-3.5 text-amber-c" />
            ) : (
              <Moon className="w-3.5 h-3.5 text-primary-c" />
            )}
          </button>
        </div>
      </header>

      {/* Single-Pane Workspace */}
      <div className="flex-1 flex overflow-hidden relative justify-center bg-surface-0">
        <div className="w-full max-w-6xl h-full flex flex-col">
          <div className="flex-1 overflow-hidden">
            <ChatTerminal />
          </div>
        </div>
      </div>

      {/* Sticky 3D Gap Button */}
      {!focusMode && <Sticky3DGapButton />}

      {/* Gap Analysis Drawer */}
      <AnimatePresence>
        {isGapDrawerOpen && <GapAnalysisDrawer />}
      </AnimatePresence>
    </div>
  );
}
