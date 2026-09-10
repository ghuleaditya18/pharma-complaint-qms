import json
import logging
import re
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from app.agent.prompts import (
    GENERATE_REPLY_PROMPT,
    INTENT_AND_EXTRACTION_PROMPT,
    RISK_ASSESSMENT_PROMPT,
)
from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize ChatGroq LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=settings.GROQ_API_KEY or "placeholder",
)

NOISE_STRINGS = {
    "field", "extracted information", "attribute", "value", "field name",
    "not specified", "n/a", "na", "none", "unknown", "null", "not available", "blank", "-"
}


def _is_active_api_key(key: str) -> bool:
    """Check if the Groq API key is validly configured."""
    return bool(key and key.strip() and "your_groq_api_key" not in key.lower())


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON object from LLM response text."""
    if not text:
        return None
    cleaned_text = text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        cleaned_text = cleaned_text.strip()

    match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
    if not match:
        return None

    json_str = match.group(0).strip()
    json_str = re.sub(r",\s*([\}\]])", r"\1", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"LLM Parsing error: {e}")
        traceback.print_exc()
        logger.warning(f"LLM Parsing error: {e}")
        return None


def _sanitize_extracted_fields(extracted: Dict[str, Any], raw_message: str = "", action: str = "log") -> Dict[str, Any]:
    """Sanitize extracted fields for 12 AIVOA complaint specification fields."""
    sanitized: Dict[str, Any] = {}

    alias_map = {
        "product_strength_grade": "product_strength",
        "strength_grade": "product_strength",
        "complainant_name": "customer_name",
        "complainant": "customer_name",
        "defect_category": "complaint_category",
    }

    for key, val in extracted.items():
        if val is None:
            continue
        val_str = str(val).strip()
        if val_str.lower() in NOISE_STRINGS or val_str == "":
            continue

        target_key = alias_map.get(key, key)
        sanitized[target_key] = val_str

    # Date normalization and sanity check
    mfg_date = sanitized.get("manufacturing_date")
    exp_date = sanitized.get("expiry_date")
    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def _normalize_date_str(d_str: str) -> Optional[str]:
        if not d_str:
            return None
        if date_regex.match(d_str):
            return d_str
        for fmt in ("%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y.%m.%d", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(d_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return d_str

    if mfg_date:
        norm_mfg = _normalize_date_str(mfg_date)
        if norm_mfg:
            sanitized["manufacturing_date"] = norm_mfg

    if exp_date:
        norm_exp = _normalize_date_str(exp_date)
        if norm_exp:
            sanitized["expiry_date"] = norm_exp

    cur_mfg = sanitized.get("manufacturing_date")
    cur_exp = sanitized.get("expiry_date")
    if cur_mfg and cur_exp and date_regex.match(cur_mfg) and date_regex.match(cur_exp):
        if cur_mfg > cur_exp:
            sanitized["manufacturing_date"], sanitized["expiry_date"] = cur_exp, cur_mfg

    # Automatic Deduction Rules:
    msg_lower = (raw_message + " " + sanitized.get("defect_description", "")).lower()

    if any(w in msg_lower for w in ["discolor", "coloration", "capping", "dissolution", "blister", "bottle", "capsule", "seal"]):
        if "originating_site_block" not in sanitized:
            sanitized["originating_site_block"] = "Packaging" if any(w in msg_lower for w in ["blister", "bottle", "seal"]) else "Manufacturing"
        if "impacted_npm" not in sanitized:
            sanitized["impacted_npm"] = "Primary Packaging (Bottle)" if "bottle" in msg_lower else "Blister Pack"
        if "complaint_category" not in sanitized:
            sanitized["complaint_category"] = "Product Defect - Discoloration"

    if any(w in msg_lower for w in ["api", "raw material", "synthesis", "foreign matter", "particle", "drum"]):
        if "originating_site_block" not in sanitized:
            sanitized["originating_site_block"] = "Synthesis / Active Material Processing"
        if "impacted_npm" not in sanitized:
            sanitized["impacted_npm"] = "Fiber Drum Liner"
        if "complaint_category" not in sanitized:
            sanitized["complaint_category"] = "Contamination - Foreign Matter"

    if sanitized.get("customer_name") and "complaint_source" not in sanitized:
        cust = sanitized["customer_name"].lower()
        if "hospital" in cust:
            sanitized["complaint_source"] = "Hospital"
        elif "pharmacy" in cust or "store" in cust:
            sanitized["complaint_source"] = "Pharmacy"
        elif "distributor" in cust or "wholesaler" in cust:
            sanitized["complaint_source"] = "Distributor"
        else:
            sanitized["complaint_source"] = "Pharmacy"

    # Defect Description Fix: MUST NEVER BE EMPTY whenever any fields are extracted on log action
    if not sanitized.get("defect_description") and sanitized and action != "edit":
        prod = sanitized.get("product_name", "Product")
        batch = sanitized.get("batch_number", "Unspecified Batch")
        cat = sanitized.get("complaint_category", "Quality Discrepancy")
        qty = sanitized.get("affected_quantity", "")
        qty_str = f" affecting {qty}" if qty else ""
        sanitized["defect_description"] = f"Quality complaint logged for {prod} (Batch: {batch}){qty_str} regarding {cat}."

    return sanitized


def _fallback_parse_and_extract(message: str, current_form: Dict[str, Any]) -> Dict[str, Any]:
    """Robust rule-based fallback parser when LLM is unavailable."""
    msg_lower = message.lower()
    is_edit = any(w in msg_lower for w in ["change", "update", "correct", "edit", "instead of", "not "])
    is_inquire = any(w in msg_lower for w in ["how to", "what is", "can i", "procedure", "sop", "policy"]) and not any(
        w in msg_lower for w in ["defect", "batch", "complaint", "strip", "tablet", "vial", "bottle", "capsule"]
    )

    action = "edit" if is_edit else ("inquire" if is_inquire else "log")
    extracted: Dict[str, Any] = {}

    iso_mfg = re.search(
        r"(?:manufacturing|mfg|manufacture)(?:\s+date)?(?:\s+is)?[\s:]+([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9]{2}|[A-Za-z]+\s+\d{4})",
        message,
        re.IGNORECASE,
    )
    if iso_mfg:
        extracted["manufacturing_date"] = iso_mfg.group(1).strip()
    else:
        mfg_match = re.search(
            r"(?:manufacturing|mfg|manufacture)(?:\s+date)?(?:\s+is)?[\s:]+([A-Za-z0-9\s,-]+?)(?=\s+(?:for|with|batch|lot)|[,\.]|$)",
            message,
            re.IGNORECASE,
        )
        if mfg_match:
            extracted["manufacturing_date"] = mfg_match.group(1).strip()

    iso_exp = re.search(
        r"(?:expiry|exp|expiration)(?:\s+date)?(?:\s+is)?[\s:]+([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9]{2}|[A-Za-z]+\s+\d{4})",
        message,
        re.IGNORECASE,
    )
    if iso_exp:
        extracted["expiry_date"] = iso_exp.group(1).strip()
    else:
        exp_match = re.search(
            r"(?:expiry|exp|expiration)(?:\s+date)?(?:\s+is)?[\s:]+([A-Za-z0-9\s,-]+?)(?=\s+(?:for|with|batch|lot)|[,\.]|$)",
            message,
            re.IGNORECASE,
        )
        if exp_match:
            extracted["expiry_date"] = exp_match.group(1).strip()

    cust_match = (
        re.search(r"^(?:the\s+)?([A-Za-z0-9\s]+(?:Pharmacy|Hospital|Clinic|Distributor|Labs|Health))\s+reported", message, re.IGNORECASE) or
        re.search(r"(?:reported by|from|complaint:?)\s+([A-Za-z0-9\s]+(?:Pharmacy|Hospital|Clinic|Distributor|Labs|Health))", message, re.IGNORECASE) or
        re.search(r"(?:complainant|reported by|customer|from)(?:\s+is)?[\s:]+([A-Za-z0-9\s\.\(\)]+?)(?=\s+(?:for|with|batch|lot)|[,\n]|$)", message, re.IGNORECASE)
    )
    if cust_match:
        cust_str = cust_match.group(1).strip()
        if cust_str.endswith(".") and not any(cust_str.endswith(t) for t in ["Dr.", "Mr.", "Mrs.", "Ms.", "Prof."]):
            cust_str = cust_str[:-1].strip()
        if cust_str.lower() not in NOISE_STRINGS:
            extracted["customer_name"] = cust_str

    if "pharmacy" in msg_lower:
        extracted["complaint_source"] = "Pharmacy"
    elif "hospital" in msg_lower:
        extracted["complaint_source"] = "Hospital"
    elif "clinic" in msg_lower:
        extracted["complaint_source"] = "Clinic"
    elif "distributor" in msg_lower or "wholesaler" in msg_lower:
        extracted["complaint_source"] = "Distributor"
    elif "patient" in msg_lower or "physician" in msg_lower or "dr." in msg_lower:
        extracted["complaint_source"] = "Patient"

    batch_match = re.search(
        r"(?:batch\s*(?:number|no)?|lot\s*(?:number|no)?)(?:\s+(?:to|is|=|:))*\s*[:=]?\s*([A-Za-z0-9\-]+)",
        message,
        re.IGNORECASE,
    )
    if batch_match:
        extracted["batch_number"] = batch_match.group(1).strip()

    prod_match = (
        re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Capsules|Tablets|Suspension|Syrup|Injection|API|Ointment|Cream|Solution))\b", message) or
        re.search(r"\b([A-Za-z]+(?:cillin|formin|statin|zole|fenac|mol|cin|pam)?\s+(?:Capsules|Tablets|Suspension|Syrup|Injection|API|Ointment|Cream|Solution))\b", message, re.IGNORECASE) or
        re.search(r"(?:product\s*(?:name)?|drug\s*(?:name)?)(?:\s+(?:to|is|=|:))*\s*[:=]?\s*([A-Za-z0-9\s]+?)(?:,|\.|\s+with|\s+batch|\s+lot|$)", message, re.IGNORECASE)
    )
    if prod_match:
        prod_name = prod_match.group(1).strip()
        if prod_name.lower() not in NOISE_STRINGS:
            extracted["product_name"] = prod_name

    qty_match = re.search(r"(\d+\s*(?:strips?|vials?|bottles?|packs?|cartons?|tablets?|capsules?|kg|g|units?))", message, re.IGNORECASE)
    if qty_match:
        extracted["affected_quantity"] = qty_match.group(1).strip()

    strength_match = re.search(r"(\d+\s*(?:mg|g|ml|mcg|%)(?:/\w+)?|API Grade)", message, re.IGNORECASE)
    if strength_match:
        extracted["product_strength"] = strength_match.group(1).strip()

    clean_desc = re.sub(r"(?i)\s*(?:please\s+)?log\s+(?:this\s+)?complaint:?.*$", "", message).strip()
    clean_desc = re.sub(r"(?i)^(?:please\s+)?log\s+(?:this\s+)?complaint:?\s*", "", clean_desc).strip()

    if any(w in msg_lower for w in ["broken", "leak", "contaminat", "seal", "scuff", "color", "discolor", "chipping", "capping", "particle", "foil", "damaged"]):
        extracted["defect_description"] = clean_desc if clean_desc else message

    sanitized = _sanitize_extracted_fields(extracted, message, action=action)

    return {
        "action": action,
        "extracted_fields": sanitized,
    }


def _fallback_evaluate_risk(defect: str, product: str, quantity: str) -> Dict[str, Any]:
    """GMP-compliant rule-based risk evaluation fallback for AIVOA Risk Assessment."""
    d = defect.lower()

    if any(w in d for w in ["microbial", "contamination", "potency", "superpoten", "subpoten", "glass", "metal", "foreign particle", "steril"]):
        return {
            "severity": "Critical",
            "suggested_next_action": "Issue Immediate Batch Recall & Quarantine",
            "initial_risk_assessment": "Critical product contamination or active material impurity defect posing immediate patient safety risk.",
        }

    if any(w in d for w in ["seal", "blister", "unsealed", "leak", "discolor", "broken", "weight variation", "chipping", "capping"]):
        return {
            "severity": "Major",
            "suggested_next_action": "Route to QA Investigation & Issue Replacement",
            "initial_risk_assessment": "Potential moisture ingress or primary packaging seal failure leading to product degradation or capsule discoloration.",
        }

    return {
        "severity": "Minor",
        "suggested_next_action": "Log Incident for Quality Trend Analysis",
        "initial_risk_assessment": "Cosmetic secondary packaging discrepancy without direct chemical stability or patient safety impact.",
    }


# -------------------------------------------------------------------------
# Node 1: parse_and_extract
# -------------------------------------------------------------------------
async def parse_and_extract(state: AgentState) -> Dict[str, Any]:
    """Extract fields from user text. In edit mode, perform shallow merge preserving untouched fields."""
    user_message = state.get("user_message", "")
    current_form = dict(state.get("current_form") or {})

    action = "log"
    extracted_fields: Dict[str, Any] = {}

    if _is_active_api_key(settings.GROQ_API_KEY):
        try:
            prompt_content = (
                f"Current Complaint Form State:\n{json.dumps(current_form, indent=2)}\n\n"
                f"User Message:\n{user_message}"
            )
            response = await llm.ainvoke([
                SystemMessage(content=INTENT_AND_EXTRACTION_PROMPT),
                HumanMessage(content=prompt_content),
            ])
            parsed = _extract_json_from_text(response.content)
            if parsed and isinstance(parsed, dict) and "action" in parsed:
                action = parsed.get("action", "log")
                raw_extracted = parsed.get("extracted_fields", {})
                if isinstance(raw_extracted, dict):
                    extracted_fields = raw_extracted
            else:
                fallback = _fallback_parse_and_extract(user_message, current_form)
                action = fallback["action"]
                extracted_fields = fallback["extracted_fields"]
        except Exception as err:
            print(f"LLM Invocation Error in parse_and_extract: {err}")
            traceback.print_exc()
            logger.warning(f"ChatGroq parsing failed, using fallback: {err}")
            fallback = _fallback_parse_and_extract(user_message, current_form)
            action = fallback["action"]
            extracted_fields = fallback["extracted_fields"]
    else:
        fallback = _fallback_parse_and_extract(user_message, current_form)
        action = fallback["action"]
        extracted_fields = fallback["extracted_fields"]

    sanitized_extracted = _sanitize_extracted_fields(extracted_fields, user_message, action=action)

    updated_form = dict(current_form)
    if action in ("log", "edit"):
        for key, val in sanitized_extracted.items():
            if val is not None and str(val).strip() != "":
                updated_form[key] = val

    return {
        "action": action,
        "extracted_fields": sanitized_extracted,
        "current_form": updated_form,
    }


# -------------------------------------------------------------------------
# Node 2: evaluate_risk
# -------------------------------------------------------------------------
async def evaluate_risk(state: AgentState) -> Dict[str, Any]:
    """Run risk analysis on the latest complaint details."""
    form = state.get("current_form") or {}
    defect_description = form.get("defect_description", "")
    product_name = form.get("product_name", "")
    product_strength = form.get("product_strength", "")
    affected_quantity = form.get("affected_quantity", "")
    complaint_category = form.get("complaint_category", "")

    if not defect_description and not product_name:
        existing_risk = state.get("current_risk") or {}
        if existing_risk.get("severity"):
            return {
                "risk_assessment": existing_risk,
                "current_risk": existing_risk,
            }
        default_risk = {
            "severity": "Minor",
            "suggested_next_action": "Log Incident for Quality Trend Analysis",
            "initial_risk_assessment": "Insufficient details to evaluate critical or major risk.",
        }
        return {
            "risk_assessment": default_risk,
            "current_risk": default_risk,
        }

    risk_result: Optional[Dict[str, Any]] = None

    if _is_active_api_key(settings.GROQ_API_KEY):
        try:
            prompt_content = (
                f"Product: {product_name}\n"
                f"Strength: {product_strength}\n"
                f"Complaint Category: {complaint_category}\n"
                f"Affected Quantity: {affected_quantity}\n"
                f"Defect Description: {defect_description}"
            )
            response = await llm.ainvoke([
                SystemMessage(content=RISK_ASSESSMENT_PROMPT),
                HumanMessage(content=prompt_content),
            ])
            parsed = _extract_json_from_text(response.content)
            if parsed and isinstance(parsed, dict) and "severity" in parsed:
                risk_result = parsed
        except Exception as err:
            logger.warning(f"ChatGroq risk evaluation failed, using fallback: {err}")
            risk_result = _fallback_evaluate_risk(defect_description, product_name, affected_quantity)
    else:
        risk_result = _fallback_evaluate_risk(defect_description, product_name, affected_quantity)

    if not risk_result:
        risk_result = _fallback_evaluate_risk(defect_description, product_name, affected_quantity)

    return {
        "risk_assessment": risk_result,
        "current_risk": risk_result,
    }


# -------------------------------------------------------------------------
# Node 3: calculate_completeness
# -------------------------------------------------------------------------
async def calculate_completeness(state: AgentState) -> Dict[str, Any]:
    """Compute 0–100 score based on essential intake fields."""
    form = state.get("current_form") or {}

    essential_fields = [
        bool(str(form.get("product_name") or "").strip()),
        bool(str(form.get("product_strength") or "").strip()),
        bool(str(form.get("batch_number") or "").strip()),
        bool(str(form.get("manufacturing_date") or "").strip()),
        bool(str(form.get("expiry_date") or "").strip()),
        bool(str(form.get("affected_quantity") or "").strip()),
        bool(str(form.get("defect_description") or "").strip()),
    ]

    filled_count = sum(1 for is_filled in essential_fields if is_filled)
    score = round((filled_count / 7.0) * 100)

    return {
        "completeness_score": score,
    }


# -------------------------------------------------------------------------
# Node 4: generate_reply
# -------------------------------------------------------------------------
async def generate_reply(state: AgentState) -> Dict[str, Any]:
    """Formulate a clear, professional confirmation message summarizing what was updated."""
    action = state.get("action", "log")
    extracted = state.get("extracted_fields") or {}
    form = state.get("current_form") or {}
    risk = state.get("current_risk") or {}
    score = state.get("completeness_score", 0)

    reply_text = ""

    if _is_active_api_key(settings.GROQ_API_KEY):
        try:
            context = (
                f"Action: {action}\n"
                f"Newly Extracted/Updated Fields: {json.dumps(extracted, indent=2)}\n"
                f"Current Form: {json.dumps(form, indent=2)}\n"
                f"Risk Evaluation: {json.dumps(risk, indent=2)}\n"
                f"Completeness Score: {score}%\n"
                f"User Message: {state.get('user_message', '')}"
            )
            response = await llm.ainvoke([
                SystemMessage(content=GENERATE_REPLY_PROMPT),
                HumanMessage(content=context),
            ])
            reply_text = response.content.strip()
        except Exception as err:
            logger.warning(f"ChatGroq reply generation failed, using fallback: {err}")

    if not reply_text:
        updated_keys = list(extracted.keys())
        updated_str = ", ".join(updated_keys) if updated_keys else "no new fields"
        severity = risk.get("severity", "Unspecified")

        if action == "edit":
            reply_text = (
                f"The complaint record has been successfully updated. "
                f"Updated fields: {updated_str}. "
                f"Risk severity assessed as {severity}. "
                f"Form completeness is currently {score}%."
            )
        elif action == "inquire":
            reply_text = (
                "Thank you for reaching out to the Pharmaceutical QMS team. "
                "You can log product quality complaints or update existing records by providing details "
                "such as batch number, defect description, product name, and affected quantity."
            )
        else:
            reply_text = (
                f"Complaint details recorded successfully. "
                f"Captured fields: {updated_str}. "
                f"Evaluated Risk Severity: {severity}. "
                f"Complaint completeness: {score}%."
            )

    return {
        "reply": reply_text,
    }


# -------------------------------------------------------------------------
# Compile the StateGraph
# -------------------------------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("parse_and_extract", parse_and_extract)
workflow.add_node("evaluate_risk", evaluate_risk)
workflow.add_node("calculate_completeness", calculate_completeness)
workflow.add_node("generate_reply", generate_reply)

workflow.set_entry_point("parse_and_extract")
workflow.add_edge("parse_and_extract", "evaluate_risk")
workflow.add_edge("evaluate_risk", "calculate_completeness")
workflow.add_edge("calculate_completeness", "generate_reply")
workflow.add_edge("generate_reply", END)

complaint_agent_app = workflow.compile()


# -------------------------------------------------------------------------
# Exported Helper Function
# -------------------------------------------------------------------------
async def process_user_query(
    message: str,
    current_form: Optional[Dict[str, Any]] = None,
    current_risk: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute the LangGraph QMS agent workflow for a user query."""
    initial_state: AgentState = {
        "user_message": message,
        "current_form": dict(current_form or {}),
        "current_risk": dict(current_risk or {}),
        "action": "log",
        "extracted_fields": {},
        "risk_assessment": dict(current_risk or {}),
        "completeness_score": 0,
        "reply": "",
    }

    final_state = await complaint_agent_app.ainvoke(initial_state)

    return {
        "reply": final_state.get("reply", ""),
        "updated_form": final_state.get("current_form", {}),
        "updated_risk": final_state.get("current_risk", {}),
        "completeness_score": final_state.get("completeness_score", 0),
        "action": final_state.get("action", "log"),
    }

