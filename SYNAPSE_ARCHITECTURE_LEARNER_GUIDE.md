# Syntapse Multi-Agent Learning System — Complete Architecture Guide

A learner-friendly walkthrough of how Cogniflow's adaptive tutoring pipeline actually works. No code — just concepts, flow, and why each piece exists.

---

## 1. The Big Picture — What Is This System?

### The Core Problem It Solves

Most AI tutors give everyone the same answer. If you already understand the basics, you get bored. If you're struggling, you get lost. The system doesn't adapt to *you*.

Syntapse solves this by doing something different: **it reverse-engineers how you think first**, then tailors every explanation and every question to match your mental model.

### How It Does This

1. **Before anything else** — You write a calibration essay. The system analyzes it to build your **Cognitive DNA** (how you reason, what analogies you use, where you'll likely get stuck).
2. **Every question you ask** — Goes through a pipeline of specialized AI agents, each doing one specific job.
3. **After every answer** — The system evaluates whether your response shows understanding or confusion, and updates its model of how you learn.

---

## 2. Complete Lifecycle — From Calibration to End of Turn

This section walks through the entire journey: from your first essay submission, through session creation, and every step of an active chat turn.

---

### Phase A: Onboarding & Cognitive Calibration (Agent 1)

This happens only once — when you first use the system.

**Step 1: You submit a writing sample**

You write an essay explaining a concept you know well — something like how RAG works, or how databases handle queries. The system wants to see *how you think*, not just what you know.

**Step 2: Agent 1 (Mapper) extracts your cognitive fingerprint**

Agent 1 reads your essay and analyzes it for:

- **Epistemic Signature** — How do you construct arguments? Do you use deduction, induction, analogy, or abduction?
- **Causal Reasoning style** — Do you think sequentially (A causes B causes C) or emergently (A and B combine to create C)?
- **Abstraction Ladder movement** — Do you ground concepts concretely first, then climb to abstraction? Or do you jump to high-level principles and drill down later?
- **Certainty Markers** — How confident are you? Do you hedge ("it might", "I think") or assert ("definitely", "always")?
- **Knowledge Organization** — How do you structure your ideas? Chronologically? By components? By cause-effect chains?
- **Atomic Evidence Map** — What kinds of evidence do you cite? Code examples? Real-world analogies? Research papers?
- **Friction Points** — Where do you trip up? What concepts confuse you?

**Step 3: The profile is saved**

Agent 1 produces a JSON object called `cognitive_profile.json` and saves it to disk. This profile will now be attached to every session you create.

---

### Phase B: Session Initialization & Chamber Setup

**Step 4: You start a new learning chamber**

You enter a topic (e.g., "Linux kernel memory management") and click "Start Session". The backend calls `/session/start`.

**What happens behind the scenes:**

- A unique `session_id` (also called `thread_id`) is generated
- This session is registered with LangGraph's SQLite checkpointer (`syntapse_sessions.db`)
- Your cognitive profile is loaded from disk and injected into the LangGraph state
- The system is now ready to handle messages

**Why this matters:** The profile is your "teaching DNA". Every agent in the pipeline reads it and adjusts its output to match how you learn.

---

### Phase C: Active Chat Turn Pipeline

This is the core execution flow. It happens on **every single message** you send.

---

#### Step 1: You submit a message

You type a question in the chat, like: *"How does the Linux kernel handle page faults?"*

---

#### Step 2: Agent 3A (Cognitive Validator) — The Question It Answers

**"Did the user just answer a Socratic probe from the previous turn?"**

**When it runs:** Before anything else, on every message.

**Why it exists:** The Teacher (Agent 4) asks you questions to check understanding. But the system needs a way to *grade your answer* and learn from it. That's what this agent does.

**What it actually does:**

1. Checks: *"Was there a pedagogical validation probe in the previous turn?"*
2. If yes: takes your answer, compares it to what a correct understanding should look like
3. Generates a validation signal:
   - `response_quality`: "strong" | "adequate" | "partial" | "weak" | "incorrect"
   - `hypothesis_effect`: "support" | "contradict" | "inconclusive"
4. Creates a **cognitive event** — a record that gets added to your cognitive profile
5. If there are active hypotheses (testable guesses about your learning style), it **updates their weights**

**Concrete example:**

- *Turn 1:* Teacher asks: *"If a process requests 1MB but only uses 100KB, what's charged against its limit?"*
- *Turn 2:* You answer: *"The whole 1MB because allocation = charging"*
- *Validator sees this:* Your answer shows a misunderstanding. The hypothesis "this user understands memory accounting" gets a **contradiction** event.

**What it produces:**

```json
{
  "response_quality": "weak",
  "hypothesis_effect": "contradict",
  "cognitive_event": { "event_id": "...", "probe_id": "...", "target_concept": "memory_charging" },
  "last_validation": { "probe_response_status": "incorrect", "content_gap": "..." }
}
```

**Where it goes next:** Always passes to the Guardrail (Agent 5).

---

#### Step 3: Agent 5 (Guardrail) — The Question It Answers

**"What kind of message is this, and where should it go next?"**

**When it runs:** Immediately after the Cognitive Validator, on every message.

**Why it exists:** Different messages need different handling. A greeting shouldn't trigger a research pipeline. A question about kernel internals needs different treatment than "what can you do?". The Guardrail makes these routing decisions.

**What it actually does — three layers:**

1. **Fast bypass (0 LLM tokens):** If it's a common greeting ("hi", "hello", "hey"), immediately mark as greeting and skip LLM call.
2. **Meta bypass (0 LLM tokens):** If it's a meta-query ("what can you do?", "help"), immediately mark as meta and skip LLM call.
3. **LLM classification:** For everything else, call the LLM to classify into one of these:
   - On-topic technical query
   - Off-topic
   - Needs deep research
   - Gap analysis trigger (user clicked the FAB button)

**What it produces:**

```json
{
  "is_greeting": false,
  "is_meta": false,
  "is_off_topic": false,
  "requires_deep_research": true,
  "trigger_gap_analysis": false,
  "classification": "needs_research"
}
```

**Where it goes next:** The conditional edge function `route_from_guardrail()` reads these flags and decides the next destination.

---

#### Branch Point: Where Does the Query Go?

Based on the Guardrail flags, the query takes one of four paths:

| If this flag is true... | Go to... | What happens |
|------------------------|----------|--------------|
| `trigger_gap_analysis` | Agent 3B (Gap Analyzer) | Run diagnostic on full session |
| `is_off_topic` or `is_greeting` | Agent 4 (Teacher) | Short polite response, end |
| `requires_deep_research` | Agent 2 (Wavelength) | Build search queries |
| None of the above (default) | Agent 4 (Teacher) | Full explanation |

---

#### Step 4: Agent 2 (Wavelength Setter) — The Question It Answers

**"How deep should we search, and what search queries should we use?"**

**When it runs:** Only when the Guardrail set `requires_deep_research = True`.

**Why it exists:** Not all questions need the same search depth. "Explain operating systems" needs broad overview search. "What does copy_to_user do in the Linux kernel" needs a specific, narrow search. This agent decides the granularity and builds the queries.

**What it actually does:**

1. Takes: user's question + current topic + prior context + cognitive profile
2. Decides the **wavelength** (search scope):
   - **MACRO** — broad foundational search
   - **MESO** — intermediate connection search
   - **MICRO** — laser-focused specific search
3. Builds 1–3 structured search queries with domain filters:
   - Include: specific domains you want results from (e.g., "kernel.org", "ebpf.io")
   - Exclude: domains to skip (e.g., "reddit.com", "quora.com")

**Concrete example:**

- *User asks:* "How does eBPF verify programs before loading?"
- *Wavelength setter decides:* This is MICRO — very specific, needs authoritative sources
- *Produces queries:*
  - `{ query: "eBPF verification kernel", include: ["ebpf.io", "kernel.org"] }`
  - `{ query: "eBPF safety guarantees", exclude: ["reddit.com"] }`

**What it produces:**

```json
{
  "detected_wavelength": "MICRO",
  "adapted_learning_scope": "Specific API-level verification, assuming foundational eBPF knowledge exists",
  "agent_6_queries": [
    { "query": "...", "search_depth": "thorough", "include_domains": [...], "exclude_domains": [...] }
  ],
  "search_plan": { ... }  // passed to Agent 6
}
```

**Where it goes next:** The search plan is passed to Agent 6 (Researcher).

---

#### Step 5: Agent 6 (Deep Researcher) — The Question It Answers

**"What did the web search find, and is it trustworthy?"**

**When it runs:** Immediately after Agent 2, as part of the research branch.

**Why it exists:** The system needs fresh, verified information from the web. But search results are noisy — you need to filter out unreliable sources and synthesize the findings into something the Teacher can use.

**What it actually does:**

1. **Deduplication guard:** Check if any of the search subtopics were already covered in the existing research catalog. If too much overlap, skip to avoid redundant work.
2. **Execute searches:** Run each query from the search plan against the Tavily web search API.
3. **Source filtering:** Automatically filter out unverified sources (Reddit, Quora, StackOverflow without citations).
4. **Synthesis:** Feed raw search results to an LLM to extract:
   - Verified facts with source excerpts
   - Code or math snippets if relevant
   - Canonical subtopics covered

**What it produces:**

```json
{
  "research_id": "res_abc123",
  "source_supported_facts": [
    { "fact": "eBPF uses a verification pass that walks the entire instruction graph", "source_excerpt": "The verifier ensures...", "confidence": "high" }
  ],
  "code_or_math_snippet": "if (ctx->regs > BPF_MAXINSNS) return -E2BIG;",
  "canonical_subtopics": ["verification_pass", "instruction_graph", "safety_checks"],
  "research_catalog": [ ... ]  // appended to existing catalog
}
```

**Where it goes next:** The research catalog (a growing list) is passed to Agent 4 (Teacher). After the Teacher responds, the flow may loop back here if more research is needed (max 2 attempts).

---

#### Step 6: Agent 4 (Teacher) — The Question It Answers

**"What's the best way to explain this to THIS particular user, based on their cognitive profile?"**

**When it runs:** The main output node — runs for most messages (unless it's greeting, off-topic, or gap analysis).

**Why it exists:** This is the core of the tutoring system. It takes everything — the question, the research results, the user's cognitive profile — and generates a personalized explanation with a follow-up Socratic probe.

**What it actually does:**

1. **Special case handling:** If Guardrail said it's a greeting or off-topic, generate a short polite response and skip to end.
2. **Cognitive DNA injection:** If the user has a cognitive profile, extract key fields and inject them as a 500-character override in the system prompt:
   - Preferred pacing (slow or fast)
   - Preferred complexity (shallow or deep)
   - Enforced constraints ("always give code first, then theory")
   - Predicted friction points (where the user will likely struggle)
   - Preferred analogy domain (mechanics, biology, economics)
3. **Explanation generation:** Call the LLM with all this context. The LLM is instructed to:
   - Answer the question directly
   - Explain at the user's preferred depth
   - Use analogies from their preferred domain
   - Teach concrete tools before abstract ideas
4. **Socratic probe creation:** Generate a targeted follow-up question to keep the Socratic dialog going. Three types:
   - **pedagogical_validation** — "Did you understand this?"
   - **clarification** — "Can you explain that differently?"
   - **diagnostic** — "What happens if X?"

**Concrete example:**

- *User asks:* "How does virtual memory work?"
- *Profile says:* User thinks causally, needs concrete first, uses mechanical analogies
- *Teacher responds with:*
  - Explanation using mechanical analogy (paging as a desk with a notepad)
  - Then immediately asks: *"When you turn a page in your notepad, what happens to the previous page?"* (causal reasoning probe)

**What it produces:**

```json
{
  "answer": "## Virtual Memory\n\nThink of RAM as a desk and disk as a bookshelf...",
  "explanation_depth": "moderate",
  "concepts_covered": ["virtual_address", "page_table", "TLB"],
  "evidence_boundary": "Confident about desk-analogy, less confident about NUMA effects",
  "socratic_question": {
    "probe_id": "probe_xyz",
    "probe_type": "pedagogical_validation",
    "probe_mode": "mechanism_analysis",
    "question_text": "When a page fault occurs, what specific sequence of events happens in the CPU?",
    "target_concept": "page_fault_handler"
  },
  "requires_research_fallback": false
}
```

**Where it goes next:** Agent 3C (Quality Critic). If `requires_research_fallback == True`, the graph loops back to Agent 2 instead.

---

#### Step 6.5: Agent 3C (Quality Critic) — The Question It Answers

**"Did the Teacher follow the rules, or is this generic fluff?"**

**When it runs:** Immediately after the Teacher drafts a response.

**Why it exists:** Even smart LLMs sometimes slip into generic "textbook" tones or forget to use the user's preferred analogies. The Critic is a harsh editor that forces the Teacher to stay in character.

**What it actually does:**
1. Compares the Teacher's draft against the user's `cognitive_profile` rules.
2. Checks for fluff, corporate boilerplates, and missing concrete anchors.
3. If the draft fails, it sends a harsh critique back to the Teacher and forces a rewrite (maximum 1 retry).
4. If it passes, it approves the message.

**Where it goes next:** If FAIL, loops back to Agent 4 (Teacher). If PASS, proceeds to the Memory Compressor.

---

#### Step 7: Memory Compressor (Ghost Recorder) — The Question It Answers

**"How do we keep the conversation history from becoming too big for the LLM to handle?"**

**When it runs:** After every Agent 4 response, right before the graph terminates.

**Why it exists:** After 50 messages, the conversation history would be thousands of tokens. The LLM would slow down and eventually hit context limits. The compressor keeps it lean.

**What it actually does:**

- Takes the full Teacher response (often 1,000+ tokens)
- Extracts a lightweight "ghost record" with only the essentials:
  - Topic taught
  - Depth level
  - Concepts covered
  - 500-character excerpt of core explanation
  - What Socratic probe was asked
  - Evidence boundary (what the answer is confident about vs. uncertain)

**Why it's called "ghost":** The compressed record is a "ghost" of the full response — enough context to know what was discussed, but light enough to fit in the context window.

**What it produces:**

```json
{
  "type": "ghost_record",
  "topic": "virtual_memory",
  "depth": "moderate",
  "concepts_taught": ["page_table", "TLB", "page_fault"],
  "core_explanation": "Think of RAM as a desk and disk as a bookshelf. When you need a page not on the desk...",
  "socratic_probe": "What happens when you turn a page?",
  "probe_id": "probe_xyz",
  "evidence_boundary": "Confident about desk-analogy, less confident about NUMA effects",
  "teacher_memory": [ ... ]  // appended to teacher memory
}
```

**Where it goes next:** The state is checkpointed to SQLite and the response is returned to the user. END.

---

### Phase D: On-Demand Diagnostic Branch (Agent 3B)

This doesn't happen as part of the normal flow — it's triggered separately.

**Step 8: You click the Gap Analysis button**

In the chat UI, there's a floating button to run "Gap Analysis". When you click it, the frontend sends a request to `/gap_analysis`.

---

**Agent 3B: Knowledge Gap Analyzer — The Question It Answers**

**"What concepts is the user missing, and what should we do about it?"**

**When it runs:** Only when the user clicks the "Gap Analysis" button in the UI. It's not part of the normal message flow — it's an interrupt.

**Why it exists:** Sometimes the user themselves doesn't know what they don't know. This agent looks at the entire session history, finds the gaps, and suggests specific actions to fill them.

**What it actually does:**

1. Bundles together:
   - Full conversation history
   - Teacher memory (compressed past responses)
   - Research catalog
   - Cognitive profile
   - Cognitive events (if any)
2. Analyzes the entire session to find:
   - **Comprehension gaps** — concepts the user struggled to explain
   - **Coverage gaps** — foundational topics never introduced
   - **Misconceptions** — patterns of incorrect reasoning

**What it produces:**

```json
{
  "diagnostic_summary": "User struggles with abstraction. Never fully grasped page table hierarchies despite 3 discussions.",
  "suggestions": [
    { "type": "COMPREHENSION", "missing_subtopic": "page_table_hierarchy", "reason": "User always gives high-level descriptions without drilling into structure", "button_label": "Fill This Gap" },
    { "type": "COVERAGE", "missing_subtopic": "TLB", "reason": "Never discussed despite being foundational to virtual memory", "button_label": "Introduce TLB" }
  ],
  "last_gap_analysis": { ... }
}
```

**Where it goes next:** Memory Compressor → END. The frontend displays these as clickable cards.

---

## 3. Complete Agent Roster — All 8 Nodes Explained

Here's every agent in the system, with consistent explanation format:

---

### Agent 1: Mapper (Cognitive Footprint Extractor)

| Field | Description |
|-------|-------------|
| **The question it answers** | "What is this user's cognitive DNA — how do they think, reason, and learn?" |
| **When it runs** | Only once — during initial calibration when user submits a writing sample |
| **Why it exists** | To build the personalized teaching model that all other agents use |
| **Incoming inputs** | Raw writing sample text from the user |
| **Key processing task** | Deep epistemic extraction: maps causal reasoning style, abstraction movement, certainty markers, knowledge organization patterns, and predicted friction points |
| **Output data & format** | `cognitive_profile.json` with three sections: `cognitive_dna`, `reverse_engineered_model`, `tutor_directive` |
| **Destination** | Saved to disk (`cognitive_profile.json`) and loaded into every new session's state |

---

### Agent 3A: Cognitive Validator (Probe Response Inspector)

| Field | Description |
|-------|-------------|
| **The question it answers** | "Did the user just answer a Socratic probe? Did they show understanding or confusion?" |
| **When it runs** | Before the Guardrail, on every user message — but only does real work if there was a probe in the previous turn |
| **Why it exists** | To grade user responses to pedagogical probes and continuously refine the cognitive model |
| **Incoming inputs** | User's current message + the previous Socratic probe object from state |
| **Key processing task** | Compares user answer against expected cognitive evidence, generates validation signal, updates hypothesis weights |
| **Output data & format** | `response_quality`, `hypothesis_effect`, `cognitive_event`, `last_validation` |
| **Destination** | Agent 5 (Guardrail) |

---

### Agent 5: Scope Guardrail (Intent & Traffic Controller)

| Field | Description |
|-------|-------------|
| **The question it answers** | "What kind of message is this, and where should it go next?" |
| **When it runs** | Immediately after Cognitive Validator, on every user message |
| **Why it exists** | To classify message intent and route it to the appropriate handler |
| **Incoming inputs** | User's message + active topic context + validation state |
| **Key processing task** | Three-layer classification: deterministic bypass for greetings/meta, LLM classification for technical queries; sets flags for routing |
| **Output data & format** | `is_greeting`, `is_meta`, `is_off_topic`, `requires_deep_research`, `trigger_gap_analysis`, `classification` |
| **Destination** | Conditional edge routes to Agent 2, Agent 4, or Agent 3B |

---

### Agent 2: Wavelength Setter (Search Strategist)

| Field | Description |
|-------|-------------|
| **The question it answers** | "How deep should we search, and what search queries should we use?" |
| **When it runs** | Only when Guardrail sets `requires_deep_research = True` |
| **Why it exists** | To determine the right search granularity and build targeted queries |
| **Incoming inputs** | User's question + current topic + prior context + cognitive profile |
| **Key processing task** | Classifies query scale (MACRO/MESO/MICRO), builds domain-filtered search queries |
| **Output data & format** | `detected_wavelength`, `adapted_learning_scope`, `agent_6_queries` (structured search plan) |
| **Destination** | Agent 6 (Deep Researcher) |

---

### Agent 6: Deep Researcher (Fact Verification Engine)

| Field | Description |
|-------|-------------|
| **The question it answers** | "What did the web search find, and is it trustworthy?" |
| **When it runs** | Immediately after Agent 2, as part of the research branch |
| **Why it exists** | To gather fresh, verified technical information from authoritative web sources |
| **Incoming inputs** | Structured `search_plan` from Agent 2 |
| **Key processing task** | Executes Tavily searches, deduplicates against existing catalog, filters unverified sources, synthesizes facts via LLM |
| **Output data & format** | `research_id`, `source_supported_facts[]`, `code_or_math_snippet`, `canonical_subtopics[]`, appended to `research_catalog` |
| **Destination** | Agent 4 (Teacher) — may loop back up to 2 times if more research needed |

---

### Agent 4: Mentality Teacher (Socratic Pedagogical Engine)

| Field | Description |
|-------|-------------|
| **The question it answers** | "What's the best way to explain this to THIS particular user?" |
| **When it runs** | The main output node — runs for most messages (unless greeting/off-topic/gap analysis) |
| **Why it exists** | The core tutoring engine — generates personalized explanations and Socratic probes |
| **Incoming inputs** | User input + research catalog + cognitive profile + teacher memory |
| **Key processing task** | Injects cognitive DNA into prompt, generates personalized explanation using concrete-to-abstract laddering, creates typed Socratic probe |
| **Output data & format** | `answer` (markdown), `explanation_depth`, `concepts_covered[]`, `evidence_boundary`, `socratic_question` object, `requires_research_fallback` |
| **Destination** | Agent 3C (Quality Critic) — may loop back to Agent 2 if fallback needed |

---

### Agent 3C: Quality Critic (Draft Auditor)

| Field | Description |
|-------|-------------|
| **The question it answers** | "Did the Teacher follow the cognitive profile rules?" |
| **When it runs** | Immediately after Agent 4 drafts an answer |
| **Why it exists** | To prevent generic AI fluff and enforce strict pedagogical alignment |
| **Incoming inputs** | Teacher draft + Cognitive Profile |
| **Key processing task** | Audits for concrete anchors, fluff removal, and rule adherence |
| **Output data & format** | `PASS/FAIL` flag and `quality_critique` string |
| **Destination** | If FAIL, loops back to Teacher. If PASS, goes to Memory Compressor |

---

### Utility Node: Ghost Memory Compressor (Context Window Optimizer)

| Field | Description |
|-------|-------------|
| **The question it answers** | "How do we keep the conversation history from becoming too big?" |
| **When it runs** | After every Agent 4 response, right before graph terminates |
| **Why it exists** | To preserve context window capacity during long conversations |
| **Incoming inputs** | Full teacher response + conversation history |
| **Key processing task** | Extracts lightweight semantic "ghost record" (~1KB) with topic, depth, concepts, core explanation excerpt, probe info |
| **Output data & format** | `ghost_record` object, appended to `teacher_memory` |
| **Destination** | END — state checkpointed to SQLite, response returned to user |

---

### Agent 3B: Knowledge Gap Analyzer (FAB Diagnostic Node)

| Field | Description |
|-------|-------------|
| **The question it answers** | "What concepts is the user missing?" |
| **When it runs** | When user clicks Gap Analysis FAB button — not part of normal flow |
| **Why it exists** | To diagnose learning friction points and suggest actionable remedies |
| **Incoming inputs** | Full transcript + probe success/failure history + research catalog + cognitive profile |
| **Key processing task** | Analyzes session for comprehension gaps, coverage gaps, and misconceptions |
| **Output data & format** | `diagnostic_summary`, `suggestions[]` (with `type`, `missing_subtopic`, `reason`, `button_label`) |
| **Destination** | END — returned to frontend for UI rendering |

---

## 4. LangGraph Mechanics — The Plumbing

Now that you know each agent, let's explain how LangGraph orchestrates them.

### The Shared Blackboard: SyntapseChamberState

Every agent reads from and writes to a shared dictionary called `SyntapseChamberState`. Think of it as a blackboard that everyone can see and draw on.

**What's in the state:**

| Field | What it holds |
|-------|---------------|
| `session_id`, `turn_id` | Identity |
| `cognitive_profile` | The user's cognitive DNA |
| `topic_name` | What they're learning |
| `user_topic_context` | Sticky context that never scrolls off |
| `messages` | The full conversation history |
| `research_catalog` | All web search results accumulated |
| `teacher_memory` | Compressed past responses (ghost records) |
| `cognitive_events` | All probe validation events |
| `discussed_concepts` | Concepts covered so far |
| `is_off_topic`, `is_greeting`, `is_meta`, `requires_deep_research`, `trigger_gap_analysis` | Routing flags |
| `last_teacher_probe` | The probe from the previous turn |
| `last_teacher_response` | The previous explanation |
| `research_attempts` | How many times research loop has run |
| `active_cognitive_hypotheses` | Testable guesses about user's learning style |

### Reducers: How Data Accumulates

Not all fields are updated the same way. Reducers define the update rule:

| Reducer | Fields affected | What it does |
|---------|-----------------|--------------|
| `add_messages` | `messages` | Appends new message to the list |
| `append_research` | `research_catalog`, `teacher_memory`, `cognitive_events` | Appends new entries, never overwrites |
| (default overwrite) | Everything else | Last write wins |

**Why this matters:** The conversation history *grows*. Research results *accumulate*. This way, every agent sees everything that's happened so far.

### Conditional Edges: The Routing Logic

LangGraph uses **conditional edges** — functions that inspect the state and decide where to go next.

#### Conditional Edge 1: route_from_guardrail()

After Agent 5 (Guardrail), this function checks the flags in this exact order:

1. **Is `trigger_gap_analysis == True`?**
   - Yes → Go to Agent 3B (Gap Analyzer) → Memory Compressor → END

2. **Is `is_off_topic == True` or `is_greeting == True`?**
   - Yes → Go to Agent 4 (short response) → Memory Compressor → END

3. **Is `requires_deep_research == True`?**
   - Yes → Go to Agent 2 (Wavelength) → Agent 6 (Researcher) → Agent 4 → Memory Compressor → END

4. **Otherwise (default):**
   - Go directly to Agent 4 → Memory Compressor → END

#### Conditional Edge 2: route_from_teacher()

After Agent 4 (Teacher), this function checks:

- **Did Teacher set `requires_research_fallback == True` AND have we tried research less than 2 times?**
  - Yes → Loop back to Agent 2 (Wavelength) — do another research cycle
  - No → Go to Memory Compressor → END

### The Research Loop

Here's a subtle thing: **the research branch can loop**. If Agent 4's explanation needed more facts, it sets `requires_research_fallback = True`, and the graph loops back to Agent 2. This happens at most 2 times to prevent infinite loops.

```
Agent 2 → Agent 6 → Agent 4 → [needs more facts?] → Agent 2 → Agent 6 → Agent 4 → [needs more facts?] → Agent 2 → Agent 6 → Agent 4 → [still needs facts? stop]
```

---

## 5. Human-in-the-Loop & Feedback Cycles

### The Socratic Feedback Loop

The system is designed to run a continuous learning cycle:

1. **Teacher asks a probe** — Agent 4 generates a `pedagogical_validation` probe targeting a specific cognitive hypothesis about how the user learns.
2. **User answers** — The answer becomes the next user message.
3. **Cognitive Validator evaluates** — Agent 3A checks whether the answer confirms, contradicts, or is inconclusive for the tested hypothesis.
4. **Hypothesis weights update** — Using a formula:
   - `support_weight += evidence_weight × confidence_modifier` (or)
   - `contradiction_weight += evidence_weight × confidence_modifier`
5. **Next probe is informed** — The next time Agent 4 generates a probe, it has updated knowledge about which cognitive model fits the user.

**Why this matters:** Over a 20-turn conversation, the system builds an increasingly accurate model of the user's mental model and adapts its teaching strategy accordingly.

> ⚠️ **Current Limitation:** The Cognitive Validator is fully implemented, but it has no hypotheses to validate against because the step that seeds them at session start was never wired. This is a one-line fix in the `/session/start` endpoint.

### The Gap Analysis Loop

This is a **user-initiated** interrupt:

1. User clicks the Gap Analysis FAB button in the UI
2. Frontend sends a separate request to `/gap_analysis`
3. Backend sets `trigger_gap_analysis = True` in the state
4. The next regular chat message will route through Agent 3B, which bundles the entire session and produces a diagnostic
5. The diagnostic is returned to the frontend and rendered as clickable "Fill This Gap" cards
6. The main conversation is **not interrupted** — the gap analysis runs alongside it

---

## 6. Session Management & Dual-Layer Persistence

Two separate systems keep your data safe:

### Layer 1: SQLite Checkpointer (LangGraph)

LangGraph writes the entire state to `syntapse_sessions.db` after every node execution. This means:

- Sessions survive server restarts
- Each user has isolated sessions (via `thread_id`)
- Everything is checkpointed — messages, research, cognitive events

### Layer 2: Cognitive Profile File

Your cognitive profile is saved separately to `cognitive_profile.json` on disk. This is a fallback — if the database is wiped, your profile survives.

### Frontend localStorage

The frontend stores session metadata (topic name, turn count) in browser localStorage. This is separate from the backend because the backend only stores chat state, not the UI metadata needed to show the session list.

---

## 7. Quick Reference — The Flow in One Table

| Step | Agent | The Question It Answers | Goes To |
|------|-------|------------------------|---------|
| — | **Agent 1: Mapper** | "What's your cognitive DNA?" | Disk → Session payload |
| 1 | **Cognitive Validator (3A)** | "Did you just answer a probe?" | Guardrail |
| 2 | **Guardrail (5)** | "What kind of message is this?" | [Conditional edge] |
| 3a | **Gap Analyzer (3B)** | "What are you missing?" | Compressor → END |
| 3b | **Teacher (short)** | "Polite redirect" | Compressor → END |
| 3c | **Wavelength (2) → Researcher (6) → Teacher** | "Search, then explain" | Compressor → END |
| 3d | **Teacher (full)** | "Personalized explanation + probe" | Quality Critic |
| 3e | **Quality Critic (3C)** | "Did you follow the rules?" | Compressor (or Loop to Teacher) |
| 4 | **Compressor** | "Keep context lean" | END |
| Loop | — | "Need more research?" | Back to Wavelength (max 2×) |

---

## 8. What Works vs. What's Dormant

| Component | Status | Notes |
|-----------|--------|-------|
| Agent 1 (Mapper) | ✅ Working | Full cognitive extraction |
| Agent 3A (Validator) | ⚠️ Runs but empty | Needs hypothesis seeding to work |
| Agent 5 (Guardrail) | ✅ Working | Full classification |
| Agent 3B (Gap Analyzer) | ✅ Working | FAB-triggered |
| Agent 2 (Wavelength) | ✅ Working | Query building |
| Agent 6 (Researcher) | ✅ Working | Web search + synthesis |
| Agent 4 (Teacher) | ✅ Working | Full Socratic generation |
| Agent 3C (Critic) | ✅ Working | Audits and enforces rewrites |
| Memory Compressor | ✅ Working | Token optimization |
| SQLite persistence | ✅ Working | Survives restarts |
| Cognitive feedback loop | ❌ Dormant | Needs one wire to activate |

---

*This guide reflects the implemented system as of August 2026. For the source code, explore `v:\PROJECTS\project_agents\backend\`.*