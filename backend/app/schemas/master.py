from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MasterEventSubmission(BaseModel):
    """Event payload submitted to the Master Agent."""
    event_id: Optional[str] = Field(None, description="Identifier of the event, e.g. EVT-TEST-004")
    event_type: Optional[str] = Field(None, description="Event type string, e.g. SUPPLIER_DELAY")
    source_domain: Optional[str] = Field(None, description="Source domain agent, e.g. Procurement Agent")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Raw domain event attributes")


class NormalizationStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Event Normalization Node"
    status: Optional[str] = None
    source_domain: Optional[str] = None
    event_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    internal_entity_uuid: Optional[str] = None
    supplier: Optional[Dict[str, Any]] = None
    product: Optional[Dict[str, Any]] = None
    delay_parameters: Optional[Dict[str, Any]] = None


class PriorityStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Dynamic Scoring & Prioritization Node"
    severity: Optional[str] = None
    urgency_score: Optional[float] = None
    sla_impact: Optional[str] = None
    justification: Optional[str] = None


class ForwardImpactStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Downstream Propagation Graph Engine"
    affected_domains: List[str] = Field(default_factory=list)
    inventory_impact: Optional[Dict[str, Any]] = None
    production_impact: Optional[Dict[str, Any]] = None
    logistics_fulfillment_impact: Optional[Dict[str, Any]] = None


class BackwardImpactStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Root-Cause & SLA Audit Node"
    root_cause: Optional[str] = None
    historical_supplier_performance: Optional[Dict[str, Any]] = None
    contract_audit: Optional[Dict[str, Any]] = None


class DemandForecastingGateStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Demand & Burn-Rate Velocity Gate"
    sku: Optional[str] = None
    daily_consumption_rate: Optional[float] = None
    projected_7_day_demand: Optional[float] = None
    projected_14_day_demand: Optional[float] = None
    safety_stock_threshold: Optional[float] = None
    gate_status: Optional[str] = None
    decision_gate: Optional[str] = None


class DecisionOptimizationStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Prescriptive Trade-Off Optimizer"
    evaluated_options: List[Dict[str, Any]] = Field(default_factory=list)
    selected_recommendation: Optional[Dict[str, Any]] = None


class SmartReplenishmentStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Smart Replenishment Node"
    action_required: Optional[bool] = False
    requisition_id: Optional[str] = None
    supplier: Optional[Dict[str, Any]] = None
    replenishment_item: Optional[Dict[str, Any]] = None
    estimated_delivery_date: Optional[str] = None
    status: Optional[str] = None


class ExecutableAction(BaseModel):
    model_config = ConfigDict(extra="allow")
    action_type: str
    endpoint: Optional[str] = None
    method: Optional[str] = "POST"
    payload: Dict[str, Any] = Field(default_factory=dict)


class ExecutionBoundaryStage(BaseModel):
    model_config = ConfigDict(extra="allow")
    node: Optional[str] = "Governance & Human-in-the-Loop Gate"
    execution_mode: str = "HUMAN_IN_THE_LOOP"
    authorized_roles: List[str] = Field(default_factory=lambda: ["admin", "procurement"])
    status: str = "AWAITING_AUTHORIZATION"
    executable_actions: List[Dict[str, Any]] = Field(default_factory=list)


class MasterStages(BaseModel):
    model_config = ConfigDict(extra="allow")
    normalization: Optional[NormalizationStage] = None
    priority: Optional[PriorityStage] = None
    forward_impact: Optional[ForwardImpactStage] = None
    backward_impact: Optional[BackwardImpactStage] = None
    demand_forecasting_gate: Optional[DemandForecastingGateStage] = None
    decision_optimization: Optional[DecisionOptimizationStage] = None
    smart_replenishment: Optional[SmartReplenishmentStage] = None
    execution_boundary: Optional[ExecutionBoundaryStage] = None


class MasterPipelineResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    pipeline_execution_id: str
    event_id: str
    status: str = "COMPLETED"
    timestamp: str
    stages: MasterStages
