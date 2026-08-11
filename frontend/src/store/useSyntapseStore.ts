/**
 * ===============================================================================
 * SYNAPSE FRONTEND — Zustand Global Store (useSyntapseStore.ts)
 * ===============================================================================
 * Purpose:
 *   • Central state management store handling chamber lifecycle, chat history,
 *     cognitive profile synchronization, and UI drawer states.
 *
 * Core Logic & Hierarchy:
 *   ├── View & Theme State   : currentView, theme, isFocusMode, isGapDrawerOpen
 *   ├── Session & Profile    : activeSessionId, cognitiveProfile, isCalibrated
 *   ├── Chamber Lifecycle    : createChamber(), selectChamber(), hydrateChamber()
 *   ├── Active Learning Loop : sendMessage(), triggerGapAnalysis(), answerProbe()
 *   └── Backend Sync         : Interacts with API service to persist state across reloads
 * ===============================================================================
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  CognitiveProfile,
  Chamber,
  ChatMessage,
  GapAnalysis,
  AgentNode,
  ExplanationDepth,
  ScreenView,
  ThemeMode,
} from '@/types';
import * as api from '@/services/api';

interface TelemetryStep {
  agent: string;
  label: string;
}

interface SyntapseStore {
  // Theme
  theme: ThemeMode;
  toggleTheme: (event?: React.MouseEvent) => void;

  // Navigation
  currentView: ScreenView;
  setView: (view: ScreenView) => void;

  // Global Profile State (Phase 0)
  cognitiveProfile: CognitiveProfile | null;
  isCalibrating: boolean;
  isCognitiveModalOpen: boolean;
  toggleCognitiveModal: (isOpen?: boolean) => void;

  // Active Session State (Phase 1)
  activeSessionId: string | null;
  topicName: string | null;
  sessionsList: Chamber[];
  isStartingSession: boolean;

  // Chat & Lesson Stream State (Phase 3)
  messages: ChatMessage[];
  lastProbe: { question: string; target_concept?: string } | null;
  explanationDepth: ExplanationDepth;
  chatInput: string;

  // Agentic Telemetry Flags
  isAgentThinking: boolean;
  activeAgentNode: AgentNode;
  statusMessage: string;
  telemetrySteps: TelemetryStep[];

  // Gap Analysis Overlay State (Phase 4)
  isGapDrawerOpen: boolean;
  gapAnalysisData: GapAnalysis | null;
  isGapAnalyzing: boolean;

  // Focus mode
  focusMode: boolean;

  // Actions
  calibrate: (modalText: string) => Promise<void>;
  deleteCognitiveProfile: () => Promise<void>;
  startNewSession: (topic: string, context: string | null) => Promise<void>;
  loadChambers: () => Promise<void>;
  deleteChamber: (chamberId: string) => Promise<void>;
  hydrateChamber: (chamberId: string) => Promise<void>;
  sendChatMessage: (message: string) => Promise<void>;
  setChatInput: (text: string) => void;
  toggleGapDrawer: (isOpen?: boolean) => void;
  runGapAnalysis: () => Promise<void>;
  toggleFocusMode: () => void;
  setStatusMessage: (msg: string) => void;
  setActiveAgent: (agent: AgentNode) => void;
  pushTelemetryStep: (step: TelemetryStep) => void;
  clearTelemetry: () => void;
  resetForNewChamber: () => void;
}

export const useSyntapseStore = create<SyntapseStore>()(
  persist(
    (set, get) => ({
      // Theme
      theme: 'dark',
      toggleTheme: (event) => {
        const nextTheme = get().theme === 'dark' ? 'sepia' : 'dark';
        if (event && event.clientX !== undefined) {
          document.documentElement.style.setProperty('--reveal-x', `${event.clientX}px`);
          document.documentElement.style.setProperty('--reveal-y', `${event.clientY}px`);
        }
        if ('startViewTransition' in document && typeof (document as any).startViewTransition === 'function') {
          (document as any).startViewTransition(() => {
            set({ theme: nextTheme });
          });
        } else {
          set({ theme: nextTheme });
        }
      },

      // Navigation
      currentView: 'dashboard',
      setView: (view) => set({ currentView: view }),

      // Profile
      cognitiveProfile: null,
      isCalibrating: false,
      isCognitiveModalOpen: false,
      toggleCognitiveModal: (isOpen) =>
        set((s) => ({
          isCognitiveModalOpen: isOpen ?? !s.isCognitiveModalOpen,
        })),

      // Session
      activeSessionId: null,
      topicName: null,
      sessionsList: [],
      isStartingSession: false,

      // Chat
      messages: [],
      lastProbe: null,
      explanationDepth: 'Deep',
      chatInput: '',

      // Telemetry
      isAgentThinking: false,
      activeAgentNode: null,
      statusMessage: '',
      telemetrySteps: [],

      // Gap
      isGapDrawerOpen: false,
      gapAnalysisData: null,
      isGapAnalyzing: false,

      // Focus
      focusMode: false,

      // ── Actions ──

      calibrate: async (modalText) => {
        set({ isCalibrating: true, statusMessage: 'Initiating cognitive mapping…' });
        try {
          const profile = await api.calibrate(modalText);
          set({
            cognitiveProfile: profile,
            isCalibrating: false,
            isCognitiveModalOpen: false,
            statusMessage: '',
            currentView: 'dashboard',
          });
        } catch {
          set({
            isCalibrating: false,
            statusMessage: 'Calibration failed. Please try again.',
          });
        }
      },

      deleteCognitiveProfile: async () => {
        set({ isCalibrating: true });
        await api.deleteCognitiveProfile();
        set({ cognitiveProfile: null, isCalibrating: false });
      },

      startNewSession: async (topic, context) => {
        const { cognitiveProfile } = get();
        set({
          isStartingSession: true,
          statusMessage: 'Initializing chamber…',
        });
        try {
          const chamber = await api.startSession(
            topic,
            cognitiveProfile?.id ?? null,
            context,
            cognitiveProfile
          );
          set({
            activeSessionId: chamber.id,
            topicName: chamber.topic_name,
            messages: [],
            lastProbe: null,
            isStartingSession: false,
            statusMessage: '',
            currentView: 'chamber',
          });
          get().loadChambers();
        } catch {
          set({
            isStartingSession: false,
            statusMessage: 'Failed to initialize chamber.',
          });
        }
      },

      loadChambers: async () => {
        const chambers = await api.fetchChambers();
        set({ sessionsList: chambers });

        // Hydrate persistent Cognitive Profile from backend if not currently set in store
        if (!get().cognitiveProfile) {
          const backendProfile = await api.fetchCognitiveProfile();
          if (backendProfile) {
            set({ cognitiveProfile: backendProfile });
          }
        }
      },

      deleteChamber: async (chamberId) => {
        await api.deleteChamber(chamberId);
        get().loadChambers();
        if (get().activeSessionId === chamberId) {
          get().resetForNewChamber();
        }
      },

      hydrateChamber: async (chamberId) => {
        set({ statusMessage: 'Restoring chamber…' });
        try {
          const { cognitiveProfile } = get();
          const result = await api.fetchChamber(chamberId, cognitiveProfile);
          if (!result) {
            set({ statusMessage: 'Chamber not found.' });
            return;
          }
          const lastProbeMsg = [...result.messages]
            .reverse()
            .find((m) => m.probe_question);
          set({
            activeSessionId: result.chamber.id,
            topicName: result.chamber.topic_name,
            messages: result.messages,
            lastProbe: lastProbeMsg
              ? {
                  question: lastProbeMsg.probe_question!,
                  target_concept: lastProbeMsg.probe_target_concept ?? undefined,
                }
              : null,
            statusMessage: '',
            currentView: 'chamber',
          });
        } catch {
          set({ statusMessage: 'Failed to restore chamber.' });
        }
      },

      sendChatMessage: async (message) => {
        const { activeSessionId, topicName } = get();
        if (!activeSessionId || !topicName) return;

        // Optimistic user message
        const optimisticUserMsg: ChatMessage = {
          id: crypto.randomUUID(),
          chamber_id: activeSessionId,
          role: 'user',
          content: message,
          probe_question: null,
          probe_target_concept: null,
          depth: null,
          created_at: new Date().toISOString(),
        };

        set((s) => ({
          messages: [...s.messages, optimisticUserMsg],
          isAgentThinking: true,
          chatInput: '',
          telemetrySteps: [],
          statusMessage: 'Agents are thinking…',
        }));

        try {
          const { cognitiveProfile } = get();
          const result = await api.sendChat(
            activeSessionId,
            message,
            topicName,
            cognitiveProfile,
            (step) => get().pushTelemetryStep(step),
          );

          set((s) => ({
            messages: [...s.messages, result.message],
            isAgentThinking: false,
            activeAgentNode: null,
            statusMessage: '',
            lastProbe: result.message.probe_question
              ? {
                  question: result.message.probe_question,
                  target_concept:
                    result.message.probe_target_concept ?? undefined,
                }
              : s.lastProbe,
          }));
        } catch {
          set({
            isAgentThinking: false,
            statusMessage: 'Agent network error. Please retry.',
          });
        }
      },

      setChatInput: (text) => set({ chatInput: text }),

      toggleGapDrawer: (isOpen) =>
        set((s) => ({
          isGapDrawerOpen: isOpen ?? !s.isGapDrawerOpen,
        })),

      runGapAnalysis: async () => {
        const { activeSessionId, topicName } = get();
        if (!activeSessionId || !topicName) return;

        set({ isGapAnalyzing: true, isGapDrawerOpen: true, gapAnalysisData: null });
        try {
          const gap = await api.runGapAnalysis(activeSessionId, topicName);
          set({ gapAnalysisData: gap, isGapAnalyzing: false });
        } catch {
          set({ isGapAnalyzing: false, statusMessage: 'Gap analysis failed.' });
        }
      },

      toggleFocusMode: () => set((s) => ({ focusMode: !s.focusMode })),

      setStatusMessage: (msg) => set({ statusMessage: msg }),
      setActiveAgent: (agent) => set({ activeAgentNode: agent }),

      pushTelemetryStep: (step) =>
        set((s) => ({
          telemetrySteps: [...s.telemetrySteps, step],
          activeAgentNode: step.agent as AgentNode,
          statusMessage: step.label,
        })),

      clearTelemetry: () => set({ telemetrySteps: [], activeAgentNode: null }),

      resetForNewChamber: () =>
        set({
          activeSessionId: null,
          topicName: null,
          messages: [],
          lastProbe: null,
          telemetrySteps: [],
          isAgentThinking: false,
          activeAgentNode: null,
          statusMessage: '',
          isGapDrawerOpen: false,
          gapAnalysisData: null,
          isGapAnalyzing: false,
          currentView: 'dashboard',
        }),
    }),
    {
      name: 'syntapse-store',
      partialize: (s) => ({
        theme: s.theme,
        cognitiveProfile: s.cognitiveProfile,
        currentView: s.currentView,
        activeSessionId: s.activeSessionId,
        topicName: s.topicName,
      }),
    },
  ),
);
