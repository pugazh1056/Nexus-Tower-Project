import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.schemas.master import MasterPipelineResponse, MasterEventSubmission

logger = logging.getLogger("nexus_tower.master_agent")


class MasterAgentError(HTTPException):
    """Base exception for Master Agent communication."""
    def __init__(self, status_code: int, detail: str, error_type: str = "master_agent_error"):
        super().__init__(status_code=status_code, detail={"error": error_type, "message": detail})


class MasterWebhookNotConfiguredError(MasterAgentError):
    def __init__(self, detail: str = "Master webhook URL is not configured (MASTER_WEBHOOK_URL is unset)"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail, error_type="webhook_not_configured")


class MasterTimeoutError(MasterAgentError):
    def __init__(self, detail: str = "Master webhook request timed out"):
        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=detail, error_type="master_timeout")


class MasterConnectionError(MasterAgentError):
    def __init__(self, detail: str = "Unable to connect to Master Agent webhook"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail, error_type="master_connection_failed")


class MasterMalformedResponseError(MasterAgentError):
    def __init__(self, detail: str = "Master Agent returned a malformed or invalid response schema"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail, error_type="master_malformed_response")


class MasterAgentService:
    def __init__(self):
        self._latest_execution: Optional[MasterPipelineResponse] = None

    def get_latest_execution(self) -> Optional[MasterPipelineResponse]:
        """Returns the most recently recorded Master Agent execution result."""
        return self._latest_execution

    def set_latest_execution(self, response: MasterPipelineResponse) -> None:
        """Stores a successful Master Agent execution in cache."""
        self._latest_execution = response

    async def forward_to_master(self, event_data: MasterEventSubmission) -> MasterPipelineResponse:
        """
        Transmits a domain event to the Master Agent webhook, enforces strict validation
        against the verified output contract, and stores the execution state.
        """
        webhook_url = settings.master_webhook_url

        # Check webhook URL configuration
        if not webhook_url:
            logger.warning("MASTER_WEBHOOK_URL is not set. Cannot dispatch to external webhook.")
            raise MasterWebhookNotConfiguredError(
                "Master Webhook is not configured. Set MASTER_WEBHOOK_URL in environment configuration."
            )

        payload = event_data.model_dump()

        try:
            async with httpx.AsyncClient(timeout=settings.master_webhook_timeout_seconds) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                )

            if response.status_code >= 400:
                logger.error(f"Master webhook returned HTTP {response.status_code}: {response.text}")
                raise MasterConnectionError(
                    f"Master webhook returned HTTP {response.status_code}: {response.text[:200]}"
                )

            raw_json = response.json()

        except httpx.TimeoutException as exc:
            logger.error(f"Master webhook timed out after {settings.master_webhook_timeout_seconds}s: {exc}")
            raise MasterTimeoutError(
                f"Master webhook timed out after {settings.master_webhook_timeout_seconds}s"
            )
        except httpx.RequestError as exc:
            logger.error(f"Master webhook connection error: {exc}")
            raise MasterConnectionError(f"Failed to connect to Master Agent webhook: {str(exc)}")
        except ValueError as exc:
            logger.error(f"Failed to parse Master webhook response as JSON: {exc}")
            raise MasterMalformedResponseError("Master Agent response is not valid JSON")

        # Strict validation against verified Master output schema
        try:
            validated_response = MasterPipelineResponse.model_validate(raw_json)
            self._latest_execution = validated_response
            return validated_response
        except Exception as exc:
            logger.error(f"Master response schema validation error: {exc}")
            raise MasterMalformedResponseError(f"Master output failed schema validation: {str(exc)}")

    def get_verified_test_pipeline(self, event_id: str = "EVT-TEST-004") -> MasterPipelineResponse:
        """
        Returns the verified reference execution output for test scenarios.
        Used for verification, testing, and initial demonstration without inventing schema fields.
        """
        data = {
            "pipeline_execution_id": f"EXEC-MST-20260915-{event_id.replace('EVT-TEST-', '')}",
            "event_id": event_id,
            "status": "COMPLETED",
            "timestamp": "2026-09-15T19:06:00Z",
            "stages": {
                "normalization": {
                    "node": "Event Normalization Node",
                    "status": "VALIDATED",
                    "source_domain": "Procurement Agent",
                    "event_type": "SUPPLIER_DELAY",
                    "entity_type": "purchase_order",
                    "entity_id": "PO-001",
                    "internal_entity_uuid": "ccaa359c-72a7-4a9a-adde-abcad89cf171",
                    "supplier": {
                        "id": "545e9817-ce6b-4a0f-9a6f-9b5b29041090",
                        "supplier_code": "SUP-001",
                        "name": "Dairy Pure Co"
                    },
                    "product": {
                        "id": "b462b2e9-4a83-4e3c-af52-dd87ab42d06d",
                        "sku": "MILK-001",
                        "name": "Milk",
                        "category": "Dairy"
                    },
                    "delay_parameters": {
                        "delay_days": 8,
                        "original_expected_date": "2026-09-06",
                        "revised_expected_date": "2026-09-14"
                    }
                },
                "priority": {
                    "node": "Dynamic Scoring & Prioritization Node",
                    "severity": "CRITICAL",
                    "urgency_score": 92.4,
                    "sla_impact": "BREACH_IMMINENT",
                    "justification": "8-day delay on primary feedstock with single-silo buffer below 38h threshold"
                },
                "forward_impact": {
                    "node": "Downstream Propagation Graph Engine",
                    "affected_domains": [
                        "Inventory",
                        "Production",
                        "Logistics"
                    ],
                    "inventory_impact": {
                        "warehouse_location": "Cold Hub Alpha - Bay 4",
                        "current_available_quantity": 30.0,
                        "target_stock": 100.0,
                        "deficit": 70.0,
                        "runway_hours": 28.8
                    },
                    "production_impact": {
                        "affected_production_order": "PRD-MILK-202609",
                        "production_order_uuid": "d3c4d5e6-a7b8-4b9c-0d1e-2f3a4b5c6d7e",
                        "scheduled_line": "Filling Line 01",
                        "planned_quantity": 800.0,
                        "feedstock_required": 840.0,
                        "material_shortage": 795.0,
                        "starvation_hazard": "CRITICAL_IDLE_RISK"
                    },
                    "logistics_fulfillment_impact": {
                        "affected_distribution_centers": [
                            "Rotterdam Hub 04",
                            "Antwerp Distribution"
                        ],
                        "estimated_revenue_at_risk": 14200.0,
                        "fill_rate_projection_without_action": 0.42
                    }
                },
                "backward_impact": {
                    "node": "Root-Cause & SLA Audit Node",
                    "root_cause": "Refrigeration compressor breakdown during cold-chain pre-transit",
                    "historical_supplier_performance": {
                        "supplier_code": "SUP-001",
                        "total_historical_orders": 4,
                        "on_time_delivery_rate": 0.75,
                        "average_lead_time_days": 3.5,
                        "defect_rate": 0.0
                    },
                    "contract_audit": {
                        "contract_id": "CTR-SUP001-2026",
                        "sla_minimum": 0.95,
                        "late_delivery_penalty_rate_per_day": 0.02,
                        "applicable_penalty_amount": 800.0
                    }
                },
                "demand_forecasting_gate": {
                    "node": "Demand & Burn-Rate Velocity Gate",
                    "sku": "MILK-001",
                    "daily_consumption_rate": 25.0,
                    "projected_7_day_demand": 175.0,
                    "projected_14_day_demand": 350.0,
                    "safety_stock_threshold": 100.0,
                    "gate_status": "THRESHOLD_BREACHED_ACTION_REQUIRED",
                    "decision_gate": "PASSED_TO_OPTIMIZER"
                },
                "decision_optimization": {
                    "node": "Prescriptive Trade-Off Optimizer",
                    "evaluated_options": [
                        {
                            "option_id": "OPT-01",
                            "strategy": "DO_NOTHING_WAIT",
                            "cost": 0.0,
                            "production_downtime_loss": 14200.0,
                            "net_financial_impact": -14200.0,
                            "otif_projection": 0.42,
                            "score": 24.5
                        },
                        {
                            "option_id": "OPT-02",
                            "strategy": "EXPEDITE_EXISTING_CARRIER",
                            "cost": 450.0,
                            "production_downtime_loss": 3500.0,
                            "net_financial_impact": -3950.0,
                            "otif_projection": 0.88,
                            "score": 81.2
                        },
                        {
                            "option_id": "OPT-03",
                            "strategy": "TRIGGER_BACKUP_REPLENISHMENT_AND_EXPEDITE",
                            "cost": 450.0,
                            "production_downtime_loss": 0.0,
                            "net_financial_impact": 13750.0,
                            "otif_projection": 0.994,
                            "score": 94.8
                        }
                    ],
                    "selected_recommendation": {
                        "recommendation_id": "REC-2026-OPT-004",
                        "action_strategy": "TRIGGER_BACKUP_REPLENISHMENT_AND_EXPEDITE",
                        "title": "Expedite Raw Dairy Consignment via Cold-Chain Priority Corridor",
                        "description": "Authorizes a $450 surcharge waiver to prioritize tanker transit. Directly protects filling Line 01 continuity and averts an estimated $14,200 in idle production loss.",
                        "confidence_score": 0.984,
                        "net_protected_value": 13750.0
                    }
                },
                "smart_replenishment": {
                    "node": "Smart Replenishment Node",
                    "action_required": True,
                    "requisition_id": "REQ-AUTO-2026-004",
                    "supplier": {
                        "supplier_id": "a1b2c3d4-0005-4a7b-8c9d-0e1f2a3b4c5d",
                        "supplier_code": "SUP-005",
                        "name": "Apex Dairy Farms",
                        "tier": "backup",
                        "lead_time_days": 4
                    },
                    "replenishment_item": {
                        "product_id": "c5e6f7a8-1111-4b2c-8d3e-4f5a6b7c8d9e",
                        "sku": "RAW-MILK-01",
                        "name": "Raw Pasteurization Feedstock",
                        "quantity": 800.0,
                        "unit": "litre",
                        "unit_price": 37.0,
                        "total_amount": 29600.0,
                        "currency": "USD"
                    },
                    "estimated_delivery_date": "2026-09-18",
                    "status": "PROPOSED_PENDING_APPROVAL"
                },
                "execution_boundary": {
                    "node": "Governance & Human-in-the-Loop Gate",
                    "execution_mode": "HUMAN_IN_THE_LOOP",
                    "authorized_roles": [
                        "admin",
                        "procurement"
                    ],
                    "status": "AWAITING_AUTHORIZATION",
                    "executable_actions": [
                        {
                            "action_type": "CREATE_PURCHASE_ORDER",
                            "endpoint": "/api/purchase-orders/",
                            "method": "POST",
                            "payload": {
                                "supplier_id": "a1b2c3d4-0005-4a7b-8c9d-0e1f2a3b4c5d",
                                "po_number": "PO-EMERGENCY-001",
                                "priority": "high",
                                "items": [
                                    {
                                        "product_id": "c5e6f7a8-1111-4b2c-8d3e-4f5a6b7c8d9e",
                                        "quantity": 800.0,
                                        "unit_price": 37.0
                                    }
                                ],
                                "notes": "Emergency feedstock replenishment for PRD-MILK-202609 via Apex Dairy Farms"
                            }
                        },
                        {
                            "action_type": "BROADCAST_DOMAIN_ALERT",
                            "endpoint": "/api/alerts/",
                            "method": "POST",
                            "payload": {
                                "title": "Raw Milk Feedstock Expedite Dispatched",
                                "severity": "high",
                                "source_domain": "procurement",
                                "description": "Backup consignment authorized from Apex Dairy Farms. Production run PRD-MILK-202609 protected."
                            }
                        }
                    ]
                }
            }
        }
        res = MasterPipelineResponse.model_validate(data)
        self._latest_execution = res
        return res


master_agent_service = MasterAgentService()
