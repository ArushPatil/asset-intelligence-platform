"""
LLM Orchestrator Models.

Defines domain dataclasses for structured information exchanged across
Intent Classification, Service Execution, Prompt Construction, and LLM Synthesis.
All models contain Python-native data structures with zero library leakages.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Intent:
    """Represents detected user intent and service activation flags."""
    graph: bool = False
    telemetry: bool = False
    documents: bool = False
    target_asset: Optional[str] = "AHU-01"
    target_metric: Optional[str] = None
    target_space: Optional[str] = None


@dataclass
class ServiceCall:
    """Tracks execution metrics and records count for each queried service."""
    service: str
    success: bool
    execution_time_ms: float
    records_returned: int
    error_message: Optional[str] = None


@dataclass
class AssetContext:
    """Structured context retrieved from Neo4j Knowledge Graph."""
    asset_id: str
    asset_info: Optional[Dict[str, Any]] = None
    components: List[Dict[str, Any]] = field(default_factory=list)
    served_spaces: List[Dict[str, Any]] = field(default_factory=list)
    health_status: Optional[Dict[str, Any]] = None
    operating_state: Optional[Dict[str, Any]] = None
    manufacturer: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = field(default_factory=list)
    telemetry_streams: List[Dict[str, Any]] = field(default_factory=list)
    maintenance_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TelemetryContext:
    """Structured context retrieved from Telemetry Service analytics."""
    metrics_available: List[str] = field(default_factory=list)
    latest_readings: Dict[str, Any] = field(default_factory=dict)
    averages: Dict[str, float] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    anomalies: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class DocumentContext:
    """Structured context retrieved from Document RAG vector store."""
    query: str
    retrieved_chunks: List[Any] = field(default_factory=list)


@dataclass
class PromptContext:
    """Container holding aggregated multi-source context ready for prompt construction."""
    user_question: str
    intent: Intent
    graph_context: Optional[AssetContext] = None
    telemetry_context: Optional[TelemetryContext] = None
    document_context: Optional[DocumentContext] = None


from .execution_models import ExecutionPlan, PlanStep


@dataclass
class OrchestratorResponse:
    """Final output bundle produced by the LLM Orchestrator."""
    user_question: str
    intent: Intent
    service_calls: List[ServiceCall]
    prompt_used: str
    raw_llm_response: str
    final_answer: str
    total_execution_time_ms: float
    execution_plan: Optional[ExecutionPlan] = None
    graph_context: Optional[AssetContext] = None
    telemetry_context: Optional[TelemetryContext] = None
    document_context: Optional[DocumentContext] = None
    llm_backend: str = "local"
