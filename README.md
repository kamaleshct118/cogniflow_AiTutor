# Syntapse — Adaptive Cognitive Learning Platform

**Version:** 2.2 (Mind Blueprint Edition)  
**Last Updated:** August 2026

---

## 🎯 What Is Syntapse?

Syntapse is an **AI-powered adaptive learning platform** that teaches like a human tutor — by understanding *how* each student thinks, learns, and processes information.

Unlike traditional learning systems that treat all students the same, Syntapse builds a **Cognitive Profile** (a "Mind Blueprint") for each user by analyzing how they write and explain concepts. This profile predicts how they'll approach *any new topic* in the future.

**The Core Idea:** Instead of just teaching *what* to learn, Syntapse teaches *how* the user's mind works.

---

## 🧠 The Problem We Solve

### Traditional Tutoring
- One-size-fits-all explanations
- Can't adapt when a student gets stuck
- No understanding of *why* something is confusing
- Treats students as empty vessels to fill

### Syntapse Approach
- Builds a mental model of each learner
- Predicts where they'll struggle before they do
- Adapts teaching style to match their thinking patterns
- Uses Socratic questioning to reveal misconceptions

---

## 🏗️ System Architecture

### Three Phases

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: CALIBRATION                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  User writes an essay about a topic they understand            │    │
│  │         ↓                                                       │    │
│  │  Agent 1 (Cognitive Mapper) analyzes HOW they think            │    │
│  │         ↓                                                       │    │
│  │  Mind Blueprint saved → Active Hypotheses generated            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: LIVE CHAT LOOP                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  User asks question                                             │    │
│  │         ↓                                                       │    │
│  │  Cognitive Validator (3A) → Guardrail (5) → Teacher (4)        │    │
│  │         ↓                                                       │    │
│  │  [If needed: Wavelength Setter (2) → Researcher (6)]           │    │
│  │         ↓                                                       │    │
│  │  Quality Critic (3C) evaluates → Memory Compressor             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: UTILITIES                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Gap Analyzer (3B) - Identifies knowledge gaps                  │    │
│  │  Memory Compressor - Stores teaching history                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 The 6 Agents

### Agent 1: Cognitive Mapper (The Forensic Analyst)
**Purpose:** Build the Mind Blueprint

- Analyzes user's writing sample (300+ words)
- Extracts evidence of *how* they think:
  - Learning mechanism (sequential vs parallel processing)
  - Reasoning style (causal, analogical, deductive)
  - Error recovery (how they handle mistakes)
  - Metacognition (self-awareness of understanding)
  - Transfer readiness (can they apply learning to new topics?)
- **Output:** `cognitive_dna`, `reverse_engineered_model`, `tutor_directive`

---

### Agent 2: Wavelength Setter (The Scope Tuner)
**Purpose:** Determine learning depth

- Analyzes user's question complexity
- Decides: MACRO (broad overview) vs MICRO (deep dive)
- Generates search queries for research
- **Triggered only** when deep research is needed

---

### Agent 3A: Cognitive Validator (The Probe Grader)
**Purpose:** Evaluate Socratic probe answers

- When teacher asks a question, this grades the user's answer
- Updates cognitive hypotheses (support/refute/neutral)
- Uses Bayesian confidence scoring
- **Key:** Tracks what the user actually understands vs thinks they understand

---

### Agent 3B: Gap Analyzer (The Diagnostic Tool)
**Purpose:** Identify knowledge gaps

- Analyzes conversation history
- Compares against curriculum map
- Generates "Diagnose" cards with missing topics
- **Triggered** via UI button or `/gap_analysis` endpoint

---

### Agent 3C: Quality Critic (The Editor)
**Purpose:** Ensure teaching quality

- Evaluates teacher's response against cognitive profile
- Checks teaching blueprint compliance (concrete → abstract order)
- Validates: no fluff, proper evidence, cognitive alignment
- Enforces max 1 rewrite loop

---

### Agent 4: Teacher (The Adaptive Tutor)
**Purpose:** Generate personalized explanations

- Uses cognitive profile to adapt teaching style
- Generates Socratic probes to test understanding
- Incorporates research facts naturally
- Follows enforced constraints from profile
- **Key Behavior:** Concrete anchor first, then mechanism, then terminology

---

### Agent 5: Guardrail (The Traffic Controller)
**Purpose:** Route user requests appropriately

- Classifies intent: LEARNING, OFF_TOPIC, GREETING, META_QUERY
- Detects when deep research is needed
- Prevents off-topic conversations
- Zero-token bypass for greetings/meta

---

### Agent 6: Researcher (The Auto-Librarian)
**Purpose:** Fetch and synthesize external knowledge

- Uses Tavily search API
- Extracts source-supported facts
- Canonicalizes subtopics
- Caches results to avoid redundant searches
- **Max 2 loops** before teacher must proceed without more research

---

## 📊 The Mind Blueprint Schema

When a user calibrates, we extract this complete profile:

```json
{
  "cognitive_dna": {
    "evidence_ledger": [...],        // Raw observations from writing
    "atomic_evidence_map": {...},    // Clause structure, causal reasoning patterns
    "learning_mechanism": {          // NEW: How they process new info
      "input_processing_style": "sequential_ingestion",
      "concept_anchoring": "example_dependent"
    },
    "reasoning_style": {             // NEW: How they think
      "primary_mode": "causal",
      "directionality": "forward_chaining"
    },
    "error_recovery": {...},          // NEW: How they handle mistakes
    "metacognition": {...},           // NEW: Self-awareness
    "transfer_readiness": {...}       // NEW: Can apply to new topics
  },
  "reverse_engineered_model": {
    "mental_blueprint": {
      "primary_entry_point": "What user reaches for FIRST when learning",
      "cognitive_sequence": "Order of mental operations",
      "bottleneck": "Where they'll get stuck"
    },
    "transfer_prediction": {
      "when_new_topic": "How they'll approach any new topic"
    },
    "predicted_friction_points": [...]
  },
  "tutor_directive": {
    "pedagogical_telemetry": {
      "concept_introduction_order": "CONCRETE_FIRST",
      "analogy_domain": "MECHANICS",
      "pacing_strategy": "SLOW_BUILD"
    },
    "teaching_blueprint": {
      "explanation_structure": "CONCRETE → MECHANISM → TERMINOLOGY → PRACTICE"
    }
  }
}
```

---

## 🔄 Data Flow Example

### Scenario: User asks "How does virtual memory work?"

```
1. USER MESSAGE → Cognitive Validator (3A)
   - No probe from previous turn, so skip validation

2. Guardrail (5) classifies as LEARNING
   - No deep research needed

3. Teacher (4) receives:
   - cognitive_profile (from calibration)
   - active_hypotheses (compiled from profile)
   - research_catalog (if any exists)

4. Teacher generates response:
   - Starts with concrete example (page table code)
   - Explains mechanism (how CPU translates addresses)
   - Adds terminology (TLB, page fault)
   - Ends with Socratic probe

5. Quality Critic (3C) evaluates:
   - Did teacher start with concrete anchor? ✓
   - Did they follow concept_introduction_order? ✓
   - Is response aligned with cognitive_profile? ✓
   - Any fluff/template language? ✗

6. If PASS → Memory Compressor stores ghost record
   If FAIL → Teacher rewrites with critique feedback

7. Response sent to user
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, LangGraph, Pydantic |
| **LLM Providers** | Groq (Llama 3.3), NVIDIA NIM (Llama 3.1) |
| **Search** | Tavily API |
| **Database** | SQLite (sessions), Redis (cache) |
| **Frontend** | React, TypeScript, TailwindCSS, Zustand |
| **3D Graphics** | Three.js (Neural Background) |

---

## 📁 Project Structure

```
v:\PROJECTS\project_agents\
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── graph.py             # LangGraph definition
│   ├── nodes.py             # All 6 agent implementations
│   ├── orchestrator.py      # Agent 1 (Calibration)
│   ├── state.py             # Pydantic state model
│   ├── schemas.py           # All JSON schemas
│   ├── cognitive/           # Profile compilation & validation
│   │   ├── profile_compiler.py
│   │   ├── profile_reducer.py
│   │   └── profile_schema.py
│   └── prompt_skills/       # (moved to root)
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── calibration/ # Calibration UI
│   │   │   ├── chamber/     # Main chat interface
│   │   │   ├── dashboard/   # Session management
│   │   │   └── three/       # 3D background effects
│   │   ├── services/        # API client
│   │   ├── store/           # Zustand state
│   │   └── types/           # TypeScript definitions
│   └── package.json
│
├── prompt_skills/           # Agent system prompts
│   ├── cognitive_mapper_vr_holy_grail.md
│   ├── teacher_tutor_vr_holy_grail.md
│   ├── quality_critic_vr_holy_grail.md
│   ├── guardrail_vr_holy_grail.md
│   ├── gap_analyzer_vr_holy_grail.md
│   └── ...
│
└── project_information/     # Design documents
    ├── AGENT_ARCHITECTURE_AND_FLOW.md
    ├── PROPOSAL_AND_PIPELINE.md
    └── ...
```

---

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
# Set environment variables in .env
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Calibration Flow
1. User navigates to calibration page
2. User writes 300+ words explaining a topic they understand
3. System analyzes writing sample
4. Mind Blueprint generated and stored
5. User enters learning chamber
6. All future explanations adapt to their cognitive profile

---

## 📈 Key Features

| Feature | Description |
|---------|-------------|
| **Mind Blueprint** | Complete model of how user thinks |
| **Bayesian Hypothesis Tracking** | Confidence-weighted understanding tracking |
| **Socratic Probing** | Questions that reveal true understanding |
| **Cognitive Alignment** | Teaching adapts to learning style |
| **Gap Analysis** | Automatic identification of missing knowledge |
| **Research Integration** | Live web search for up-to-date facts |
| **Quality Critics** | Ensures teaching meets cognitive standards |
| **Memory Compression** | Efficient storage of teaching history |

---

## 🔮 Future Enhancements

- [ ] Multi-modal calibration (voice, video)
- [ ] Real-time hypothesis visualization
- [ ] Collaborative learning chambers
- [ ] Adaptive difficulty based on cognitive load
- [ ] Integration with external LMS platforms

---

## 📄 License

This project is proprietary software developed by the Syntapse team.

---

*Built with ❤️ for adaptive learning*