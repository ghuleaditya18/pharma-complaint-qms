from typing import Any, Dict, TypedDict


class AgentState(TypedDict, total=False):
    user_message: str
    current_form: Dict[str, Any]
    current_risk: Dict[str, Any]
    action: str  # 'log', 'edit', 'inquire'
    extracted_fields: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    completeness_score: int
    reply: str
