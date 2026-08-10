# 🧬 Syntapse Cognitive Engine — Complete Frontend Master Specification & Agent Prompt

> **File Purpose:** This document compiles all context, architectural flows, API contracts, design systems, ASCII CLI wireframes, component schemas, and animation guidelines from all previous planning conversations. It is designed to be passed directly to an autonomous AI UI Developer Agent (e.g., Lovable, Bolt, Cursor, v0) to build the complete frontend.

---

## 🏛️ 1. ARCHITECTURE & SYSTEM OVERVIEW

### System Vision
Syntapse is an **Agentic Socratic Learning IDE** powered by a multi-agent LangGraph backend exposed via FastAPI. Unlike standard linear chatbots, Syntapse performs background web research, forensic cognitive profiling, topic guardrail isolation, and real-time gap analysis.

### Dual-Memory System
1. **Global Cognitive Profile (User DNA):** Mapped once during onboarding (`Phase 0`). Defines how the user thinks (analogies vs. technical specs, deductive vs. inductive pacing). Applied universally across all chat rooms.
2. **Local Chamber Session (Topic Isolation):** Partitioned learning rooms (`Phase 1`). Data from "Topic A" (Transformers) never bleeds into "Topic B" (B-Trees).

### FastAPI Backend Endpoints API Contract
Base URL: `http://localhost:8000` (CORS enabled)

| Method | Endpoint | Request Payload | Response Schema | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/calibrate` | `{ modal_text: string }` | `{ status, cognitive_profile: dict }` | Runs Agent 1 to extract user's Global Cognitive Profile. |
| `POST` | `/session/start` | `{ session_id: str, topic_name: str, cognitive_profile: dict, user_context?: str }` | `{ status, session_id }` | Seeds persistent LangGraph state checkpointer for thread. |
| `GET` | `/session/{session_id}` | URL Param: `session_id` | `{ session_id, topic_name, messages: [], cognitive_profile, last_teacher_probe }` | Hydrates chat stream & state on page refresh / load. |
| `POST` | `/chat` | `{ session_id: str, message: str }` | `{ session_id, message: str, probe?: dict, depth?: str }` | Executes multi-agent graph turn & returns AI text + Socratic probe. |
| `POST` | `/gap_analysis` | `{ session_id: str }` | `{ session_id, diagnostic_summary: str, suggestions: [{ topic, reason }] }` | Runs Agent 3B to detect missing subtopics & actionable chips. |

---

## 🎨 2. DESIGN SYSTEM & COLOR PALETTE ("Groovy Book Reader")

Combines **editorial book reader comfort** (zero eye strain) with **groovy, ultra-modern dark accents**.

### Palette Tokens
* **Canvas Background:** `#121316` (Deep Warm Obsidian — avoids harsh black contrast)
* **Book Card Surface:** `#1B1C22` (Soft Warm Charcoal for reading panels & tabs)
* **Warm Ink Text:** `#E8E5DF` (Soft Warm Parchment White for high legibility)
* **Groovy Amber Accent:** `#FFB020` (Socratic Probes, Analogy Bridges & Key Takeaways)
* **Electric Violet:** `#8B5CF6` (Agent 4 Teacher Telemetry & Mind Mapping Nodes)
* **Terracotta Spice:** `#F97316` (3D Gap Analysis Button, Warnings & Attention Anchors)
* **Emerald Mint:** `#10B981` (Verified ArXiv Facts & Validation Success)
* **Sepia Light Mode (Optional Toggle):** Paper `#FAF6F0`, Ink `#1C1917`, Amber `#D97706`.

### Typography Strategy
* **Editorial Headings & Analogy Takeaways:** `Lora` or `Newsreader` (Google Fonts).
* **Body Reading Text:** `Plus Jakarta Sans` or `Inter` (`fontSize: 16px`, `lineHeight: 1.7`).
* **Code & Technical Socratic Blocks:** `JetBrains Mono` with warm syntax highlighting.

---

## 🎬 3. ANIMATION & 3D GRAPHICS STACK

