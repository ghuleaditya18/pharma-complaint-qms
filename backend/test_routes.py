import io
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.models import Complaint

client = TestClient(app)


def test_api_routes():
    print("--- 1. Testing GET /health ---")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    data = resp.json()
    assert data.get("status") == "ok"
    print(f"[PASS] Health check: {data}")

    print("\n--- 2. Testing POST /api/chat ---")
    chat_payload = {
        "message": "Received complaint for batch B90123 of Paracetamol 500mg, 50 strips affected with leaking blister packaging.",
        "current_form": {},
        "current_risk": {}
    }
    resp = client.post("/api/chat", json=chat_payload)
    assert resp.status_code == 200, f"Chat failed: {resp.text}"
    chat_data = resp.json()
    print("Chat response:")
    print(f"  Reply: {chat_data['reply'][:100]}...")
    print(f"  Form: {chat_data['updated_form']}")
    print(f"  Risk: {chat_data['updated_risk']}")
    print(f"  Score: {chat_data['completeness_score']}%")
    assert "updated_form" in chat_data
    assert "updated_risk" in chat_data
    assert chat_data["completeness_score"] > 0
    print("[PASS] Chat endpoint passed.")

    print("\n--- 3. Testing POST /api/upload (TXT file) ---")
    file_content = (
        "Dear Quality Team,\n"
        "We detected contaminated sterile vials from batch VIAL-7761. "
        "Product: Ceftriaxone 1g, affected quantity: 120 vials. Foreign black particles were observed."
    )
    files = {"file": ("complaint_letter.txt", io.BytesIO(file_content.encode("utf-8")), "text/plain")}
    resp = client.post("/api/upload", files=files)
    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    upload_data = resp.json()
    print("Upload response:")
    print(f"  Extracted Form: {upload_data['updated_form']}")
    print(f"  Assessed Severity: {upload_data['updated_risk'].get('severity')}")
    assert "updated_form" in upload_data
    print("[PASS] Upload endpoint passed.")

    print("\n--- 4. Testing POST /api/complaints ---")
    complaint_payload = {
        "complaint_id": "CMP-TEST-9901",
        "complaint_source": "Pharmacy",
        "customer_name": "City Care Pharmacy",
        "product_name": "Ibuprofen 400mg",
        "product_strength": "400mg USP",
        "batch_number": "IBU-2026-X",
        "affected_quantity": "50 strips",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-01-31",
        "originating_site_block": "Packaging",
        "impacted_npm": "Blister Foil",
        "complaint_category": "Packaging",
        "defect_description": "Foil missing on 5 blisters",
        "severity": "Major",
        "suggested_next_action": "Quarantine stock & audit sealing parameters",
        "initial_risk_assessment": "Secondary barrier compromised",
        "completeness_score": 90,
        "status": "Logged"
    }
    resp = client.post("/api/complaints", json=complaint_payload)
    assert resp.status_code == 201, f"Create complaint failed: {resp.text}"
    created_comp = resp.json()
    print(f"Created complaint: ID={created_comp['id']}, Code={created_comp['complaint_id']}")
    assert created_comp["complaint_id"] == "CMP-TEST-9901"
    assert created_comp["product_name"] == "Ibuprofen 400mg"
    print("[PASS] POST /api/complaints passed.")

    print("\n--- 5. Testing GET /api/complaints ---")
    resp = client.get("/api/complaints")
    assert resp.status_code == 200, f"List complaints failed: {resp.text}"
    complaints_list = resp.json()
    print(f"Retrieved {len(complaints_list)} complaints from DB.")
    assert len(complaints_list) >= 1
    assert any(c["complaint_id"] == "CMP-TEST-9901" for c in complaints_list)
    print("[PASS] GET /api/complaints passed.")

    print("\n--- 6. Testing GET /api/complaints/{id} ---")
    comp_id = created_comp["id"]
    resp = client.get(f"/api/complaints/{comp_id}")
    assert resp.status_code == 200, f"Get complaint by id failed: {resp.text}"
    assert resp.json()["complaint_id"] == "CMP-TEST-9901"

    # Also test fetch by complaint code string
    resp_code = client.get(f"/api/complaints/CMP-TEST-9901")
    assert resp_code.status_code == 200
    assert resp_code.json()["id"] == comp_id

    # 404 test
    resp_404 = client.get("/api/complaints/NON_EXISTENT_ID_99999")
    assert resp_404.status_code == 404
    print("[PASS] GET /api/complaints/{id} passed.")

    # Cleanup test data
    db = SessionLocal()
    try:
        db.query(Complaint).filter_by(complaint_id="CMP-TEST-9901").delete()
        db.commit()
    finally:
        db.close()

    print("\n[ALL FASTAPI ROUTE TESTS PASSED SUCCESSFULLY!]")


if __name__ == "__main__":
    test_api_routes()
