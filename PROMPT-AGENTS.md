# SYNAPSE MULTI-AGENT ARCHITECTURE & PROMPT SKILL MAP

> **File Path:** `AGENTS.md` (Root Directory)  
> **System Name:** Syntapse Adaptive Pedagogical Engine  
> **Purpose:** Developer & architectural reference detailing which Agent calls which `.md` prompt skill file, when it triggers in the lifecycle, the LLM model used, and its execution flow.

---

## 🗺️ 1. Master Agent & Prompt Skill Index

| Agent ID & Name | Python Implementation | Prompt Skill Markdown File | Execution Trigger | Primary LLM / API Engine | Output Contract |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 1: Cognitive Mapper** | `orchestrator.py: live_agent_1_mapper` | `prompt_skills/cognitive_mapper_vr_holy_grail.md` | **Phase 0** (`POST /calibrate`) when user submits essay | Groq Llama-3.3-70b-versatile | `cognitive_profile.json` (Cognitive DNA & Mind Blueprint) |
| **Agent 3A: Cognitive Validator** | `nodes.py: cognitive_validator_node` | `prompt_skills/cognitive_validator_vr_holy_grail.md` | **Phase 1** (`POST /chat`) Start of turn (Node 1) | Groq Llama-3.1-8b-instant | `last_validation` (Probe grade & Bayesian weight update) |
| **Agent 5: Scope Guardrail** | `nodes.py: guardrail_node` | `prompt_skills/guardrail_vr_holy_grail.md` | **Phase 1** (`POST /chat`) Immediately after Agent 3A | Groq Llama-3.1-8b-instant | `GuardrailDecision` (`classification`, `requires_deep_research`) |
| **Agent 2: Scope Sizer** | `nodes.py: wavelength_setter_node` | `prompt_skills/wavelength_setter_vr_holy_grail.md`<br>`prompt_skills/tavily_api_mini_manual.md` | **Phase 1** (`POST /chat`) Triggered if `requires_deep_research == True` | Groq Llama-3.3-70b-versatile | `search_plan` (`MACRO`/`MICRO` wavelength & `agent_6_queries`) |
| **Agent 6: Researcher** | `nodes.py: research_node` | `prompt_skills/research_pipeline_vr_holy_grail.md` | **Phase 1** (`POST /chat`) Immediately after Agent 2 | **Tavily Client API** + NVIDIA Llama 3.1 8B | `research_catalog` (Structured `source_supported_facts`) |
| **Agent 4: Mentality Teacher** | `nodes.py: teacher_node` | `prompt_skills/teacher_tutor_vr_holy_grail.md` | **Phase 2** (`POST /chat`) After Guardrail/Researcher OR Critic Redraft | Groq Llama-3.3-70b-versatile | `TeacherResponsePayload` (`answer`, depth, `socratic_question`) |
| **Agent 3C: Quality Critic** | `nodes.py: quality_critic_node` | `prompt_skills/quality_critic_vr_holy_grail.md` | **Phase 2** (`POST /chat`) Immediately AFTER Agent 4 draft | **NVIDIA Llama 3.1 8B Instruct** (NIM API) | `QualityCriticPayload` (`quality_passed`, `actionable_feedback`) |
| **Agent 3B: Gap Analyzer** | `nodes.py: gap_analyzer_node` | `prompt_skills/gap_analyzer_vr_holy_grail.md` | **On-Demand** (`POST /gap_analysis`) When user clicks FAB UI button | NVIDIA / Groq Llama 3.1 8B | `KnowledgeGapAnalysis` (Diagnostic gap cards) |

---

## 🔄 2. Execution Flow & Lifecycle Pipeline

