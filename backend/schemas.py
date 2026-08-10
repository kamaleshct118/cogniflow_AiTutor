from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# AGENT 1: COGNITIVE MAPPER SCHEMAS
# ---------------------------------------------------------

class InputQuality(BaseModel):
    word_count: int
    modality: str
    language_proficiency: str
    structure_type: str
    confidence: str
    confidence_basis: str

class CausalBridging(BaseModel):
    dominant_pattern: str
    pattern_ratios: Dict[str, float]
    evidence: List[str]

class NecessityFraming(BaseModel):
    dominant: str
    ratio: float
    evidence: List[str]

class AbstractionMarker(BaseModel):
    phrase: str
    type: str
    signal: str
    clause_index: int

class RealityAnchors(BaseModel):
    observed_types: List[str]
    dominant: str
    diversity_count: int
    evidence_per_type: Dict[str, List[str]]

class SyntacticRegister(BaseModel):
    clause_length: str
    formality: str
    hedging_density: float
    self_correction_present: bool

class LexicalDensity(BaseModel):
    domain_term_ratio: float
    usage_quality: str
    assessment_basis: str

class SyntaxOfThought(BaseModel):
    causal_bridging: CausalBridging
    necessity_framing: NecessityFraming
    abstraction_markers: List[AbstractionMarker]
    reality_anchors: RealityAnchors
    syntactic_register: SyntacticRegister
    lexical_density: LexicalDensity

class ObservedPrerequisite(BaseModel):
    concept: str
    prerequisite_mentioned_before: str
    type: str

class DetailDistribution(BaseModel):
    subtopics_mentioned: List[str]
    clause_count_per_subtopic: Dict[str, int]
    relative_density: str

class ComplexityApproach(BaseModel):
    observed_strategy: str
    evidence: List[str]

class EpistemicSignature(BaseModel):
    complexity_approach: ComplexityApproach
    observed_prerequisites: List[ObservedPrerequisite]
    detail_distribution: DetailDistribution

class CognitiveMechanics(BaseModel):
    input_quality: InputQuality
    syntax_of_thought: SyntaxOfThought
    epistemic_signature: EpistemicSignature

class TopicStructurePayload(BaseModel):
    topic: str
    canonical_components: List[str]
    structural_type: str
    key_abstractions: List[str]

class FrictionItem(BaseModel):
    topic_component: str
    user_mechanic: str
    predicted_friction: str
    evidence_basis: str
    severity: str

class DepthOverlay(BaseModel):
    peaks_mapped: List[str]
    valleys_mapped: List[str]

class PrerequisiteGap(BaseModel):
    concept: str
    user_has: str
    topic_requires: str

class GroundedProfile(BaseModel):
    topic: str
    topic_structure: TopicStructurePayload
    friction_map: List[FrictionItem]
    depth_overlay: DepthOverlay
    prerequisite_gaps: List[PrerequisiteGap]

class PedagogicalGuidance(BaseModel):
    step_granularity: str
    transition_style: str
    require_code_before_math: bool
    trigger_diagnostic_probe: bool
    analogy_family: str
    forbidden_analogy_families: List[str]

class InterventionTrigger(BaseModel):
    condition: str
    action: str

class TutorDirective(BaseModel):
    pedagogical_guidance: PedagogicalGuidance
    intervention_triggers: List[InterventionTrigger]
    progress_markers: List[str]

class EvidenceLedgerItem(BaseModel):
    evidence_id: str
    quote: str
    observation: str
    hypothesis: str
    alternative_explanations: List[str]
    topic_confound_risk: str
    stability: str
    confidence: str

class ClauseStructure(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]

class CausalReasoning(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]
    counter_evidence_ids: List[str] = Field(default_factory=list)

class AbstractionLadderMovement(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]

class AtomicEvidenceMap(BaseModel):
    clause_structure: ClauseStructure
    causal_reasoning: CausalReasoning
    abstraction_ladder_movement: AbstractionLadderMovement

class CertaintyMarkers(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]

class ConcreteAnchorDependence(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]

class EpistemicSignature(BaseModel):
    certainty_markers: CertaintyMarkers
    concrete_anchor_dependence: ConcreteAnchorDependence

class KnowledgeOrganization(BaseModel):
    dominant_pattern: str
    supporting_evidence_ids: List[str]

class CognitiveDna(BaseModel):
    evidence_ledger: List[EvidenceLedgerItem]
    atomic_evidence_map: AtomicEvidenceMap
    epistemic_signature: EpistemicSignature
    knowledge_organization: KnowledgeOrganization

