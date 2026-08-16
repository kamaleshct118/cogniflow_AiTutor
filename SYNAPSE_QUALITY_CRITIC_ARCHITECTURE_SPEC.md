# Syntapse Master Agent Architecture: Actor-Critic Specification

This document provides the definitive, single unified architectural flow specification of the Syntapse multi-agent engine, centered around **Onboarding Calibration (Agent 1)**, **Chamber Initialization**, the **Teacher-Critic Pair (Agent 4 & Agent 3C)**, the **Research Subsystem (Agent 2 & Agent 6)**, and the **Ghost Memory Compressor**.

---

## 1. Architectural Philosophy & Full Lifecycle Overview

Syntapse manages the entire user journey through 3 distinct phases:
1. **Phase 1: Onboarding Calibration**: **AGENT 1 (Cognitive Mapper)** reverse-engineers the user's writing sample to build their **Cognitive DNA** (`cognitive_profile.json`).
2. **Phase 2: Chamber Initialization**: `/session/start` registers the `topic_name` (e.g. `DBMS(MySQL)`) and hydrates the session state with the active `cognitive_profile`.
3. **Phase 3: Active Agentic Chat Loop**: LangGraph orchestrates **Agent 3A (Validator)**, **Agent 5 (Guardrail)**, **Agent 4 (Teacher Actor)**, **Agents 2/6 (Research Subsystem)**, **Agent 3C (Quality Critic)**, and **Ghost Compressor**.

---

## 2. Architectural Flow Diagrams

### 2.1 Simplified High-Level Flow (For Easy Understanding)
This diagram represents the conceptual, human-readable flow of how the agents collaborate to answer a single user message.

```text
       ┌───────────────┐
       │ [User Speaks] │
       └───────┬───────┘
               │
               ▼
       ┌───────────────┐
       │   AGENT 3A    │ ──► Grades previous Socratic probe
       │  (Validator)  │
       └───────┬───────┘
               │
               ▼
       ┌───────────────┐
       │   AGENT 5     │ ──► Checks safety & intent
       │  (Guardrail)  │
       └───────┬───────┘
               │
         ┌─────┴─────┐
         │           │
 [Needs Research]  [Simple Question]
         │           │
         ▼           │
 ┌───────────────┐   │
 │ AGENTS 2 & 6  │   │
 │ (Web Search)  │   │
 └───────┬───────┘   │
         │           │
         ▼           ▼
 ┌───────┴───────────┴───┐
 │       AGENT 4         │◄──┐
 │      (Teacher)        │   │
 │   Drafts the Answer   │   │
 └───────────┬───────────┘   │
             │               │
             ▼               │
 ┌───────────────────────┐   │
 │       AGENT 3C        │   │
 │   (Quality Critic)    │   │
 │ Audits Teacher's draft│   │
 └───────────┬───────────┘   │
             │               │
       ┌─────┴─────┐         │
     [FAIL]      [PASS]      │
 (Forces Rewrite)  │         │
       │           │         │
       └───────────┼─────────┘
                   ▼
           ┌───────────────┐
           │ UTILITY NODE  │ ──► Saves 1KB context ghost
           │(Ghost Memory) │
           └───────┬───────┘
                   │
                   ▼
                [ END ]
```

---

### 2.2 The Master Unified Execution Map (Complete Technical Flow)
This diagram maps exactly to the strict LangGraph edge-routing defined in `backend/graph.py`, including conditional loops and fallback routes.

