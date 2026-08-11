"""
===============================================================================
 SYNAPSE COGNITIVE ENGINE — Profile Compiler (profile_compiler.py)
===============================================================================
 Purpose:
   • Compiles raw Cognitive Profile output from Agent 1 (Mapper) into active
     Bayesian hypotheses with initial teaching policies.

 Core Logic & Hierarchy:
   ├── generate_h_id()       : Generates deterministic SHA-256 hypothesis IDs (H_CAUSAL_xxx)
   ├── compile_raw_profile() : Translates epistemic signature into active_hypotheses
   └── Initial Confidence    : Seeds initial baseline confidence (0.50) for Agent 3A evaluation
===============================================================================
"""

import hashlib
from typing import Dict, Any

def generate_h_id(prefix: str, pattern: str) -> str:
    """Generates a stable, deterministic hypothesis ID based on the pattern."""
    raw = f"{prefix}:{pattern}".encode("utf-8")
    return f"H_{prefix}_{hashlib.sha256(raw).hexdigest()[:8]}"

def compile_raw_profile(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compiles the raw cognitive forensic output from Agent 1 into the canonical Global Cognitive Profile,
    specifically translating the Evidence Ledger, Transfer Prediction, and atomic patterns into active_hypotheses.
    This bridges Agent 1 (Interpretation) and Agent 4 (Teaching Policy).
    """
    if not raw_profile:
        return {}
        
    dna = raw_profile.get("cognitive_dna", {})
    atomic_map = dna.get("atomic_evidence_map", {})
    tutor_directive = raw_profile.get("tutor_directive", {})
    pedagogy = tutor_directive.get("pedagogical_telemetry", {})
    constraints = tutor_directive.get("enforced_constraints", [])
    rev_model = raw_profile.get("reverse_engineered_model", {})
    
    active_hypotheses = {}
    
    # 1. Causal Reasoning Hypothesis
    causal = atomic_map.get("causal_reasoning")
    if causal and causal.get("dominant_pattern"):
        pattern = causal["dominant_pattern"]
        h_id = generate_h_id("CAUSAL", pattern)
        active_hypotheses[h_id] = {
            "hypothesis_id": h_id,
            "pattern": pattern,
            "source_evidence_ids": causal.get("supporting_evidence_ids", []),
            "teaching_policy": {
                "concept_introduction_order": pedagogy.get("concept_introduction_order", "mechanism -> causal sequence -> terminology"),
                "conceptual_step_size": pedagogy.get("conceptual_step_size", "small"),
                "representation_priority": "causal_flow",
                "analogy_policy": pedagogy.get("analogy_domain", "faithful_only"),
                "enforced_constraints": constraints + rev_model.get("predicted_friction_points", [])
            },
            "support_weight": 0.0,
            "contradiction_weight": 0.0,
            "independent_topics": [],
            "status": "active_hypothesis",
            "confidence": 0.50 # Python owns initialization
        }
        
    # 2. Abstraction Ladder Movement Hypothesis
    abstraction = atomic_map.get("abstraction_ladder_movement")
    if abstraction and abstraction.get("dominant_pattern"):
        pattern = abstraction["dominant_pattern"]
        h_id = generate_h_id("ABSTR", pattern)
        active_hypotheses[h_id] = {
            "hypothesis_id": h_id,
            "pattern": pattern,
            "source_evidence_ids": abstraction.get("supporting_evidence_ids", []),
            "teaching_policy": {
                "concept_introduction_order": "concrete example -> mechanism -> formal abstraction",
                "conceptual_step_size": pedagogy.get("conceptual_step_size", "small_to_medium"),
                "representation_priority": "abstraction_ladder",
                "analogy_policy": pedagogy.get("analogy_domain", "faithful_only"),
                "enforced_constraints": constraints + [rev_model.get("compression_expansion_profile", "")]
            },
            "support_weight": 0.0,
            "contradiction_weight": 0.0,
            "independent_topics": [],
            "status": "active_hypothesis",
            "confidence": 0.50
        }
        
    # 3. Knowledge Organization Hypothesis
    knowledge = dna.get("knowledge_organization")
    if isinstance(knowledge, dict) and knowledge.get("dominant_pattern"):
        pattern = knowledge["dominant_pattern"]
        h_id = generate_h_id("KNOW", pattern)
        active_hypotheses[h_id] = {
            "hypothesis_id": h_id,
            "pattern": pattern,
            "source_evidence_ids": knowledge.get("supporting_evidence_ids", []),
            "teaching_policy": {
                "concept_introduction_order": "prerequisites -> relational map -> core concept",
                "conceptual_step_size": pedagogy.get("conceptual_step_size", "medium"),
                "representation_priority": "relational_graph",
                "analogy_policy": pedagogy.get("analogy_domain", "faithful_only"),
                "enforced_constraints": constraints + [rev_model.get("transfer_prediction", "")]
            },
            "support_weight": 0.0,
            "contradiction_weight": 0.0,
            "independent_topics": [],
            "status": "active_hypothesis",
            "confidence": 0.50
        }

    # 4. Learning Mechanism Hypothesis
    learn_mech = dna.get("learning_mechanism", {})
    if isinstance(learn_mech, dict) and learn_mech.get("concept_anchoring"):
        pattern = learn_mech["concept_anchoring"].get("pattern", "example_dependent")
        h_id = generate_h_id("LEARN", pattern)
        active_hypotheses[h_id] = {
            "hypothesis_id": h_id,
            "pattern": pattern,
            "source_evidence_ids": [],
            "teaching_policy": {
                "concept_introduction_order": "concrete code/tool anchor -> mechanism -> formal theory",
                "conceptual_step_size": pedagogy.get("conceptual_step_size", "small"),
                "representation_priority": "concrete_anchor",
                "analogy_policy": pedagogy.get("analogy_domain", "mechanistic"),
                "enforced_constraints": constraints
            },
            "support_weight": 0.0,
            "contradiction_weight": 0.0,
            "status": "active_hypothesis",
            "confidence": 0.50
        }

    # 5. Reasoning Style Hypothesis
    reason_style = dna.get("reasoning_style", {})
    if isinstance(reason_style, dict) and reason_style.get("primary_mode"):
        pattern = reason_style["primary_mode"].get("pattern", "mechanistic_causal")
        h_id = generate_h_id("REASON", pattern)
        active_hypotheses[h_id] = {
            "hypothesis_id": h_id,
            "pattern": pattern,
            "source_evidence_ids": [],
            "teaching_policy": {
                "concept_introduction_order": "trigger -> sequential cause-effect trace -> outcome",
                "conceptual_step_size": "medium",
                "representation_priority": "causal_chain",
                "analogy_policy": pedagogy.get("analogy_domain", "mechanistic"),
                "enforced_constraints": constraints
            },
            "support_weight": 0.0,
            "contradiction_weight": 0.0,
            "status": "active_hypothesis",
            "confidence": 0.50
        }

    return {
        "raw_forensic_profile": raw_profile, # Retain Evidence Ledger for auditability
        "active_hypotheses": active_hypotheses
    }
