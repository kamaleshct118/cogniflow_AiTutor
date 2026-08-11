"""
===============================================================================
 SYNAPSE COGNITIVE ENGINE — Bayesian Profile Reducer (profile_reducer.py)
===============================================================================
 Purpose:
   • Mathematical engine implementing Bayesian weight updates based on
     Socratic Probe evidence evaluation.

 Core Logic & Hierarchy:
   ├── apply_event_to_profile() : Updates hypothesis confidence weights
   ├── Confidence Formula      : Confidence = Support / (Support + Contradiction + 1.0)
   └── Weight Promotion Rule   : Promotes hypothesis to preferred_representation when >=3.0
===============================================================================
"""

from typing import Dict, Any
from .profile_schema import CognitiveEvent, HypothesisState

EVIDENCE_WEIGHT = {
    "strong": 1.0,
    "adequate": 0.75,
    "partial": 0.4,
    "weak": 0.2,
    "incorrect": 1.0,
    "nonresponsive": 0.0,
    "insufficient_evidence": 0.0,
}

CONFIDENCE_WEIGHT_MODIFIER = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.3
}

def calculate_confidence(support_weight: float, contradiction_weight: float) -> float:
    total = support_weight + contradiction_weight
    if total == 0:
        return 0.5
    return support_weight / (total + 1.0)

def update_hypothesis_status(hypothesis: HypothesisState) -> None:
    if hypothesis.confidence > 0.75:
        hypothesis.status = "preferred_representation"
    elif hypothesis.confidence >= 0.45:
        hypothesis.status = "active_hypothesis"
    elif hypothesis.confidence >= 0.25:
        hypothesis.status = "weak_hypothesis"
    else:
        hypothesis.status = "deactivated"

def apply_event_to_profile(profile_dict: Dict[str, Any], event: CognitiveEvent, topic: str = "general") -> Dict[str, Any]:
    # Ensure active_hypotheses dict exists in profile
    if "active_hypotheses" not in profile_dict:
        profile_dict["active_hypotheses"] = {}
        
    hyp_dict = profile_dict["active_hypotheses"].get(event.hypothesis)
    if not hyp_dict:
        hyp = HypothesisState(
            hypothesis_id=event.hypothesis,
            pattern=event.hypothesis,
            teaching_policy={
                "concept_introduction_order": "standard",
                "conceptual_step_size": "medium",
                "representation_priority": "standard",
                "analogy_policy": "standard",
                "enforced_constraints": []
            }
        )
    else:
        hyp = HypothesisState(**hyp_dict)
        
    base_weight = EVIDENCE_WEIGHT.get(event.response_quality, 0.0)
    conf_mod = CONFIDENCE_WEIGHT_MODIFIER.get(event.observation_confidence, 0.7)
    weight = base_weight * conf_mod
    
    if event.effect == "support":
        hyp.support_weight += weight
    elif event.effect == "contradict":
        hyp.contradiction_weight += weight
        
    if topic not in hyp.independent_topics:
        hyp.independent_topics.append(topic)
        
    hyp.confidence = calculate_confidence(hyp.support_weight, hyp.contradiction_weight)
    update_hypothesis_status(hyp)
    
    if qualifies_for_global_update(hyp):
        # Commit back to profile
        profile_dict["active_hypotheses"][event.hypothesis] = hyp.model_dump()
        
    return profile_dict

def qualifies_for_global_update(hypothesis: HypothesisState) -> bool:
    meaningful_evidence = hypothesis.support_weight + hypothesis.contradiction_weight
    return meaningful_evidence >= 3.0 and len(hypothesis.independent_topics) >= 2