```text
          [ONBOARDING: POST /calibrate]
                        │
                        ▼
            ┌───────────────────────┐
            │ AGENT 1: Cognitive    │
            │ Mapper (Essay DNA)    │
            └───────────┬───────────┘
                        │ (Persists cognitive_profile.json)
                        ▼
          [CHAMBER INIT: POST /session/start]
                        │
                        ▼
            ┌───────────────────────┐
            │ Chamber Setup & State │
            │ Profile Hydration     │
            └───────────┬───────────┘
                        │
                        ▼
          [ACTIVE CHAT: POST /chat]
                        │
                        ▼
                     [START]
                        │
                        ▼
            ┌───────────────────────┐
            │ AGENT 3A: Validator   │ (Grades Previous Socratic Probe)
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ AGENT 5: Guardrail    │ (Safety & Intent Check)
            └───────────┬───────────┘
                        │
          ┌─────────────┴─────────────┐
          │   route_from_guardrail()  │
          └─────────────┬─────────────┘
          ┌─────────────┼─────────────┐
   (GAP ANALYSIS)  (RESEARCH)    (NO RESEARCH)
          │             │             │
          ▼             ▼             │
    ┌───────────┐ ┌───────────┐       │
    │ AGENT 3B  │ │ AGENT 2   │       │
    │ Gap Engine│ │ Wavelength│       │
    └─────┬─────┘ └─────┬─────┘       │
          │             │             │
       [ END ]          ▼             │
                  ┌───────────┐       │
                  │ AGENT 6   │       │
                  │ Researcher│       │
                  └─────┬─────┘       │
                        │             │
                        ▼             ▼
                  ┌─────────────────────┐◄──────┐
                  │ AGENT 4: Teacher    │       │
                  │ (Response Engine)   │◄─┐    │
                  └──────────┬──────────┘  │    │
                             │             │    │
                   ┌─────────┴─────────┐   │    │
                   │ Needs Fallback    │   │    │
                   │ Web Research?     │   │    │
                   └────┬─────────┬────┘   │    │
                        │         │        │    │
                  (YES) │         │ (NO)   │    │
                        ▼         │        │    │
                  ┌───────────┐   │        │    │
                  │ AGENT 2&6 │   │        │    │
                  │ Fallback  │   │        │    │
                  └─────┬─────┘   │        │    │
                        │         │        │    │
                        └─────────┼────────┘    │
                                  ▼             │
                        ┌──────────────────┐    │
                        │ AGENT 3C: Critic │    │
                        │ (Quality Audit)  │    │
                        └─────────┬────────┘    │
                                  │             │
                      ┌───────────┴───────────┐ │
                  (FAIL: count < 1)         (PASS)
                      │                       │
                      └───────────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ UTILITY NODE:    │
                                    │ Ghost Memory     │
                                    │ Compressor       │
                                    └─────────┬────────┘
                                              │
                                              ▼
                                           [ END ]
```

---

## 3. Detailed Lifecycle Execution Logic

### Phase 1: Calibration (Agent 1 - Cognitive Mapper)
* **Trigger**: `POST /calibrate` with raw user writing essay.
* **Execution**: Extracts clause structure, causal reasoning patterns, abstraction ladder movement, epistemic markers, and seed hypotheses (`H_CAUSAL`, `H_ABSTR`, `H_KNOW`).
* **Output**: Writes `cognitive_profile.json` to disk (`Layer 2 persistence`) and database.

### Phase 2: Chamber Initialization & Hydration
* **Trigger**: `POST /session/start` with `topic_name` (e.g. `DBMS(MySQL)`).
* **Execution**: Registers chamber metadata and **hydrates the session state** with the user's `cognitive_profile`.

### Phase 3: Active Turn Loop Execution

#### 1. AGENT 3A (Cognitive Validator)
* **Trigger**: Automatic at turn start.
* **Action**: Grades user probe answers if an active probe exists; updates Bayesian hypothesis weights in `cognitive_profile`.

#### 2. AGENT 5 (Scope Guardrail)
* **Trigger**: Automatic after Agent 3A.
* **Action**: Validates topic safety; routes to Agent 3B for gap analysis or Agent 4 for chat turns.

#### 3. AGENT 4 (Teacher - Initial Check)
* **Action**: Assesses factual readiness. If facts are missing $\rightarrow$ sets `requires_deep_research = True`.

#### 4. AGENT 2 (Wavelength) & AGENT 6 (Deep Researcher)
* **Trigger**: Triggered when `requires_deep_research == True` AND `research_attempts < 2`.
* **Action**: Agent 2 writes search plan $\rightarrow$ Agent 6 executes Tavily API search and appends factual snippets into `research_catalog`. Hard-capped at **Max 2 search passes per turn**.

#### 5. AGENT 4 (Teacher - Drafting Phase)
* **Action**: Synthesizes concrete-anchor-first response draft using loaded facts.

