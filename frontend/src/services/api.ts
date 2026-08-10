import type {
  CognitiveProfile,
  Chamber,
  ChatMessage,
  GapAnalysis,
  GapSuggestion,
} from '@/types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const SESSIONS_STORAGE_KEY = 'syntapse_sessions_v1';

const rid = () => crypto.randomUUID();

function getStoredSessions(): Chamber[] {
  try {
    const raw = localStorage.getItem(SESSIONS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveStoredSession(session: Chamber): void {
  try {
    const list = getStoredSessions();
    const existingIdx = list.findIndex((s) => s.id === session.id);
    if (existingIdx >= 0) {
      list[existingIdx] = { ...list[existingIdx], ...session, updated_at: new Date().toISOString() };
    } else {
      list.unshift(session);
    }
    localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(list));
  } catch (e) {
    console.error('Failed to persist session to localStorage', e);
  }
}

/* ──────────────────────────────────────────────────────────────
   Phase 0: Calibration — Calls POST /calibrate
   ────────────────────────────────────────────────────────────── */

export async function calibrate(modalText: string): Promise<CognitiveProfile> {
  try {
    const response = await fetch(`${API_BASE}/calibrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ modal_text: modalText }),
    });

    if (!response.ok) {
      throw new Error(`Calibration server error: ${response.statusText}`);
    }

    const data = await response.json();
    const rawProfile = data.cognitive_profile || {};

    const profile: CognitiveProfile = {
      ...rawProfile,
      id: rid(),
      modal_text: modalText,
      causal_strategy: rawProfile.causal_strategy || 'analogical',
      pacing: rawProfile.pacing || 'moderate',
      complexity: rawProfile.complexity || 'intermediate',
      analogy_style: rawProfile.analogy_style || 'structural',
      structural_depth: rawProfile.structural_depth || 'deep',
      created_at: new Date().toISOString(),
    };

    return profile;
  } catch (error) {
    console.warn('Backend /calibrate failed, falling back to dynamic local calibration:', error);
    return {
      id: rid(),
      modal_text: modalText,
      causal_strategy: 'analogical',
      pacing: 'moderate',
      complexity: 'intermediate',
      analogy_style: 'structural',
      structural_depth: 'deep',
      created_at: new Date().toISOString(),
    };
  }
}

export async function deleteCognitiveProfile(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/calibrate`, { method: 'DELETE' });
    return response.ok;
  } catch (error) {
    console.warn('Backend DELETE /calibrate error:', error);
    return false;
  }
}

/* ──────────────────────────────────────────────────────────────
   Phase 1: Session Start — Calls POST /session/start
   ────────────────────────────────────────────────────────────── */

export async function startSession(
  topicName: string,
  profileId: string | null,
  userContext: string | null,
  cognitiveProfile?: CognitiveProfile | null,
): Promise<Chamber> {
  const sessionId = rid();
  const now = new Date().toISOString();

  const chamber: Chamber = {
    id: sessionId,
    profile_id: profileId,
    topic_name: topicName,
    user_context: userContext,
    status: 'active',
    turn_count: 0,
    explanation_depth: 'Deep',
    created_at: now,
    updated_at: now,
  };

  try {
    await fetch(`${API_BASE}/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        topic_name: topicName,
        cognitive_profile: cognitiveProfile || {},
        user_context: userContext,
      }),
    });
  } catch (e) {
    console.warn('Backend /session/start offline or error:', e);
  }

  saveStoredSession(chamber);
  return chamber;
}

export async function fetchChambers(): Promise<Chamber[]> {
  return getStoredSessions();
}

export async function deleteChamber(chamberId: string): Promise<boolean> {
  try {
    const list = getStoredSessions();
    const updatedList = list.filter((s) => s.id !== chamberId);
    localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updatedList));

    const response = await fetch(`${API_BASE}/session/${chamberId}`, {
      method: 'DELETE',
    });
    return response.ok;
  } catch (error) {
    console.warn('Backend DELETE /session error:', error);
    return false;
  }
}

export async function fetchChamber(
  chamberId: string,
  cognitiveProfile?: CognitiveProfile | null,
): Promise<{ chamber: Chamber; messages: ChatMessage[] } | null> {
  try {
    const response = await fetch(`${API_BASE}/session/${chamberId}`);
    if (response.ok) {
      const data = await response.json();
      const stored = getStoredSessions().find((s) => s.id === chamberId);
      const chamber: Chamber = stored || {
        id: chamberId,
        profile_id: null,
        topic_name: data.topic_name || 'Learning Session',
        user_context: null,
        status: 'active',
        turn_count: (data.messages || []).length,
        explanation_depth: 'Deep',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      const messages: ChatMessage[] = (data.messages || []).map((m: any, idx: number) => ({
        id: `msg-${idx}-${rid()}`,
        chamber_id: chamberId,
        role: m.role === 'user' ? 'user' : 'ai',
        content: m.content,
        probe_question:
          idx === data.messages.length - 1 && data.last_teacher_probe
            ? data.last_teacher_probe.question || data.last_teacher_probe
            : null,
        probe_target_concept: null,
        depth: 'Deep',
        created_at: new Date().toISOString(),
      }));

      return { chamber, messages };
    }

    // Session not found on backend (e.g. server restarted) — auto re-register
    if (response.status === 404 || response.status === 400) {
      const stored = getStoredSessions().find((s) => s.id === chamberId);
      if (stored) {
        console.warn(`Session ${chamberId} not found on backend — re-registering...`);
        try {
          await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: chamberId,
              topic_name: stored.topic_name,
              cognitive_profile: cognitiveProfile || {},
              user_context: stored.user_context,
            }),
          });
        } catch (e) {
          console.warn('Re-registration failed:', e);
        }
        return { chamber: stored, messages: [] };
      }
    }
  } catch (e) {
    console.warn(`GET /session/${chamberId} error:`, e);
  }

  const stored = getStoredSessions().find((s) => s.id === chamberId);
  if (stored) {
    return { chamber: stored, messages: [] };
  }
  return null;
}

/* ──────────────────────────────────────────────────────────────
   Phase 3: Chat Loop — Calls POST /chat
   ────────────────────────────────────────────────────────────── */

interface ChatResult {
  message: ChatMessage;
  telemetrySteps: { agent: string; label: string }[];
}

const TELEMETRY_SEQUENCE = [
  { agent: 'Agent 5', label: 'Validating topic boundaries' },
  { agent: 'Agent 6', label: 'Scraping ArXiv for verified facts' },
  { agent: 'Agent 2', label: 'Mapping knowledge graph nodes' },
  { agent: 'Agent 4', label: 'Synthesizing Socratic lesson' },
];

export async function sendChat(
  chamberId: string,
  message: string,
  topicName: string,
  cognitiveProfile: CognitiveProfile | null,
  onTelemetry: (step: { agent: string; label: string }) => void,
): Promise<ChatResult> {
  const steps = [...TELEMETRY_SEQUENCE];

  // Always emit guardrail step first — it always runs
  onTelemetry({ agent: 'Agent 5', label: 'Validating topic boundaries...' });

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: chamberId,
        message,
        cognitive_profile: cognitiveProfile || undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat HTTP Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // FIX #6: Real telemetry — emit only agents that actually ran
    const realAgents: string[] = data.agents_triggered || [];
    for (const agentLabel of realAgents) {
      const matched = TELEMETRY_SEQUENCE.find((s) => agentLabel.includes(s.agent));
      if (matched && matched.agent !== 'Agent 5') {
        onTelemetry(matched);
        await new Promise((r) => setTimeout(r, 300));
      }
    }

    const probe = data.probe;
    const probeQuestion =
      typeof probe === 'string' ? probe : probe?.question || probe?.probe_question || null;
    const probeConcept =
      typeof probe === 'object' ? probe?.target_concept || probe?.concept || null : null;

    const aiMsg: ChatMessage = {
      id: rid(),
      chamber_id: chamberId,
      role: 'ai',
      content: data.message || 'No response content returned.',
      probe_question: probeQuestion,
      probe_target_concept: probeConcept,
      depth: data.depth || 'Deep',
      created_at: new Date().toISOString(),
    };

    return { message: aiMsg, telemetrySteps: steps };
  } catch (error) {
    const errMsg = error instanceof Error ? error.message : String(error);
    const isMissing =
      errMsg.includes('400') || errMsg.includes('404') || errMsg.includes('Bad Request');
    const friendlyMsg = isMissing
      ? '⚠️ Your session has expired (the backend restarted). Please **refresh the page** to start a new chamber.'
      : `⚠️ Could not reach the backend. Check that the server is running.\n\nError: ${errMsg}`;

    onTelemetry(steps[3]);
    const aiMsg: ChatMessage = {
      id: rid(),
      chamber_id: chamberId,
      role: 'ai',
      content: friendlyMsg,
      probe_question: null,
      probe_target_concept: null,
      depth: 'Deep',
      created_at: new Date().toISOString(),
    };
    return { message: aiMsg, telemetrySteps: steps };
  }
}

/* ──────────────────────────────────────────────────────────────
   Phase 4: Gap Analysis — Calls POST /gap_analysis
   ────────────────────────────────────────────────────────────── */

export async function runGapAnalysis(
  chamberId: string,
  topicName: string,
): Promise<GapAnalysis> {
  try {
    const response = await fetch(`${API_BASE}/gap_analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: chamberId }),
    });

    if (!response.ok) {
      throw new Error(`Gap Analysis error: ${response.statusText}`);
    }

    const data = await response.json();
    const suggestions: GapSuggestion[] = (data.suggestions || []).map((s: any) => ({
      topic: typeof s === 'string' ? s : s.missing_subtopic || s.topic || s.title || 'Subtopic Analysis',
      reason:
        typeof s === 'object' ? s.reason || 'Identified learning boundary' : 'Session friction point',
      button_label: typeof s === 'object' ? s.button_label : undefined,
    }));

    return {
      id: rid(),
      chamber_id: chamberId,
      diagnostic_summary: data.diagnostic_summary || `Diagnostic complete for ${topicName}.`,
      suggestions:
        suggestions.length > 0
          ? suggestions
          : [
              { topic: 'Foundational Boundaries', reason: 'High friction detected during probe validation' },
              { topic: 'Deep Mechanism Integration', reason: 'Topic requires further exploration' },
            ],
      created_at: new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Backend /gap_analysis error:', error);
    const errMsg = error instanceof Error ? error.message : String(error);
    return {
      id: rid(),
      chamber_id: chamberId,
      diagnostic_summary: `⚠️ Gap analysis failed. The session may have expired — please refresh and start a new chamber. Error: ${errMsg}`,
      suggestions: [],
      created_at: new Date().toISOString(),
    };
  }
}