1. **Lenis (`lenis.dev`):** Smooth inertia scrolling across chat streams and lesson canvases.
2. **Motion (`motion.dev`):** Fluid page transitions, component mounting, and chat message stream effects.
3. **React Spring (`react-spring.dev`):** Physics-based tactile springs for buttons, drawers, and tabs.
4. **Three.js / React Three Fiber (`threejs.org`):**
   - **Sticky 3D Gap Orb:** A persistent 3D floating orb/button (`[⚡ ANALYZE KNOWLEDGE GAP]`) anchored on the chat interface that rotates, emits particles, and reacts to clicks.
   - **Mesmerizing Latency Loader:** During API calls (`/calibrate`, `/session/start`, `/chat`), triggers a 3D morphing particle/neural graph animation over the submit button so the user feels captivated while waiting.
5. **GSAP (`gsap.com`):** Complex scroll-triggered animations and multi-stage loading timelines.

---

## 🖥️ 4. CLI VISUAL WIREFRAMES & LAYOUT BLUEPRINTS

```
===============================================================================================
SCREEN 1: THE CALIBRATION GATE (Phase 0 — Cognitive DNA Onboarding)
===============================================================================================

+-----------------------------------------------------------------------------------------------+
| 🧬 SYNTAPSE // COGNITIVE FORENSIC ENGINE v9.0                        [ Mode: Uncalibrated ]   |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|   +---------------------------------------------------------------------------------------+   |
|   | 📚 CALIBRATE YOUR LEARNING DNA                                                        |   |
|   | Explain a complex concept you already understand. We will reverse-engineer your       |   |
|   | preferred analogies, pacing, and structural depth.                                    |   |
|   +---------------------------------------------------------------------------------------+   |
|                                                                                               |
|   [ EDITORIAL ESSAY INPUT CANVAS ]                                                            |
|   +---------------------------------------------------------------------------------------+   |
|   | In B-Trees, data is structured in balanced multi-way search trees where nodes         |   |
|   | maintain sorted keys. I think of this like a library catalog system...                |   |
|   +---------------------------------------------------------------------------------------+   |
|                                                                                               |
|   [ 🚀 3D MESMERIZING SUBMIT BUTTON ] (3D morphing neural core during POST /calibrate)        |
|   +---------------------------------------------------------------------------------------+   |
|   |  [ ⚡ INITIATE COGNITIVE MAPPING ]                                                     |   |
|   +---------------------------------------------------------------------------------------+   |
|                                                                                               |
+-----------------------------------------------------------------------------------------------+

===============================================================================================
SCREEN 2: CHAMBER DASHBOARD & ROOM INITIALIZER (Phase 1)
===============================================================================================

+-----------------------------------------------------------------------------------------------+
| 🏛️ SYNTAPSE // CHAMBER DASHBOARD                      [ Profile: DNA-ANALOGY-DEDUCTIVE-v9 Active ]|
+-----------------------------------------------------------------------------------------------+
|  SIDEBAR: CHAMBER ROOMS             |  MAIN WORKSPACE: INITIALIZE NEW CHAMBER                 |
|                                     |                                                         |
|  [+] + New Learning Chamber         |  Target Topic:                                          |
|  -------------------------------    |  [ Transformer Attention Mechanisms                  ]  |
|  [•] Transformer Architecture       |                                                         |
|      Turn 4 • Active                |  Optional Context:                                      |
|  [•] B-Tree Indexing                |  [ I know matrix dot products, but struggle with Q,K,V ]|
|      Turn 12 • Saved                |                                                         |
|  [•] Async IO in Python             |  [ 🔮 3D ORB SUBMIT: INITIALIZE CHAMBER (POST /start) ]   |
|      Archived                       |  (Spins into a 3D vortex while background pre-fetches)  |
+-----------------------------------------------------------------------------------------------+

===============================================================================================
SCREEN 3: ACTIVE SYNTAPSE IDE & CHAT CHAMBER (Phase 3 — With Sticky 3D Gap Button)
===============================================================================================

+-----------------------------------------------------------------------------------------------+
| ⚡ CHAMBER: Transformer Attention Mechanisms  | Depth: Deep  | Agent: Active                  |
+-----------------------------------------------------------------------------------------------+
| PANE A: LESSON CANVAS & CODE        | PANE B: SOCRATIC CHAT STREAM & TERMINAL                 |
| (Editorial Lora / Newsreader font)  |                                                         |
|                                     | [ TELEMETRY HUD: Agent 4 Teaching | Agent 6 Scraped ArXiv]|
| ## 1. The Library Analogy           | ------------------------------------------------------- |
| Self-Attention works like a query   | USER: How does scaling by sqrt(d_k) work?               |
| catalog search where Queries (Q)... |                                                         |
|                                     | AGENT 4 (Teacher):                                      |
| ```python                           | Scaling prevents large dot products from pushing        |
|  def scaled_dot_product(Q, K, V):   | softmax into zero-gradient regions.                     |
|      scores = matmul(Q, K.T) / ?    |                                                         |
| ```                                 | +-----------------------------------------------------+ |
|                                     | | 🎯 SOCRATIC PROBE CARD                             | |
|                                     | | Q: What happens if softmax gradients explode?       | |
|                                     | +-----------------------------------------------------+ |
|                                     |                                                         |
|                                     | [ TERMINAL INPUT ]                                      |
|                                     | > Type response or question...           [ Send ]       |
|                                     |                                                         |
|                                     |  ====================================================== |
|                                     |  | 🔮 STICKY 3D GAP BUTTON (Floating Persistent FAB)  | |
|                                     |  | [ ⚡ ANALYZE KNOWLEDGE GAP ]  (Rotates in 3D canvas) | |
|                                     |  ====================================================== |
+-----------------------------------------------------------------------------------------------+

===============================================================================================
SCREEN 4: KNOWLEDGE GAP DIAGNOSTIC OVERLAY (Phase 4 — Triggered by 3D FAB)
===============================================================================================

+-----------------------------------------------------------------------------------------------+
| ACTIVE CHAMBER WORKSPACE (SCREEN 3)                                                           |
|                                                                                               |
|        =============================================================================          |
|        | ⚡ KNOWLEDGE GAP DIAGNOSTIC OVERLAY (Triggered via POST /gap_analysis)    |          |
|        |                                                                           |          |
|        | DIAGNOSTIC SUMMARY:                                                       |          |
|        | "You have mastered Scaled Dot-Product math, but exhibit friction on       |          |
|        |  Multi-Head Linear Projection matrices."                                  |          |
|        |                                                                           |          |
|        | ACTIONABLE SUGGESTION CHIPS (1-Click Chat Injections):                    |          |
|        |                                                                           |          |
|        |  [ 📌 Explore Gap: Multi-Head Linear Projections ]                         |          |
|        |     Reason: Missed validation probe on weight dimensions                  |          |
|        |                                                                           |          |
|        |  [ 📌 Explore Gap: Decoder Causal Masking ]                                |          |
|        |     Reason: Topic not yet covered in current session                      |          |
|        |                                                                           |          |
|        |  [ ✖ CLOSE DIAGNOSTIC DRAWER ]                                            |          |
|        =============================================================================          |
|                                                                                               |
|                                               [ 🔮 3D GAP BUTTON (Pulsing Active State) ]    |
+-----------------------------------------------------------------------------------------------+
```

