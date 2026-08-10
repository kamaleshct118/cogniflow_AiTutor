# Syntapse Agent Flow — Brutal Honest Analysis

## The Actual Data Flow (What Happens Where)

### Phase 0: Calibration (Before Any Chat)

```
User writes essay about RAG in the Cognitive Modal
         │
         ▼
Frontend sends `modal_text` (the raw essay string)
         │  POST /calibrate  { modal_text: "we apply rag when..." }
         ▼
orchestrator.py → live_agent_1_mapper(modal_text)
         │
         │  Sends the raw essay to Groq Llama-3.3-70b
         │  with the cognitive_mapper_vr_holy_grail.md system prompt
         ▼
LLM returns a JSON cognitive profile:
  - cognitive_dna.evidence_ledger (quotes + observations)
  - cognitive_dna.atomic_evidence_map (clause_structure, causal_reasoning, abstraction_ladder)
  - epistemic_signature (certainty_markers, concrete_anchor_dependence)
  - reverse_engineered_model (transfer_prediction, predicted_friction_points)
  - tutor_directive (pedagogical_telemetry, enforced_constraints, detected_knowledge_gaps)
         │
         ▼
Frontend receives it, spreads it into a CognitiveProfile object,
saves it in Zustand store + localStorage
```

### Phase 0 → Phase 1: Session Start

```
User picks a topic: "langraph"
User optionally types topic context text
         │
         │  POST /session/start {
         │    session_id: UUID,
         │    topic_name: "langraph",
         │    cognitive_profile: { ...the entire profile from Phase 0... },
         │    user_context: "..." (optional topic text)
         │  }
         ▼
main.py → start_session()
  Creates the LangGraph state with:
    - cognitive_profile = the profile dict from the request body
    - topic_name = "langraph"
    - messages = [SystemMessage(user_context)] if user_context provided
    - everything else initialized empty
  Writes this into the LangGraph MemorySaver checkpointer
```

> [!IMPORTANT]
> **Your question: "Where does the topic text input box go?"**
>
> The `user_context` field in `SessionStartRequest` is where the topic text gets sent. In `main.py` line 135-136, if `user_context` is present, it becomes a `SystemMessage` prepended to the conversation. But here's the thing — **no agent ever explicitly reads this SystemMessage**. It just sits as the first message in the `messages` list. The Teacher receives the last 5 messages of chat history (`messages[-5:]`), so this system message would only be visible to the teacher during the first ~4 exchanges, then it scrolls off the window. **It's not prominently wired into anything.** It's a silent context injection that gets drowned out quickly.

### Phase 1: The Chat Loop (Every User Message)

