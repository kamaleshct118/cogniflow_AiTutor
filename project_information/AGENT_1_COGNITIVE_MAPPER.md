# Agent 1: Cognitive Mapper — Technical Reference

> **Agent Identifier:** `syntapse.agents.cognitive_mapper.v9_evidence_ledger`  
> **Role:** Forensic Cognitive Decompiler & Predictive Teaching Payload Compiler  
> **Runtime Model:** Groq `llama-3.3-70b-versatile` — Single API call, native JSON mode  
> **Files:** `backend/orchestrator.py` → `live_agent_1_mapper()`, prompt: `prompt_skills/cognitive_mapper_vr_holy_grail.md`

---

## What It Does

Agent 1 ingests an unprompted free-form text where the user explains a concept they already understand. It reverse-engineers their **cognitive fingerprint** — not personality types, but the structural mechanics of how they think and communicate.

It answers one question: *"Given how this person thinks, what teaching strategy is currently supported by the available evidence, and what diagnostic observation would confirm or falsify it on a new topic?"*

---

## Evidence Ledger Protocol (Anti-Hallucination)

Every inference must be grounded in a direct quote from the user's text. **Minimum 5 evidence items required.**

```json
{
  "evidence_id": "E01",
  "quote": "exact sentence from user",
  "observation": "what the user is literally doing",
  "hypothesis": "inferred reasoning operation",
  "alternative_explanations": ["other possible explanations"],
  "topic_confound_risk": "low | medium | high",
  "stability": "single_occurrence | repeated_pattern",
  "confidence": "low | medium | high"
}
```

**Stability rules:**
- `repeated_pattern` — only if the same cognitive behavior appears in 2+ separate quotes
- `high confidence` — only if `repeated_pattern`

---

## Forensic Extraction Dimensions

| Dimension | What It Detects |
|---|---|
| **Clause Structure** | Simple / compound / nested explanations. A→B? A because B? |
| **Causal Bridges** | Mechanistic causality vs temporal sequence vs unsupported assertion |
| **Abstraction Ladder** | Can they move abstract↔concrete? Do they plateau at concrete? |
| **Concrete Anchors** | Example-*supported* vs example-*dependent* understanding |
| **Epistemic Signature** | Hedging ("I think"), compression markers ("basically"), authoritative assertion |
| **Terminology Handling** | Do they *own* domain terms (define them) or just *use* them (surface familiarity)? |
| **Gap Detection** | What did the expert NOT mention that reveals blind spots? |

---

## Output Schema

```json
{
  "cognitive_dna": {
    "evidence_ledger": [ ...minimum 5 items... ],
    "atomic_evidence_map": {
      "clause_structure": { "dominant_pattern": "...", "supporting_evidence_ids": [] },
      "causal_reasoning": { "dominant_pattern": "...", "supporting_evidence_ids": [], "counter_evidence_ids": [] },
      "abstraction_ladder_movement": { "dominant_pattern": "...", "supporting_evidence_ids": [] }
    },
    "epistemic_signature": {
      "certainty_markers": { "dominant_pattern": "...", "supporting_evidence_ids": [] },
      "concrete_anchor_dependence": { "dominant_pattern": "...", "supporting_evidence_ids": [] }
    },
    "knowledge_organization": { "dominant_pattern": "...", "supporting_evidence_ids": [] }
  },
  "reverse_engineered_model": {
    "transfer_prediction": "How this user will approach unfamiliar complex topics",
    "predicted_friction_points": ["Specific friction 1", "Specific friction 2"],
    "compression_expansion_profile": "Where compression is successful vs dangerous"
  },
  "tutor_directive": {
    "pedagogical_telemetry": {
      "concept_introduction_order": "SPECIFIC — not generic",
      "conceptual_step_size": "SPECIFIC — not generic",
      "analogy_domain": "SPECIFIC — not generic"
    },
    "enforced_constraints": ["Brutally specific constraint 1"],
    "detected_knowledge_gaps": ["What the user did NOT mention that they should know"]
  }
}
```

---

## Core Safeguards

1. **Zero predefined buckets** — All labels are emergent from evidence, never hardcoded categories
2. **No fact-checking** — A confidently wrong explanation and a correct one reveal identical reasoning mechanics. Truth is irrelevant to profiling
3. **ANTI-GENERICITY RULE** — `tutor_directive` fields must be brutally specific with concrete examples. "Use analogies" is a failure
4. **Profile persistence** — Profile is stored in frontend Zustand localStorage and re-injected into backend on every session start/re-registration