---

## 🧩 5. COMPONENT HIERARCHY & ZUSTAND STORE SCHEMA

### Component Tree
```
src/
├── components/
│   ├── 3d/
│   │   ├── Sticky3DGapButton.tsx       # R3F Canvas for the floating 3D Gap FAB
│   │   └── MesmerizingLoader.tsx       # 3D morphing particle aura for button wait states
│   ├── calibration/
│   │   ├── CalibrationGate.tsx         # Screen 1 container
│   │   ├── EssayCanvas.tsx             # Textarea editor for onboarding text
│   │   └── ProfileRadarCard.tsx        # Visualizer for extracted Cognitive DNA
│   ├── dashboard/
│   │   ├── ChamberDashboard.tsx        # Screen 2 container
│   │   ├── RoomInitializer.tsx         # Form for topic_name & user_context
│   │   └── SessionHistoryList.tsx      # Sidebar listing active/past threads
│   ├── chamber/
│   │   ├── ActiveChamberIDE.tsx        # Screen 3 workspace container
│   │   ├── LessonCanvas.tsx            # Pane A: Editorial Markdown & Code Viewer
│   │   ├── TelemetryHUD.tsx            # Live agent node execution timeline
│   │   ├── ChatTerminal.tsx            # Pane B: Interactive chat stream & input
│   │   └── SocraticProbeCard.tsx       # Injected interactive diagnostic question card
│   └── gap_analysis/
│       └── GapAnalysisDrawer.tsx       # Screen 4: Glassmorphic slide-over drawer
├── store/
│   └── useSyntapseStore.ts             # Global Zustand state management
└── services/
    └── api.ts                          # Fetch / Axios wrapper for FastAPI endpoints
```

