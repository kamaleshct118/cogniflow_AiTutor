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
        className="flex items-center gap-3 px-5 py-3 border-b"
        style={{
          background: 'var(--header-bg)',
          backdropFilter: 'blur(8px)',
          borderColor: 'var(--surface-border)',
        }}
      >
        <button
          onClick={() => setView('dashboard')}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-sm text-secondary-c"
          style={{ background: 'transparent' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Chambers</span>
        </button>

        <div className="h-5 w-px" style={{ background: 'var(--surface-border)' }} />

        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-c" />
          <h1 className="font-serif text-lg font-bold truncate max-w-[200px] sm:max-w-none text-primary-c">
            Cogniflow // {topicName}
          </h1>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border text-primary-c"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            <Layers className="w-3 h-3 text-amber-c" />
            Depth: {explanationDepth || 'Deep'}
          </span>
          <span
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border text-primary-c"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            <Activity className="w-3 h-3 text-mint-c" />
            Agent: Active
          </span>
          <span
            className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono font-medium border text-primary-c ml-2"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
          >
            [ {buildDnaTag(cognitiveProfile)} ]
          </span>
          <button
            onClick={toggleFocusMode}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-colors text-xs font-semibold text-primary-c"
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
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-xs font-semibold text-primary-c border ml-1"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Download Session as PDF"
          >
            <Download className="w-3.5 h-3.5 text-mint-c" />
            <span className="hidden md:inline">Export PDF</span>
          </button>
          <button
            onClick={() => toggleCognitiveModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg transition-colors text-xs font-semibold text-primary-c border ml-1"
            style={{ background: 'var(--surface-1)', borderColor: 'var(--surface-border)' }}
            title="Cognitive Footprint Settings"
          >
            <Dna className="w-3.5 h-3.5 text-amber-c" />
            <span className="hidden md:inline">Footprint</span>
          </button>
          <button
            onClick={(e) => toggleTheme(e)}
            className="p-1.5 rounded-lg border transition-colors ml-1"
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
