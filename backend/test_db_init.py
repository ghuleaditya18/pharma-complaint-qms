import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import inspect
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Complaint
from app.schemas import ComplaintResponse, ComplaintFields, RiskAssessment, ChatRequest, ChatResponse


def verify_tables():
    print(f"Testing database URL: {settings.DATABASE_URL}")
    print(f"Groq API Key placeholder loaded: {bool(settings.GROQ_API_KEY)}")

    # 1. Drop existing tables and recreate
    print("\n--- Re-initializing tables with Base.metadata.drop_all & create_all ---")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 2. Inspect created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    assert "complaints" in tables, "Table 'complaints' was not created!"

    columns = [col["name"] for col in inspector.get_columns("complaints")]
    print(f"Columns in 'complaints' table ({len(columns)}): {columns}")

    expected_cols = [
        "id", "complaint_id", "complaint_source", "customer_name",
        "product_name", "product_strength", "batch_number", "affected_quantity",
        "manufacturing_date", "expiry_date", "originating_site_block",
        "impacted_npm", "complaint_category", "defect_description",
        "severity", "suggested_next_action", "initial_risk_assessment",
        "completeness_score", "status", "created_at"
    ]
    for col in expected_cols:
        assert col in columns, f"Missing expected column: {col}"

    # 3. Test insertion and retrieval
    print("\n--- Testing insert & query with SQLAlchemy session ---")
    db = SessionLocal()
    try:
        sample_complaint = Complaint(
            complaint_id="CMP-2026-001",
            complaint_source="Pharmacy",
            customer_name="Apollo Pharmacy",
            product_name="Paracetamol 500mg",
            product_strength="500 mg",
            batch_number="B240901",
            affected_quantity="100 strips",
            manufacturing_date="2026-01-15",
            expiry_date="2028-01-14",
            originating_site_block="Packaging",
            impacted_npm="Blister Foil",
            complaint_category="Product Defect - Discoloration",
            defect_description="Blister foil unsealed on multiple strips.",
            severity="Major",
            suggested_next_action="Route to QA Investigation & Issue Replacement",
            initial_risk_assessment="Potential moisture ingress or primary packaging seal failure leading to capsule discoloration.",
            completeness_score=95,
            status="Logged",
            created_at=datetime.utcnow()
        )
        db.add(sample_complaint)
        db.commit()
        db.refresh(sample_complaint)
        print(f"Inserted complaint: {sample_complaint}")

        retrieved = db.query(Complaint).filter_by(complaint_id="CMP-2026-001").first()
        assert retrieved is not None, "Failed to retrieve complaint from DB!"
        assert retrieved.product_name == "Paracetamol 500mg"
        print(f"Successfully retrieved complaint: ID={retrieved.id}, Code={retrieved.complaint_id}")

        # 4. Validate Pydantic v2 serialization
        print("\n--- Validating Pydantic v2 schemas ---")
        pydantic_obj = ComplaintResponse.model_validate(retrieved)
        print(f"Validated ComplaintResponse: {pydantic_obj.complaint_id}, Next Action: {pydantic_obj.suggested_next_action}")
        assert pydantic_obj.completeness_score == 95

        chat_req = ChatRequest(message="We found broken seal on batch B240901")
        assert chat_req.message == "We found broken seal on batch B240901"

        chat_resp = ChatResponse(
            reply="Acknowledged. Please provide expiry date.",
            updated_form={"product_name": "Paracetamol 500mg"},
            updated_risk={"severity": "Major"},
            completeness_score=60
        )
        assert chat_resp.completeness_score == 60
        print("Pydantic v2 schemas validated successfully.")

    finally:
        # Clean up test row
        db.query(Complaint).filter_by(complaint_id="CMP-2026-001").delete()
        db.commit()
        db.close()

    print("\n[SUCCESS] All tables and schemas initialized and verified cleanly!")


if __name__ == "__main__":
    verify_tables()