```text
[PHASE 0: CALIBRATION & ONBOARDING]
User Essay ──► Agent 1 (cognitive_mapper_vr_holy_grail.md) ──► cognitive_profile.json

[PHASE 1 & 2: ACTIVE CHAT PIPELINE (POST /chat)]
User Chat Input
    │
    ▼
1. Agent 3A (cognitive_validator_vr_holy_grail.md)      [Grades previous probe answer]
    │
    ▼
2. Agent 5  (guardrail_vr_holy_grail.md)                [Intent filter & sets requires_deep_research]
    │
    ├──► (If Fast Path: requires_deep_research == False) ──────────┐
    │                                                              │
    └──► (If Research Path: requires_deep_research == True)        │
          │                                                        │
          ▼                                                        ▼
       3. Agent 2 (wavelength_setter_vr_holy_grail.md +           │
                   tavily_api_mini_manual.md)                       │
          │                                                        │
          ▼                                                        │
       4. Agent 6 (research_pipeline_vr_holy_grail.md)             │
          │                                                        │
          └──────────────────────────┬─────────────────────────────┘
                                     │
                                     ▼
                          5. Agent 4 (teacher_tutor_vr_holy_grail.md)
                                     │
                                     ▼
                          6. Agent 3C (quality_critic_vr_holy_grail.md)
                                     │
                        ┌────────────┴────────────┐
                     (FAIL)                    (PASS)
                        │                         │
                        ▼                         ▼
            Loop Back to Agent 4      Ghost Memory Compressor
           (Pass 1 Redraft Loop)       (0 LLM Calls Utility Node)
                                                  │
                                                  ▼
                                           Return to User
```

---

## 🧠 3. Detailed Agent Breakdown

### Agent 1: Cognitive Mapper (Decompiler)
* **File Loaded:** `prompt_skills/cognitive_mapper_vr_holy_grail.md`
* **When:** Phase 0 onboarding (`POST /calibrate`).
* **Role:** Performs forensic linguistic reverse-engineering of user's writing sample to produce a topic-independent Mind Blueprint (`evidence_ledger`, `clause_structure`, `concrete_first`, `analogy_domain`, `learning_mechanism`, `reasoning_style`).

### Agent 3A: Cognitive Validator (Probe Evaluator)
* **File Loaded:** `prompt_skills/cognitive_validator_vr_holy_grail.md`
* **When:** Entry node of every chat turn (`POST /chat`).
* **Role:** Grades user's answer to previous Socratic probe and updates Bayesian hypothesis weights in state.

### Agent 5: Scope Guardrail (Intent Classifier)
* **File Loaded:** `prompt_skills/guardrail_vr_holy_grail.md`
* **When:** Node 2 of every chat turn (`POST /chat`).
* **Role:** Classifies user query into `IN_BOUNDS`, `OFF_TOPIC_PIVOT`, or `META_QUERY`. Sets `requires_deep_research: True/False`.

### Agent 2: Scope Sizer / Wavelength Setter
* **Files Loaded:** `prompt_skills/wavelength_setter_vr_holy_grail.md` + `prompt_skills/tavily_api_mini_manual.md`
* **When:** Node 3 (only if `requires_deep_research == True`).
* **Role:** Reads `tavily_api_mini_manual.md` to design valid search query JSON specifications (`agent_6_queries`). Does **not** execute HTTP web calls.

### Agent 6: Researcher (RAG Scraping Engine)
* **File Loaded:** `prompt_skills/research_pipeline_vr_holy_grail.md`
* **When:** Node 4 (immediately following Agent 2).
* **Role:** Executes live `TavilyClient.search()` HTTP API calls, scrapes web content, strips fluff, and populates `research_catalog`.

### Agent 4: Mentality Teacher (Socratic Tutor)
* **File Loaded:** `prompt_skills/teacher_tutor_vr_holy_grail.md`
* **When:** Node 5 (after Guardrail/Researcher OR during Critic Redraft pass).
* **Role:** Generates pedagogical explanation and Socratic probe question. Strictly leads with concrete tool anchor and matches user syntax. Injects `REQUIRED_REVISION_STEPS` if redrafting.

### Agent 3C: Quality Critic (Master Auditor)
* **File Loaded:** `prompt_skills/quality_critic_vr_holy_grail.md`
* **When:** Node 6 (immediately after Agent 4 draft).
* **Role:** Audits Teacher draft across 6 dimensions (`cognitive_alignment`, `completeness`, `probe_eval`, `anti_fluff`, `evidence_ledger_audit`). If rejected, passes `quality_critique` and `how_to_fix` instructions back to Agent 4 for a single redraft pass.

### Agent 3B: Knowledge Gap Analyzer
* **File Loaded:** `prompt_skills/gap_analyzer_vr_holy_grail.md`
* **When:** On-demand when user clicks Knowledge Gap FAB button on UI (`POST /gap_analysis`).
* **Role:** Scans chat history and produces interactive diagnostic cards highlighting mastered vs missing subtopics.
