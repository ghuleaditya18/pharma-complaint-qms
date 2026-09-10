from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

NOISE_STRINGS = {
    "none", "null", "n/a", "na", "not specified", "unknown", "field",
    "extracted information", "attribute", "value", "not available", "blank", "-"
}


def _sanitize_string_value(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, str):
        v_stripped = v.strip()
        if v_stripped.lower() in NOISE_STRINGS or v_stripped == "":
            return ""
        return v_stripped
    return v


FIELD_LIST = [
    "complaint_source",
    "customer_name",
    "product_name",
    "product_strength",
    "batch_number",
    "affected_quantity",
    "manufacturing_date",
    "expiry_date",
    "originating_site_block",
    "impacted_npm",
    "complaint_category",
    "defect_description",
]


class ComplaintFields(BaseModel):
    """Editable 12 fields of a complaint intake record."""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category: Optional[str] = None
    defect_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator(*FIELD_LIST, mode="before")
    @classmethod
    def clean_noise(cls, v: Any) -> Any:
        return _sanitize_string_value(v)


class RiskAssessment(BaseModel):
    """Risk assessment details for a complaint."""
    severity: Optional[str] = None  # 'Critical', 'Major', 'Minor'
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Request payload for chat-assisted complaint intake."""
    message: str
    current_form: Optional[Dict[str, Any]] = Field(default_factory=dict)
    current_risk: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response payload for chat-assisted complaint intake."""
    reply: str
    updated_form: Dict[str, Any]
    updated_risk: Dict[str, Any]
    completeness_score: int


class ComplaintCreate(BaseModel):
    """Payload to create or finalize a complaint in QMS database."""
    complaint_id: Optional[str] = None
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category: Optional[str] = None
    defect_description: Optional[str] = None

    severity: Optional[str] = None
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None
    completeness_score: Optional[int] = 0
    status: Optional[str] = "Logged"

    model_config = ConfigDict(from_attributes=True)

    @field_validator(*FIELD_LIST, mode="before")
    @classmethod
    def clean_noise(cls, v: Any) -> Any:
        return _sanitize_string_value(v)


class ComplaintResponse(BaseModel):
    """Full serialized representation of a Complaint."""
    id: int
    complaint_id: str
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category: Optional[str] = None
    defect_description: Optional[str] = None

    severity: Optional[str] = None
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None
    completeness_score: Optional[int] = 0
    status: str = "Logged"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator(*FIELD_LIST, mode="before")
    @classmethod
    def clean_noise(cls, v: Any) -> Any:
        return _sanitize_string_value(v)