```
User types: "explain about langraph"
         │
         │  POST /chat { session_id: UUID, message: "explain about langraph" }
         ▼
main.py → syntapse_app.invoke({ messages: [HumanMessage("explain about langraph")] })
         │
         │  LangGraph starts the graph from START node
         ▼
┌──────────────────────────────────────────────┐
│ NODE 1: cognitive_validator_node()           │
│                                              │
│ Checks: is there a last_teacher_probe?       │
│ If no probe → returns {} (does nothing)      │
│ If probe exists but type ≠                   │
│   "pedagogical_validation" → clears probe    │
│ If pedagogical_validation → evaluates user   │
│   response against the hypothesis, emits     │
│   CognitiveEvent, updates profile            │
│                                              │
│ On first message: ALWAYS skips (no probe yet)│
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ NODE 2: guardrail_node()                     │
│                                              │
│ 1. Deterministic check: is it a greeting?    │
│    ("hi", "hello", etc) → sets is_greeting   │
│ 2. Deterministic check: is it a meta query?  │
│    ("what can you do") → sets is_meta        │
│ 3. Otherwise → LLM call to Groq:            │
│    Classifies as IN_BOUNDS, OFF_TOPIC_PIVOT, │
│    REQUIRES_DEEP_RESEARCH, etc.              │
│                                              │
│ Output: { is_off_topic, is_greeting,         │
│           is_meta, requires_deep_research }  │
└──────────────────┬───────────────────────────┘
                   │
                   │  route_from_guardrail() decides:
                   │
            ┌──────┼───────┐
            │      │       │
         greeting/ │    requires_deep_research=true
         meta/     │       │
         off_topic │       ▼
            │      │  ┌─────────────────────────┐
            │      │  │ wavelength_setter_node() │
            │      │  │ Generates search queries │
            │      │  │ for Tavily               │
            │      │  └────────┬────────────────┘
            │      │           │
            │      │           ▼
            │      │  ┌─────────────────────────┐
            │      │  │ research_node()          │
            │      │  │ Runs Tavily search       │
            │      │  │ Synthesizes facts via    │
            │      │  │ NVIDIA Llama-3.1-8b      │
            │      │  │ Dumps into               │
            │      │  │ research_catalog[]       │
            │      │  └────────┬────────────────┘
            │      │           │
            ▼      ▼           ▼
┌──────────────────────────────────────────────┐
│ NODE: teacher_node()                         │
│                                              │
│ IF is_greeting → static greeting, return     │
│ IF is_meta → static meta response, return    │
│ IF is_off_topic → rejection message, return  │
│                                              │
│ OTHERWISE (the real teaching path):          │
│                                              │
│ 1. Reads cognitive_profile from state        │
│ 2. Extracts:                                 │
│    - tutor_directive.pedagogical_telemetry   │
│    - tutor_directive.enforced_constraints    │
│    - reverse_engineered_model.               │
│      predicted_friction_points               │
│    - reverse_engineered_model.               │
│      transfer_prediction                     │
│ 3. Packages these as "compiled_teacher_policy│
│ 4. Adds chat history (last 5 messages)       │
│ 5. Adds research_catalog (last 3 entries)    │
│ 6. Adds teacher_memory (last 8 ghost records)│
│ 7. Sends ALL of this to Groq Llama-3.3-70b  │
│    with the teacher system prompt            │
│                                              │
│ LLM returns:                                 │
│  - answer (the teaching text)                │
│  - explanation_depth                         │
│  - concepts_covered                          │
│  - evidence_boundary                         │
│  - socratic_question (with probe_type,       │
│    probe_mode, tests_hypothesis)             │
│  - requires_research_fallback                │
│                                              │
│ Formats answer + evidence_boundary +         │
│ socratic_question into one AIMessage         │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ NODE: memory_compressor_node()               │
│                                              │
│ Takes the teacher's response and compresses  │
│ it into a "ghost record" (topic, depth,      │
│ concepts_taught, core_explanation[:500])      │
│ Appends to teacher_memory[]                  │
│ Resets research_attempts to 0                │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
                  END → Response sent to frontend
```

---

## Now the Brutal Truth About the Cognitive Profile

### Does it actually work? What does it really do?

Let me trace exactly what happens with your RAG essay, step by step.

**Step 1 — Agent 1 (Mapper) genuinely analyzes your essay.** The LLM reads your RAG explanation and produces evidence-grounded observations. Looking at the output in your console logs, it extracted 5 evidence items (E01-E05) with quotes, observations, hypotheses, and confidence levels. It identified your causal reasoning pattern ("mechanistic causal reasoning"), your abstraction movement ("fluid bidirectional"), and your knowledge organization ("hierarchical with some associative"). **This part is real work. The LLM is genuinely analyzing your writing.**

**Step 2 — The profile gets stored.** The frontend receives it and saves it in localStorage. When you start a session on "langraph", the frontend sends the entire profile back to the backend in `POST /session/start`.

**Step 3 — The Teacher receives the profile.** In `teacher_node()` (lines 520-556), the teacher constructs a `teacher_context` dict that contains:

```json
{
  "active_hypotheses": {},
  "pedagogical_telemetry": {
    "concept_introduction_order": "Introduce the concept of RAG and its purpose...",
    "conceptual_step_size": "Break down complex concepts into smaller...",
    "analogy_domain": "Use analogies related to data processing..."
  },
  "enforced_constraints": ["Constraint 1: Ensure the user understands...", "Constraint 2: ..."],
  "predicted_friction_points": ["Friction 1: ...", "Friction 2: ..."],
  "transfer_prediction": "Given the observed reasoning..."
}
```

This gets stuffed into the prompt under `compiled_teacher_policy`.

### Your Core Question: "If the user learns topic X, what happens when topic Y comes — does the cognitive profile solve this?"

> [!CAUTION]
> **Brutal answer: The cognitive profile is being _passed_ to the teacher, but its actual influence on the teaching output is almost entirely dependent on whether the LLM _chooses_ to follow it.** There is zero programmatic enforcement.

Here's what I mean:

1. **The profile IS extracted correctly.** Agent 1 does analyze your essay and outputs real observations. ✅

2. **The profile IS transmitted to the Teacher.** The `compiled_teacher_policy` is included in the Teacher's prompt payload. ✅