class ReverseEngineeredModel(BaseModel):
    transfer_prediction: str
    predicted_friction_points: List[str]
    compression_expansion_profile: str

class PedagogicalTelemetry(BaseModel):
    concept_introduction_order: str
    conceptual_step_size: str
    analogy_domain: str

class TutorDirective(BaseModel):
    pedagogical_telemetry: PedagogicalTelemetry
    enforced_constraints: List[str]

class CognitiveProfilePayload(BaseModel):
    cognitive_dna: CognitiveDna
    reverse_engineered_model: ReverseEngineeredModel
    tutor_directive: TutorDirective


# ---------------------------------------------------------
# AGENT 4: TEACHER TUTOR SCHEMAS
# ---------------------------------------------------------

from typing import Literal

class SocraticQuestion(BaseModel, extra="forbid"):
    question: str
    
    # What kind of question is this pedagogically?
    probe_type: Literal[
        "pedagogical_validation",
        "clarification",
        "diagnostic"
    ]
    
    # What cognitive operation does the question test?
    probe_mode: Literal[
        "recall",
        "application",
        "mechanism_analysis",
        "comparison",
        "prediction",
        "causal_reasoning"
    ]
    
    tests_hypothesis: Optional[str] = None
    target_concept: str
    expected_evidence: str
    failure_signal: str

class TeacherProbe(SocraticQuestion):
    probe_id: str

class TeacherResponsePayload(BaseModel, extra="forbid"):
    requires_research_fallback: Optional[bool] = False
    answer: str = Field(..., description="The natural, seamlessly integrated explanation answering the user's question.")
    explanation_depth: Literal["basic", "intermediate", "deep"]
    concepts_covered: List[str]
    evidence_boundary: Optional[str] = Field(None, description="Explicit statement of what is NOT covered by the research, if applicable.")
    socratic_question: SocraticQuestion = Field(..., description="Single targeted Socratic question")

# ---------------------------------------------------------
# AGENT 5: GUARDRAIL SCHEMAS
# ---------------------------------------------------------
class GuardrailDecision(BaseModel, extra="forbid"):
    classification: Literal["IN_BOUNDS", "METAPHOR_BRIDGE", "OFF_TOPIC_PIVOT", "CONVERSATIONAL_GREETING", "META_QUERY"]
    requires_deep_research: bool = Field(False, description="True if the user's question is highly complex and requires Agent 6 live search")

# ---------------------------------------------------------
# KNOWLEDGE GAP FAB SCHEMAS
# ---------------------------------------------------------
class GapSuggestion(BaseModel, extra="forbid"):
    type: Literal["COMPREHENSION", "COVERAGE"]
    missing_subtopic: str
    reason: str
    button_label: str = Field(..., description="Actionable button text, e.g., 'Explore Positional Encoding'")

class KnowledgeGapAnalysis(BaseModel):
    diagnostic_summary: str = Field(..., description="Summary of what the user has mastered vs missed based on history")
    suggestions: List[GapSuggestion] = Field(..., description="List of interactive buttons to generate lessons for missing gaps")

# ---------------------------------------------------------
# AGENT 6: RESEARCH PAYLOAD SCHEMAS
# ---------------------------------------------------------
class SourceSupportedFact(BaseModel, extra="forbid"):
    fact: str
    source_excerpt: str
    confidence: Literal["low", "medium", "high"]

class ResearchPayload(BaseModel, extra="forbid"):
    source_url: Optional[str] = None
    source_domain: str = Field(..., description="Source of the information")
    source_title: Optional[str] = None
    source_supported_facts: List[SourceSupportedFact] = Field(..., description="List of high-density un-simplified technical facts")
    code_or_math_snippet: Optional[str] = Field(None, description="Raw code block or LaTeX formula if applicable")
    canonical_subtopics: List[str] = Field(..., description="List of subtopics covered in this research")
    retrieved_at: Optional[str] = None
    research_status: Optional[str] = None

# ---------------------------------------------------------
# AGENT 2: SCOPE SIZER / WAVELENGTH SETTER SCHEMAS
# ---------------------------------------------------------
class SearchQuery(BaseModel, extra="forbid"):
    query: str
    search_depth: Literal["basic", "advanced"] = "advanced"
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)

class ScopeSizerPayload(BaseModel, extra="forbid"):
    original_input: str
    detected_wavelength: Literal["MACRO", "MICRO"]
    adapted_learning_scope: str
    user_facing_explanation: str
    agent_6_queries: List[SearchQuery]
