# Syntapse Cognitive Engine — Project README

> **An adaptive multi-agent pedagogical system.** Syntapse teaches any technical topic by first reverse-engineering how a user thinks, then orchestrating 6 specialized AI agents to deliver personalized Socratic instruction grounded in live web research.

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # Fill in API keys
python main.py
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI runs at http://localhost:5173
```

---

## Environment Variables (`backend/.env`)

| Variable | Model Used | Agent |
|---|---|---|
| `MODEL_1_MAPPER_KEY` | Groq Llama 3.3 70B | Agent 1 — Cognitive Mapper |
| `MODEL_2_WAVELENGTH_KEY` | Groq Llama 3.3 70B | Agent 2 — Wavelength Setter |
| `MODEL_3_GAP_ANALYZER_KEY` | NVIDIA Llama 3.1 8B | Agent 3B — Gap Analyzer |
| `MODEL_4_TEACHER_KEY` | Groq Llama 3.3 70B | Agent 4 — Teacher |
| `MODEL_5_GUARDRAIL_KEY` | Groq Llama 3.3 70B | Agent 5 — Guardrail |
| `MODEL_6_RESEARCHER_KEY` | NVIDIA Llama 3.1 8B | Agent 6 — Researcher |
| `TAVILY_KEY_1/2/3` | Tavily Web Search API | Agent 6 (round-robin) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | LangGraph (stateful multi-agent graph) |
| **API** | FastAPI + Uvicorn |
| **LLM — Reasoning Agents** | Groq `llama-3.3-70b-versatile` |
| **LLM — Synthesis Agents** | NVIDIA NIM `meta/llama-3.1-8b-instruct` |
| **Web Research** | Tavily Search API |
| **Frontend Framework** | React 18 + TypeScript + Vite |
| **Styling** | TailwindCSS v3 |
| **State Management** | Zustand (with localStorage persistence) |
| **Animations** | Framer Motion |
| **Validation** | Pydantic v2 |

---

## Agent Roster

| Agent | Name | Model | Role |
|---|---|---|---|
| **Agent 1** | Cognitive Mapper | Groq 70B | Forensic cognitive profile extraction from calibration essay |
| **Agent 2** | Wavelength Setter | Groq 70B | Generates optimized Tavily search queries |
| **Agent 3** | Cognitive Validator | Groq 70B | Evaluates probe responses, updates hypothesis map |
| **Agent 3B** | Gap Analyzer | NVIDIA 8B | Diagnoses structural knowledge gaps from full session history |
| **Agent 4** | Teacher | Groq 70B | Core adaptive Socratic tutor |
| **Agent 5** | Guardrail | Groq 70B | Intent classification (5-class), 0-token bypass for greetings/meta |
| **Agent 6** | Researcher | NVIDIA 8B | Live Tavily web research + fact synthesis |

---

## Key Architectural Decisions

### 0-Token Guardrail Bypass
Greetings (`hi`, `thanks`, `ok`) and meta-queries (`what can you do`) are intercepted **before** the LLM via regex string matching. No tokens consumed, no LLM latency.

### Cognitive Profile Persistence
Agent 1 runs once per user. The profile persists in frontend localStorage and is re-injected to the backend on every session start — surviving server restarts without re-calibration.

### Research Deduplication
Before triggering a Tavily search, Agent 6 checks existing `research_catalog.canonical_subtopics`. If ≥2 topic words overlap, the search is skipped to avoid burning API credits on duplicate research.

### Research Catalog Cap
Only the last 3 research entries are passed to the Teacher prompt per turn to prevent context window explosion over long sessions.

### Hypothesis Lifecycle
`active_cognitive_hypotheses` are pruned every Teacher call: resolved hypotheses (support/refute from Validator) are removed, and the dict is capped at 5 active items.

### Phantom Probe Guard
`last_teacher_probe` is only written to state after a successful teacher response — not on API fallback. This prevents the Cognitive Validator from evaluating phantom probes the user never saw.

### Gap Analysis Guard
`gap_analyzer_node` requires ≥2 user messages before running. On empty sessions, it returns a clean "ask more questions first" message instead of hallucinated gaps.

---

## Prompt Skills

All agent system prompts are stored as markdown in `prompt_skills/`:

| File | Agent |
|---|---|
| `cognitive_mapper_vr_holy_grail.md` | Agent 1 |
| `guardrail_vr_holy_grail.md` | Agent 5 |
| `teacher_tutor_vr_holy_grail.md` | Agent 4 |
| `gap_analyzer_vr_holy_grail.md` | Agent 3B |
| `research_pipeline_vr_holy_grail.md` | Agent 6 |

---

## Limitations

- **No database persistence** — Session message history lives in LangGraph in-memory state. Server restart clears history (cognitive profile survives in localStorage)
- **No streaming** — Teacher responses return as complete JSON, not streamed tokens
- **Cold-start profile** — Single calibration essay = ~5 evidence items. Cognitive profile strengthens with probe interaction over 8-10 turns
- **CORS** — Currently set to `allow_origins=["*"]` for local development. Lock down before production deployment

---

## File Map

```
project_agents/
├── backend/
│   ├── main.py           # FastAPI app + all endpoints
│   ├── graph.py          # LangGraph graph definition + edge routing
│   ├── nodes.py          # All agent node implementations
│   ├── orchestrator.py   # Agent 1 calibration (runs outside graph)
│   ├── state.py          # SyntapseChamberState definition
│   ├── schemas.py        # Pydantic schemas for all agent outputs
│   ├── config.py         # Model configuration + API client factories
│   ├── prompts.py        # Prompt loading utility
│   └── requirements.txt  # Python dependencies
├── frontend/
│   └── src/
│       ├── components/   # React UI components
│       ├── services/     # api.ts — all backend API calls
│       ├── store/        # useSyntapseStore.ts — Zustand state
│       └── types/        # TypeScript type definitions
├── prompt_skills/        # All agent system prompt markdown files
├── project_information/  # Architecture documentation
├── test_chamber/         # Manual test scripts and sample data
└── .gitignore
```