#### 6. AGENT 3C (Quality Critic Node)
* **Trigger**: Runs immediately after Agent 4 drafts a response.
* **Target Engine & API**: NVIDIA Llama 3.1 8B Instruct API (`MODEL_3C_QUALITY_CRITIC_KEY` in `.env`).
* **Payload Evaluated**:
  * `USER_QUERY`: User's original query or prompt.
  * `PROBE_EVALUATION_CONTEXT`: Object containing `PROBE_QUESTION`, `USER_ANSWER`, `TARGET_CONCEPT`, and `EXPECTED_EVIDENCE` (if user is answering a probe).
  * `TEACHER_DRAFT_RESPONSE`: The draft generated by Agent 4 (`answer`, `explanation_depth`, `concepts_covered`, `socratic_question`).
  * `RESEARCH_CATALOG_FACTS`: Background technical facts retrieved by Agent 6 (if any).
  * `COGNITIVE_MAPPER_PROFILE`: Active Cognitive DNA profile, concrete anchor mandates, and tutor directives.
* **Action**: Audits draft on 4 dimensions (*Fact Grounding*, *Prompt Completeness*, *Anti-Fluff Enforcement*, and *Profile Alignment*).
* **Routing (`route_from_quality_check`)**:
  * **`FAIL` (count < 1)**: Sets `quality_critique` feedback in state and **loops directly back to Agent 4 (Drafting Phase)**. Web search is bypassed.
  * **`PASS`**: Proceeds directly to the **Ghost Memory Compressor Utility Node**.

#### 7. UTILITY NODE (Ghost Memory Compressor)
* **Trigger**: Triggered on EVERY completed conversation turn immediately after Agent 3C Quality Critic approves the draft (`PASS`).
* **Action**: Extracts `concepts_covered`, `core_explanation` (truncated to 500 chars), `probe_id`, and `evidence_boundary` from `last_teacher_response`. Appends a lightweight **~1KB `teacher_ghost` record** to `teacher_memory`, resets `research_attempts = 0`, and clears temporary `last_teacher_response`.
* **Termination**: Saves SQLite checkpoint $\rightarrow$ `[END]` (Renders response in UI).

---

## 4. Summary of Full Agent Roster & Roles

| Node / Agent Name | Role | Position in Flow | Trigger / Action |
| :--- | :--- | :--- | :--- |
| **AGENT 1: Cognitive Mapper** | DNA Extractor | Onboarding (`/calibrate`) | Extracts Epistemic DNA $\rightarrow$ `cognitive_profile.json`. |
| **Chamber Hydration** | State Initializer | Session Setup (`/session/start`) | Hydrates `topic_name` & `cognitive_profile` into state. |
| **AGENT 3A: Validator** | User Probe Auditor | Turn Start (Automatic) | Grades user probe answers $\rightarrow$ updates profile weights. |
| **AGENT 5: Scope Guardrail** | Intent Controller | After Agent 3A (Automatic) | Classifies intent & topic safety. |
| **AGENT 4: Mentality Teacher** | Actor / Engine | Chat Turns (Automatic) | Evaluates research need & drafts personalized response. |
| **AGENT 2: Wavelength Setter** | Search Strategist | `requires_deep_research == True` | Defines search depth & writes domain queries. |
| **AGENT 6: Deep Researcher** | Fact Extractor | `requires_deep_research == True` | Runs Tavily search $\rightarrow$ appends facts to `research_catalog`. |
| **AGENT 3C: Quality Critic** | Teacher Draft Auditor | After Agent 4 Draft | Audits Teacher draft; loops directly back to Agent 4 if flawed. |
| **Ghost Memory Compressor** | Context Optimizer | Utility Node (After Critic PASS) | Compresses approved draft into 1KB `teacher_ghost` record. |
| **`[END]`** | Termination Point | Graph Exit | Flushes SQLite state & returns JSON to UI client. |
| **AGENT 3B: Gap Analyzer** | Mid-Session Auditor | On-Demand (`/gap_analysis`) | Diffs chat history vs topic map $\rightarrow$ renders action cards. |
