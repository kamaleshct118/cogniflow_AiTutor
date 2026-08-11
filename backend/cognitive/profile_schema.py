"""
===============================================================================
 SYNAPSE COGNITIVE ENGINE — Pydantic Data Contracts (profile_schema.py)
===============================================================================
 Purpose:
   • Defines strict Pydantic structures for cognitive events, pedagogical signals,
     hypothesis states, and probe validation payloads.

 Core Logic & Hierarchy:
   ├── PedagogicalSignal          : Agent 3A evaluation signal (response quality & hypothesis effect)
   ├── CognitiveValidationPayload : Contract returned by Agent 3A to update state
   ├── CognitiveEvent            : Immutable audit record stored in cognitive_events state list
   └── HypothesisState           : Bayesian hypothesis state tracking support & contradiction weights
===============================================================================
"""

from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

class ContentGap(BaseModel, extra="forbid"):
    present: bool
    concept: Optional[str] = None
    evidence: Optional[str] = None

class BehavioralEvidence(BaseModel, extra="forbid"):
    user_response: str
    observation: str
    interpretation: str

class TeachingPolicy(BaseModel, extra="forbid"):
    concept_introduction_order: str
    conceptual_step_size: str
    representation_priority: str
    analogy_policy: str
    forbidden_analogy_families: List[str] = Field(default_factory=list)
    enforced_constraints: List[str] = Field(default_factory=list)

class PedagogicalSignal(BaseModel, extra="forbid"):
    probe_id: str
    target_concept: str
    tested_hypothesis: str
    response_quality: Literal[
        "strong",
        "adequate",
        "partial",
        "weak",
        "incorrect",
        "nonresponsive",
        "insufficient_evidence"
    ]
    hypothesis_effect: Literal[
        "support",
        "contradict",
        "inconclusive"
    ]
    evidence: BehavioralEvidence
    topic_confound_risk: Literal["low", "medium", "high"]
    observation_confidence: Literal["low", "medium", "high"]
    suggested_override: Optional[str] = None

class CognitiveValidationPayload(BaseModel, extra="forbid"):
    probe_response_status: Literal["ANSWERED", "PARTIALLY_ANSWERED", "NOT_ANSWERING_PROBE"] = "NOT_ANSWERING_PROBE"
    content_gap: ContentGap
    pedagogical_signal: Optional[PedagogicalSignal] = None

class CognitiveEvent(BaseModel, extra="forbid"):
    event_id: str
    source: Literal[
        "teacher_socratic_response",
        "diagnostic_probe",
        "gap_analysis"
    ]
    hypothesis: str
    effect: Literal["support", "contradict", "inconclusive"]
    response_quality: Literal[
        "strong",
        "adequate",
        "partial",
        "weak",
        "incorrect",
        "nonresponsive",
        "insufficient_evidence"
    ]
    
    probe_id: str
    target_concept: str
    
    user_response: str
    observation: str
    interpretation: str
    observation_confidence: Literal["low", "medium", "high"]
    topic_confound_risk: Literal["low", "medium", "high"]
    session_id: Optional[str] = None
    turn_id: Optional[int] = None
    timestamp: datetime

class HypothesisState(BaseModel):
    hypothesis_id: str
    pattern: str
    source_evidence_ids: List[str] = Field(default_factory=list)
    teaching_policy: TeachingPolicy
    support_weight: float = 0.0
    contradiction_weight: float = 0.0
    independent_topics: List[str] = Field(default_factory=list)
    status: str = "active_hypothesis"
    confidence: float = 0.5
