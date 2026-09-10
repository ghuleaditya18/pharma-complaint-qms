import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.agent.state import AgentState
from app.agent.prompts import INTENT_AND_EXTRACTION_PROMPT, RISK_ASSESSMENT_PROMPT, GENERATE_REPLY_PROMPT
from app.agent.graph import complaint_agent_app, process_user_query, calculate_completeness, _extract_json_from_text, _sanitize_extracted_fields
from app.schemas import ComplaintFields, ComplaintCreate, ComplaintResponse


async def test_agent():
    print("--- 1. Testing Prompts and AgentState ---")
    assert "INTENT" in INTENT_AND_EXTRACTION_PROMPT
    assert "Critical" in RISK_ASSESSMENT_PROMPT
    assert "Major" in RISK_ASSESSMENT_PROMPT
    assert "Minor" in RISK_ASSESSMENT_PROMPT
    assert "Empathetic" in GENERATE_REPLY_PROMPT or "QMS" in GENERATE_REPLY_PROMPT
    assert "CRITICAL DATE RULE" in INTENT_AND_EXTRACTION_PROMPT
    assert "CRITICAL DEDUCTION RULES" in INTENT_AND_EXTRACTION_PROMPT
    print("[PASS] Prompts and State verified.")

    print("\n--- 2. Testing JSON Parsing with Fences ---")
    fenced_json = """```json
{
  "action": "log",
  "extracted_fields": {
    "product_name": "Paracetamol"
  }
}
```"""
    parsed = _extract_json_from_text(fenced_json)
    assert parsed is not None
    assert parsed.get("action") == "log"
    assert parsed.get("extracted_fields", {}).get("product_name") == "Paracetamol"
    print("[PASS] Markdown fence JSON extraction verified.")

    print("\n--- 3. Testing Date Sanity & Auto-Swap Inverted Dates ---")
    inverted_fields = {
        "manufacturing_date": "2027-12-31",
        "expiry_date": "2025-01-01",
    }
    sanitized_dates = _sanitize_extracted_fields(inverted_fields)
    print(f"Inverted dates before: {inverted_fields} -> after: {sanitized_dates}")
    assert sanitized_dates["manufacturing_date"] == "2025-01-01"
    assert sanitized_dates["expiry_date"] == "2027-12-31"

    # Test single manufacturing date strict assignment
    single_mfg_text = "Manufacturing date is 2025-05-10 for lot B-10"
    mfg_result = await process_user_query(message=single_mfg_text)
    print(f"Single mfg result: {mfg_result['updated_form']}")
    assert mfg_result["updated_form"].get("manufacturing_date") == "2025-05-10"
    assert mfg_result["updated_form"].get("expiry_date") is None or mfg_result["updated_form"].get("expiry_date") != "2025-05-10"
    print("[PASS] Date sanity, inversion swapping, and strict mfg date assignment verified.")

    print("\n--- 4. Testing Customer/Complainant Mapping & Dual Keys ---")
    comp_msg = "Complaint reported by Dr. Sharma at Apollo Hospital for batch B240901."
    comp_res = await process_user_query(message=comp_msg)
    form = comp_res["updated_form"]
    print(f"Complainant extracted form: {form}")
    assert "customer_name" in form
    assert "Dr. Sharma" in form["customer_name"]
    print("[PASS] Customer name extraction & dual-key normalization verified.")

    print("\n--- 5. Testing Noise & Table Header Sanitization ---")
    noisy_fields = {
        "product_name": "Amoxicillin",
        "batch_number": "Field",
        "customer_name": "Not specified",
        "complaint_category": "N/A",
        "defect_description": "Extracted Information",
    }
    sanitized_noise = _sanitize_extracted_fields(noisy_fields)
    print(f"Sanitized noise fields: {sanitized_noise}")
    assert sanitized_noise.get("batch_number") is None
    assert sanitized_noise.get("customer_name") is None
    assert sanitized_noise.get("complaint_category") is None
    assert sanitized_noise.get("defect_description") != "Extracted Information"
    assert sanitized_noise.get("product_name") == "Amoxicillin"
    print("[PASS] Table header & noise placeholder sanitization verified.")

    print("\n--- 6. Testing Pydantic Schema Coercion ---")
    cf = ComplaintFields(
        product_name="Ibuprofen",
        batch_number="N/A",
        customer_name="Not specified",
        defect_description="None",
    )
    print(f"Pydantic coerced fields: product_name='{cf.product_name}', batch_number='{cf.batch_number}', customer_name='{cf.customer_name}'")
    assert cf.product_name == "Ibuprofen"
    assert cf.batch_number == ""
    assert cf.customer_name == ""
    assert cf.defect_description == ""
    print("[PASS] Pydantic schema noise coercion verified.")

    print("\n--- 7. Testing Completeness Calculation ---")
    partial_form = {
        "product_name": "Amoxicillin",
        "product_strength": "250 mg",
        "batch_number": "AMX-101",
    }
    comp_state: AgentState = {"current_form": partial_form}
    result = await calculate_completeness(comp_state)
    expected_score = round((3 / 7.0) * 100)  # 43%
    print(f"Partial form score: {result['completeness_score']}% (expected ~{expected_score}%)")
    assert result["completeness_score"] == expected_score

    full_form = {
        "complaint_source": "Pharmacy",
        "customer_name": "Apollo Pharmacy",
        "product_name": "Amoxicillin",
        "product_strength": "250 mg",
        "batch_number": "AMX-101",
        "affected_quantity": "500 bottles",
        "manufacturing_date": "2025-10-01",
        "expiry_date": "2027-09-30",
        "originating_site_block": "Packaging Block B",
        "impacted_npm": "Primary Packaging (Bottle)",
        "complaint_category": "Packaging Defect",
        "defect_description": "Damaged blister foil seal and discolored capsules",
    }
    comp_state_full: AgentState = {"current_form": full_form}
    result_full = await calculate_completeness(comp_state_full)
    print(f"Full form score: {result_full['completeness_score']}%")
    assert result_full["completeness_score"] == 100
    print("[PASS] Completeness calculation verified.")

    print("\n--- 8. Testing process_user_query (Log Complaint) ---")
    log_msg = "Logging issue for batch B240901, 100 strips of 500 mg Paracetamol. Packaging is broken and unsealed."
    res1 = await process_user_query(message=log_msg)
    print("Log response:")
    print(f"  Reply: {res1['reply'][:120]}...")
    print(f"  Updated form: {res1['updated_form']}")
    print(f"  Updated risk severity: {res1['updated_risk'].get('severity')}")
    print(f"  Completeness score: {res1['completeness_score']}%")
    assert res1["completeness_score"] > 0
    assert "B240901" in str(res1["updated_form"])

    print("\n--- 9. Testing process_user_query (Edit Mode - Shallow Merge) ---")
    edit_msg = "Change batch number to B999999 and affected quantity to 250 strips."
    res2 = await process_user_query(
        message=edit_msg,
        current_form=res1["updated_form"],
        current_risk=res1["updated_risk"]
    )
    print("Edit response:")
    print(f"  Reply: {res2['reply'][:120]}...")
    print(f"  Updated form: {res2['updated_form']}")
    print(f"  Updated risk severity: {res2['updated_risk'].get('severity')}")
    assert res2["updated_form"].get("batch_number") == "B999999"
    assert "250 strips" in str(res2["updated_form"].get("affected_quantity"))
    if "defect_description" in res1["updated_form"]:
        assert res2["updated_form"].get("defect_description") == res1["updated_form"]["defect_description"]
    print("[PASS] Shallow merge in edit mode preserved untouched fields.")

    print("\n--- 10. Testing Critical Defect Risk Evaluation ---")
    critical_msg = "Discovered foreign metal particles and bacterial contamination in vial batch V-881."
    res3 = await process_user_query(message=critical_msg)
    print(f"Critical test severity: {res3['updated_risk'].get('severity')}")
    assert res3["updated_risk"].get("severity") == "Critical"
    print(f"Suggested next action: {res3['updated_risk'].get('suggested_next_action')}")
    print("[PASS] GMP Critical severity correctly triggered.")

    print("\n--- 11. Testing Natural Language Entity Extraction & Defect Synthesis ---")
    nl_msg = "Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch number AMX240602. Manufacturing date March 2026. Expiry date February 2028. Please log this complaint"
    res4 = await process_user_query(message=nl_msg)
    form4 = res4["updated_form"]
    print(f"Natural language extracted form: {form4}")
    assert form4.get("customer_name") == "Apollo Pharmacy"
    assert form4.get("complaint_source") == "Pharmacy"
    assert form4.get("product_name") == "Amoxicillin Capsules"
    assert form4.get("product_strength") == "500 mg"
    assert form4.get("batch_number") == "AMX240602"
    assert form4.get("manufacturing_date") == "March 2026"
    assert form4.get("expiry_date") == "February 2028"
    assert "Please log" not in form4.get("defect_description", "")
    print("[PASS] Natural language extraction & conversational directive stripping verified.")

    print("\n[ALL AGENT TESTS PASSED CLEANLY!]")


if __name__ == "__main__":
    asyncio.run(test_agent())