3. **But the Teacher is a single LLM call that receives the policy as _one field among many_.** The Teacher prompt (`teacher_tutor_vr_holy_grail.md`) has **zero mention** of `compiled_teacher_policy`, `pedagogical_telemetry`, or `enforced_constraints`. The system prompt tells the teacher to "adapt precisely to the user's cognitive DNA" but **never tells it HOW to read the policy payload or what to do with specific fields**. The teacher prompt is entirely about the 9-step reasoning pipeline (detect ambiguity → identify intent → determine depth → build answer → gather evidence → explain → ask socratic question). The cognitive profile just rides along in the JSON input and the LLM may or may not pay attention to it.

4. **The "transfer prediction" is a string like:** *"Given the observed reasoning, the user will likely struggle with handling ambiguous or uncertain input data, and may rely heavily on the embedding model for vector conversion."* **This is RAG-specific nonsense when applied to "langraph".** The mapper analyzed a RAG essay, so its friction predictions are about RAG concepts. When the user switches to langraph, those friction predictions are irrelevant — they're about embeddings and vector databases, not about graph nodes and reducers.

5. **The `profile_compiler.py` is DEAD CODE.** The function `compile_raw_profile()` that would translate the raw forensic profile into structured `active_hypotheses` (with teaching policies per hypothesis) is **never called anywhere**. It sits in the codebase doing nothing. This means the sophisticated hypothesis → teaching policy pipeline that was designed (`HypothesisState` with `teaching_policy.concept_introduction_order`, `conceptual_step_size`, `representation_priority`, `analogy_policy`) is **completely disconnected** from the runtime.

6. **The `active_cognitive_hypotheses` starts empty `{}` every session.** Looking at `main.py` line 153: `"active_cognitive_hypotheses": {}`. Since `profile_compiler` is never called, there are never any hypotheses loaded from the profile. The Cognitive Validator (Agent 3) can only validate hypotheses that already exist, but none are ever seeded. The Teacher can only test hypotheses that are in `active_hypotheses`, but it's always empty. **The entire hypothesis feedback loop is a dead circuit.**

### Summary — What Actually Influences Teaching

| Component | Is it Real? | Does it Matter? |
|-----------|-------------|-----------------|
| Essay analysis (Agent 1) | ✅ Yes, real LLM analysis | ⚠️ Produces real observations but... |
| Profile stored in state | ✅ Yes, transmitted correctly | ⚠️ ...it arrives at the teacher but... |
| Teacher reads policy | ✅ Yes, included in prompt | ❌ ...the teacher prompt has no instructions for it |
| Transfer prediction | ⚠️ Generated but topic-locked | ❌ Predictions about RAG are useless for langraph |
| Profile compiler | ❌ Dead code, never called | ❌ Hypotheses never seeded |
| Cognitive validator feedback loop | ❌ Empty hypotheses = no validation | ❌ Agent 3 always skips |
| Topic text (user_context) | ⚠️ Injected as SystemMessage | ❌ Scrolls off after ~4 turns |

### The Bottom Line

The cognitive profile is a **cosmetic passenger**. The data flows correctly through the pipes, but:

1. **The Teacher's system prompt doesn't tell it how to use the profile fields.** It's hoping the LLM will figure it out from the JSON key names.
2. **The profile is topic-contaminated.** A profile built from a RAG essay makes RAG-specific predictions. When applied to langraph, the constraints like "ensure user understands embedding model biases" are meaningless.
3. **The hypothesis loop is broken.** `profile_compiler.py` would seed initial hypotheses from the profile, but it's never wired up. Without hypotheses, the Cognitive Validator always skips, and the Teacher never runs `pedagogical_validation` probes that test real learning patterns.
4. **There is no topic-independent cognitive extraction.** The mapper prompt *asks* for topic-independent patterns (clause structure, causal reasoning, abstraction movement), and these ARE somewhat transferable. But the `pedagogical_telemetry` and `enforced_constraints` that Agent 1 generates are always contaminated by the topic the essay was about.

### What Would Need to Change to Make It Real

1. **Wire up `profile_compiler.py`** — Call `compile_raw_profile()` on the Agent 1 output and seed `active_cognitive_hypotheses` from it at session start.
2. **Add profile-reading instructions to the Teacher prompt** — Tell the teacher explicitly: "Read `compiled_teacher_policy.pedagogical_telemetry` and follow its `concept_introduction_order`."
3. **Separate topic-specific vs topic-independent observations** — The mapper should split its output into "how this person thinks" (transferable) vs "what this person knows about RAG" (not transferable).
