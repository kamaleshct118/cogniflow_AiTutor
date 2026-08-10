# Syntapse — Frontend Architecture

**Stack:** React 18 + TypeScript + Vite + TailwindCSS + Zustand  
**Last Updated:** 2026-08-09

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── calibration/       # Cognitive profile calibration modal
│   │   ├── chamber/
│   │   │   ├── ChatTerminal.tsx        # Main chat interface
│   │   │   └── SocraticProbeCard.tsx   # Probe question card
│   │   ├── dashboard/         # Session list + new session creation
│   │   ├── gap_analysis/
│   │   │   └── GapAnalysisDrawer.tsx   # Slide-in gap analysis panel
│   │   └── layout/            # Header, theme toggle
│   ├── services/
│   │   └── api.ts             # All backend API calls
│   ├── store/
│   │   └── useSyntapseStore.ts # Zustand global state
│   ├── types/                 # TypeScript interfaces
│   └── App.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## State Management (Zustand with Persistence)

The store (`useSyntapseStore.ts`) uses `zustand/middleware/persist`. The following keys are persisted to **localStorage** across sessions:

| Key | Type | Purpose |
|---|---|---|
| `theme` | `'dark' \| 'sepia'` | UI theme |
| `cognitiveProfile` | `CognitiveProfile \| null` | Full Agent 1 output, re-injected on session start |
| `currentView` | `ScreenView` | Active screen (dashboard / chamber / calibration) |
| `activeSessionId` | `string \| null` | Current LangGraph session ID |
| `topicName` | `string \| null` | Active learning topic |

**Non-persisted state** (in-memory only, lost on page refresh):
- `messages` — chat history
- `isAgentThinking`, `telemetrySteps` — UI loading state
- `gapAnalysisData` — last gap analysis result

---

## Session Lifecycle & Auto-Recovery

1. **Fresh start** → User completes calibration (`POST /calibrate`) → profile stored in Zustand localStorage
2. **Session start** → `POST /session/start` with topic + full cognitive profile → backend registers session in LangGraph memory
3. **Page refresh (backend still running)** → `GET /session/{id}` succeeds → messages restored from backend state
4. **Page refresh (backend restarted)** → `GET /session/{id}` returns 404 → frontend **auto re-registers** the session by calling `POST /session/start` again with the profile from localStorage → user can continue immediately without re-calibrating

---

## API Service (`services/api.ts`)

| Function | Endpoint | Notes |
|---|---|---|
| `calibrate(text)` | `POST /calibrate` | Spreads full backend profile including nested `tutor_directive` |
| `startSession(...)` | `POST /session/start` | Passes full `cognitiveProfile` object |
| `fetchChamber(id, profile)` | `GET /session/{id}` | Auto re-registers on 404 |
| `sendChat(...)` | `POST /chat` | Emits real telemetry from `agents_triggered` response field |
| `runGapAnalysis(...)` | `POST /gap_analysis` | Returns error summary on failure, no fake fallback data |

### Real Telemetry (FIX #6)
`sendChat` now emits **only the agents that actually ran** in a given turn:
- Always emits `Agent 5 (Guardrail)` immediately
- After response arrives, iterates `data.agents_triggered` from backend and emits matched steps
- If only guardrail ran (e.g., greeting), only Agent 5 shows — no fake Agent 6/2/4 animation

---

## Screens / Views

### Dashboard (`currentView: 'dashboard'`)
- Shows list of past sessions from localStorage
- New session form: topic name + optional user context
- Profile status indicator (calibrated / not calibrated)

### Chamber (`currentView: 'chamber'`)
- **ChatTerminal** — full-width chat interface, AI message font `text-base` (16px)
- `Enter` to send, `Shift+Enter` for newline
- Agent thinking indicator with real telemetry steps
- **SocraticProbeCard** — rendered below AI message when probe is returned
- **GapAnalysisDrawer** — slide-in panel triggered by FAB button

### Calibration Modal
- Full-screen overlay
- Textarea for calibration essay
- Submits to `POST /calibrate` → stores profile → closes modal

---

## Design System

| Token | Dark Mode | Sepia Mode | Purpose |
|---|---|---|---|
| `--surface-0` | Deep black | Parchment | Page background |
| `--surface-1` | Dark charcoal | Light parchment | Card/bubble background |
| `--surface-2` | Slightly lighter | Tan | User message bubbles |
| `--accent-amber` | `#F59E0B` | `#92400E` | Primary accent, user labels |
| `--accent-violet` | `#7C3AED` | `#5B21B6` | AI labels |
| `--text-primary` | Off-white | Dark brown | Main text |

**Theme toggle** uses `startViewTransition` API (with fallback) for smooth CSS view transitions.

---

## Known Constraints

- **No message persistence** — chat history lives in LangGraph in-memory state. Server restart = history gone (profile survives in localStorage)
- **No streaming** — responses are returned as complete JSON, not streamed tokens
- **Telemetry is post-response** — agent step animations play after the response arrives, not during
