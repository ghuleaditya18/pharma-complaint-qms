import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models import Complaint

client = TestClient(app)


def test_commit_persistence():
    print("--- 1. Initializing Database and Verifying Schema ---")
    init_db()
    db = SessionLocal()

    test_complaint_id = "CMP-PERSIST-TEST-001"

    # Cleanup any pre-existing record from past runs
    try:
        db.query(Complaint).filter_by(complaint_id=test_complaint_id).delete()
        db.commit()
    except Exception:
        db.rollback()

    print("\n--- 2. Testing API Commit (POST /api/complaints) ---")
    payload = {
        "complaint_id": test_complaint_id,
        "complaint_source": "Hospital Pharmacy",
        "customer_name": "Apollo Hospital & Medical Center",
        "product_name": "Amoxicillin Trihydrate",
        "product_strength": "500 mg Capsules",
        "batch_number": "BATCH-2026-PERSIST",
        "affected_quantity": "250 bottles",
        "manufacturing_date": "2026-01-15",
        "expiry_date": "2028-01-14",
        "originating_site_block": "Packaging Line 4",
        "impacted_npm": "Primary Packaging (HDPE Bottle)",
        "complaint_category": "Product Defect - Discoloration",
        "defect_description": "Observed capsule shell discoloration and defective inner foil seal.",
        "severity": "Major",
        "suggested_next_action": "Quarantine affected lot and initiate root cause investigation",
        "initial_risk_assessment": "Potential moisture ingress due to defective induction seal.",
        "completeness_score": 100,
        "status": "Logged"
    }

    response = client.post("/api/complaints", json=payload)
    print(f"API Response Status Code: {response.status_code}")
    assert response.status_code == 201, f"POST /api/complaints failed: {response.text}"

    resp_data = response.json()
    print(f"API Created Record ID: {resp_data.get('id')}, Code: {resp_data.get('complaint_id')}")
    assert resp_data.get("complaint_source") == "Hospital Pharmacy"
    assert resp_data.get("customer_name") == "Apollo Hospital & Medical Center"
    assert resp_data.get("product_name") == "Amoxicillin Trihydrate"

    print("\n--- 3. Querying Database directly via SQLAlchemy Session ---")
    retrieved = db.query(Complaint).filter_by(complaint_id=test_complaint_id).first()
    assert retrieved is not None, "Failed to retrieve committed complaint from DB!"

    print(f"Direct DB Query Record:")
    print(f"  id: {retrieved.id}")
    print(f"  complaint_id: {retrieved.complaint_id}")
    print(f"  complaint_source: {retrieved.complaint_source}")
    print(f"  customer_name: {retrieved.customer_name}")
    print(f"  product_name: {retrieved.product_name}")
    print(f"  product_strength: {retrieved.product_strength}")
    print(f"  batch_number: {retrieved.batch_number}")
    print(f"  originating_site_block: {retrieved.originating_site_block}")
    print(f"  impacted_npm: {retrieved.impacted_npm}")
    print(f"  severity: {retrieved.severity}")
    print(f"  suggested_next_action: {retrieved.suggested_next_action}")
    print(f"  initial_risk_assessment: {retrieved.initial_risk_assessment}")

    assert retrieved.complaint_source == "Hospital Pharmacy"
    assert retrieved.customer_name == "Apollo Hospital & Medical Center"
    assert retrieved.product_name == "Amoxicillin Trihydrate"
    assert retrieved.product_strength == "500 mg Capsules"
    assert retrieved.batch_number == "BATCH-2026-PERSIST"
    assert retrieved.originating_site_block == "Packaging Line 4"
    assert retrieved.impacted_npm == "Primary Packaging (HDPE Bottle)"
    assert retrieved.severity == "Major"
    assert retrieved.suggested_next_action == "Quarantine affected lot and initiate root cause investigation"

    # Cleanup test record
    db.delete(retrieved)
    db.commit()
    db.close()

    print("\n[SUCCESS] SQLite Schema & Commit Persistence Test Passed Cleanly with ZERO OperationalErrors!")


if __name__ == "__main__":
    test_commit_persistence()
