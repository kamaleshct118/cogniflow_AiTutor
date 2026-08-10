export interface CognitiveProfile {
  id: string;
  modal_text: string;
  causal_strategy: string;
  pacing: string;
  complexity: string;
  analogy_style: string;
  structural_depth: string;
  raw_data?: any;
  created_at?: string;
}

export type ChamberStatus = 'active' | 'saved' | 'archived';

export interface Chamber {
  id: string;
  profile_id: string | null;
  topic_name: string;
  user_context: string | null;
  status: ChamberStatus;
  turn_count: number;
  explanation_depth: string;
  created_at: string;
  updated_at: string;
}

export type MessageRole = 'user' | 'ai';

export interface ChatMessage {
  id: string;
  chamber_id: string;
  role: MessageRole;
  content: string;
  probe_question: string | null;
  probe_target_concept: string | null;
  depth: string | null;
  created_at: string;
}

export interface GapSuggestion {
  topic: string;
  reason: string;
  button_label?: string;
}

export interface GapAnalysis {
  id: string;
  chamber_id: string;
  diagnostic_summary: string;
  suggestions: GapSuggestion[];
  created_at: string;
}

export type AgentNode =
  | 'Agent 1'
  | 'Agent 2'
  | 'Agent 4'
  | 'Agent 5'
  | 'Agent 6'
  | null;

export type ExplanationDepth = 'Foundational' | 'Deep' | null;

export type ScreenView = 'calibration' | 'dashboard' | 'chamber';

export type ThemeMode = 'dark' | 'sepia';

export function buildDnaTag(profile: CognitiveProfile | null): string {
  if (!profile) return 'Uncalibrated';
  const analogy = profile.analogy_style.toUpperCase();
  const strategy = profile.causal_strategy.toUpperCase();
  return `DNA-${analogy}-${strategy}-v9`;
}
