# Syntapse Core System Architecture & Interaction Flow

> **System Identification:** `syntapse.architecture.core_flow_v6`  
> **Core Focus:** Persistent Cognitive Profiling, Autonomous Deep Research, Guardrail Isolation, and Dynamic Knowledge Gap Analysis via LangGraph Orchestration.

---

## 🏛️ 1. Global vs. Local State Management Architecture

To ensure strict content isolation while maintaining personalized learning, Syntapse utilizes a dual-state memory architecture orchestrated by **LangGraph**:

1. **Global Cognitive Profile (The User's DNA):**
   * Extracted by **Agent 1 (Cognitive Mapper)**.
   * Stored globally at the user-account level.
   * Defines *how* the user thinks (causal bridging, preferred analogies, complexity strategy).
   * Applied universally across **all** local chat sessions.

2. **Local Chamber Session Context (The Topic Room):**
   * Unique to each specific chat card / session.
   * Contains: Target Topic, Session Chat History, Pre-fetched Research Data, and Session-Specific `TutorDirective`.
   * **Content Isolation:** Strictly partitioned. Data from "Chat A (Transformers)" can never bleed into "Chat B (Docker)".

---

## 🤖 2. Multi-Agent Roster & Responsibilities

* **Agent 1 (Cognitive Mapper - The Master Settings Engine):** Extracts the Global Cognitive Profile from the user's baseline input. This profile acts as the universal "setting" applied to all interactions.
* **Agent 2 (Wavelength & Query Orchestrator):** Translates the user's target topic into 3-5 highly optimized search queries (crucially including broader, 'one-level-higher' queries to retrieve foundational context for the Analogy Bridge), AND uses Agent 1's Linguistic Mechanics to configure the Tavily API parameters (search depth, trusted domains) to match the user's expertise level.
* **Agent 3 (Gap Analyzer & Cognitive Validator):** Runs in the background to detect knowledge gaps from user interaction. It provides pedagogical signals and updates the Learner Model if the Teacher's strategy is failing.
* **Agent 4 (Mentality Teacher):** Synthesizes Dual-Layered responses (Analogy Bridge + Technical Anchor), autonomously delegating to Agent 6 when deep technical depth is required.
* **Agent 5 (Guardrail Agent):** Inspects every user prompt to enforce topic boundary isolation and maintain topical diversity between chat rooms.
* **Agent 6 (Research Agent):** Executes Google Searches, scrapes canonical data, deduplicates facts, and injects verified external source-grounded evidence into the Chamber Session Memory (this is treated as evidence, not absolute ground truth).
* **Agent 3C (Quality Critic):** The final auditor. Intercepts the Teacher's draft to ensure it strictly follows the user's Cognitive Profile rules. If the Teacher fails to align, Agent 3C forces a rewrite loop.

---

## 🔄 3. The User Journey & Sequential Interaction Flow

### Phase 1: Initial Onboarding & The Cognitive "Setting" (Model Card)
When a user clicks **"+ New Chat"**, a Model Card appears with the following configuration:
1. **Title / Target Topic:** (e.g., *Transformer Architecture*).
2. **Knowledge Status Field (The Cognitive Profile Setting):** The user inputs text based on one of two choices:
   * **"Known Content":** Something they already know well. **Crucially, Agent 1 processes this text to generate the user's Global Cognitive Profile.** This profile is the master setting governing all future interactions.
   * **"Content to Learn":** What they currently know or expect to learn about the Target Topic.
3. **The `[ SKIP / UNKNOWN ]` Option:** If the user has zero prior knowledge about the topic and doesn't want to write a baseline, they can click skip. The system falls back to a standard diagnostic curriculum.
4. **Action:** User clicks **[ Save & Initialize Chamber ]**.

### Phase 2: Agent 1 Profiling & Automated Research Integration
*Immediately upon clicking Save, before the user sees the first message:*
1. **Agent 1 (Cognitive Mapper)** executes on the user's text to lock in their Global Cognitive Settings (if not already established).
2. **Agent 2 (Wavelength & Query Orchestrator)** analyzes the Target Topic and Cognitive Profile, generating 3-5 high-value search queries (including foundational, one-level-higher context) bundled with domain constraints (e.g., `include_domains: ["arxiv.org"]` for experts).
3. **Agent 6 (Research Agent)** executes this pre-configured payload, scrapes documentation, and compiles a canonical topic structure.
4. This external data is stored directly within the **Local Chamber Session Memory**.
5. The system is now primed. All agents in this chamber now share access to this verified baseline knowledge.

### Phase 3: The Mentality Chat Loop & Dynamic Depth
1. **User asks a question** in the active chat.
2. **Agent 5 (Guardrail Agent)** intercepts the query. It verifies topic safety and performs a **Proactive Depth Check**. If the query requires complex technical APIs or obscure facts, the Guardrail instantly routes directly to Agent 2 and Agent 6 for research *before* the Teacher wakes up.
3. **Reactive Depth Check (Fallback):** If Guardrail didn't catch it, **Agent 4 (Teacher)** starts drafting. If it realizes it lacks facts mid-draft, it autonomously triggers a fallback loop to **Agent 6 (Researcher)**.
4. **Response Generation & Quality Audit:** Agent 4 synthesizes the draft using the Global Cognitive Profile. Before the user sees it, **Agent 3C (Quality Critic)** ruthlessly audits the draft against the user's DNA. If approved, it is displayed. If rejected, it forces the Teacher to rewrite it.

### Phase 4: Dynamic Knowledge Gap Analysis (The FAB)
At *any* point in the conversation, the user can click the persistent **Floating Action Button (FAB) `[ ⚡ Analyze Knowledge Gap ]`**.
1. **Trigger:** The system suspends standard chat generation. *(LangGraph Conditional Guard: If `len(chat_history) < 2`, it yields a message asking the user to explore the topic first, avoiding the "Premature Gap" paradox).*
2. **Analysis:** An analysis agent reviews the *entire dialogue history* of the current session against the canonical topic data gathered by Agent 6.
3. **Output Summary:** The system generates a diagnostic message highlighting what subtopics the user has missed or misunderstood.
4. **Interactive Suggestion Buttons:** The message appends clickable buttons for each gap (e.g., `[ Explore Positional Encoding ]`).
5. **Seamless Continuation:** Clicking a suggestion button automatically acts as a user prompt, triggering Agent 4 to generate a tailored explanation.

---

## 🔒 4. LangGraph State & Dual-Stream Memory Protocols

Syntapse relies on a highly structured **LangGraph State Object** to ensure that data is isolated, manageable, and performant.

### The Two Separate Memory Streams
Instead of dumping raw internet data into the chat history and confusing the LLM context, Syntapse isolates memory into two dedicated streams within the `State` dictionary:

```python
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class SyntapseChamberState(TypedDict):
    # 1. THE GLOBAL SETTING
    cognitive_profile: dict
    
    # 2. THE CLEAN CONVERSATION STREAM (Human-facing Chat)
    messages: Annotated[list, add_messages]
    
    # 3. THE ISOLATED RESEARCH CATALOG (Background Agent Store)
    research_catalog: List[dict]  # Agent 6 dumps facts, snippets, and scraped JSON here
    
    # 4. ORCHESTRATION FLAGS
    requires_deep_research: bool
```

### Protocol Execution:
1. **The Handoff:** When Agent 4 (Teacher) is prompted to generate a response, LangGraph passes *both* memory streams. 
2. **Browsing the Catalog:** Agent 4 "browses" the `research_catalog` to fetch necessary raw facts, but formats its response strictly into the `messages` stream using the user's Cognitive Profile.
3. **Context Window Compression:** Before generation, a LangGraph `MemoryCompressorNode` compresses older chat turns and deduplicates the `research_catalog` to prevent token bloat and latency spikes over long sessions.
4. **Asynchronous Hand-offs:** If Agent 4 triggers Agent 6 for deep research, LangGraph yields a partial UI state (`status="deep_research"`) so the frontend displays a loading indicator (e.g., `"Agent 6 is retrieving technical specifications..."`) preventing UI freezes.