### Zustand Store Schema (`useSyntapseStore.ts`)
```typescript
interface SyntapseStore {
  // Global Profile State (Phase 0)
  cognitiveProfile: Record<string, any> | null;
  setCognitiveProfile: (profile: Record<string, any>) => void;

  // Active Session State (Phase 1)
  activeSessionId: string | null;
  topicName: string | null;
  sessionsList: Array<{ session_id: string; topic_name: string }>;
  
  // Chat & Lesson Stream State (Phase 3)
  messages: Array<{ role: 'user' | 'ai'; content: string }>;
  lastProbe: { question: string; target_concept?: string } | null;
  explanationDepth: 'Foundational' | 'Deep' | null;
  
  // Agentic Telemetry Flags
  isAgentThinking: boolean;
  activeAgentNode: 'Agent 1' | 'Agent 2' | 'Agent 4' | 'Agent 5' | 'Agent 6' | null;
  statusMessage: string;

  // Gap Analysis Overlay State (Phase 4)
  isGapDrawerOpen: boolean;
  gapAnalysisData: {
    diagnostic_summary: string;
    suggestions: Array<{ topic: string; reason: string }>;
  } | null;
  
  // Actions
  startNewSession: (sessionId: string, topic: string) => void;
  toggleGapDrawer: (isOpen?: boolean) => void;
}
```

---

## 🤖 6. COPY-PASTE AGENT PROMPT FOR FRONTEND DEVELOPER

```markdown
# SYSTEM PROMPT: BUILD SYNTAPSE AGENTIC LEARNING IDE FRONTEND

You are an expert AI Frontend Engineer specializing in React, Next.js/Vite, TypeScript, TailwindCSS/Vanilla CSS, and Three.js/React Three Fiber.

Your task is to build the full frontend for **Syntapse Cognitive Engine** adhering strictly to the specification below:

### KEY REQUIREMENTS:
1. **Design System:** Implement the "Groovy Book Reader" aesthetic (`#121316` Dark Obsidian, `#1B1C22` Warm Charcoal, `#FFB020` Warm Amber, `#8B5CF6` Electric Violet, `#F97316` Terracotta, `#10B981` Emerald Mint). Use `Lora`/`Newsreader` font for lesson headings & analogy bridges, and `Plus Jakarta Sans` for body text.
2. **Animation & 3D Stack:**
   - Use **Lenis** for smooth inertia scrolling.
   - Use **Motion** for smooth page and message transitions.
   - Use **React Three Fiber (Three.js)** for a persistent, floating 3D Gap Analysis Orb (`Sticky3DGapButton.tsx`) anchored on the chat interface.
   - Use **3D Particle Loaders (`MesmerizingLoader.tsx`)** over submit buttons during API execution (`/calibrate`, `/session/start`, `/chat`) for latency masking.
3. **Screens to Build:**
   - **Screen 1 (Calibration Gate):** Onboarding essay textarea + 3D submit button calling `POST /calibrate`.
   - **Screen 2 (Chamber Dashboard):** Past sessions sidebar (`GET /session/{id}`) + new topic initializer form calling `POST /session/start`.
   - **Screen 3 (Active Syntapse IDE):** Dual-pane layout (Pane A: Lesson Canvas; Pane B: Telemetry HUD + Socratic Chat Terminal). Injects interactive `SocraticProbeCard.tsx` when `probe` object is present in `/chat` output. Features persistent 3D Gap FAB button.
   - **Screen 4 (Gap Diagnostic Overlay):** Slide-over glassmorphic drawer triggered by 3D Gap FAB calling `POST /gap_analysis`. 1-click suggestion chips populate & fire the chat terminal.
4. **Backend API Integration:** Point all fetch calls to `http://localhost:8000`. Maintain state in Zustand (`useSyntapseStore.ts`).

Now, proceed to build the complete frontend codebase.
```
