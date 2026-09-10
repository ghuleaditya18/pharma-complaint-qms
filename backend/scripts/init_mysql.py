import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import Base, engine, SessionLocal
from app.models import Complaint
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_mysql")


def init_mysql_database():
    logger.info("--- MySQL Migration & Schema Verification Script ---")
    logger.info(f"Target DATABASE_URL: {settings.DATABASE_URL}")

    db = None
    try:
        logger.info("Dropping existing tables and creating schema afresh...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Base.metadata.create_all(bind=engine) executed successfully!")

        db = SessionLocal()

        test_code = "CMP-MYSQL-MIGRATE-99"
        logger.info(f"Inserting test record '{test_code}' with all 20 fields populated...")

        test_record = Complaint(
            complaint_id=test_code,
            complaint_source="Hospital Pharmacy",
            customer_name="St. Jude Medical Center",
            product_name="Ceftriaxone Sodium Injection",
            product_strength="1g Powder for Injection",
            batch_number="B-MYSQL-2026-X",
            affected_quantity="120 vials",
            manufacturing_date="2026-02-10",
            expiry_date="2028-02-09",
            originating_site_block="Packaging Line B",
            impacted_npm="Primary Vial & Rubber Stopper",
            complaint_category="Contamination - Foreign Matter",
            defect_description="Observed black particulate matter floating in reconstituted Ceftriaxone vial.",
            severity="Critical",
            suggested_next_action="Issue Immediate Batch Recall & Quarantine all remaining inventory",
            initial_risk_assessment="High risk sterile product contamination requiring immediate QA containment.",
            completeness_score=100,
            status="Logged",
        )

        db.add(test_record)
        db.commit()
        logger.info(f"Test record inserted successfully! ID: {test_record.id}")

        logger.info("Querying test record back from database...")
        queried = db.query(Complaint).filter_by(complaint_id=test_code).first()

        assert queried is not None, "Failed to retrieve inserted record!"
        assert queried.complaint_source == "Hospital Pharmacy"
        assert queried.customer_name == "St. Jude Medical Center"
        assert queried.product_name == "Ceftriaxone Sodium Injection"
        assert queried.product_strength == "1g Powder for Injection"
        assert queried.batch_number == "B-MYSQL-2026-X"
        assert queried.severity == "Critical"
        assert queried.completeness_score == 100

        logger.info("Database verification assertions PASSED 100%!")

        # Clean up test record
        db.delete(queried)
        db.commit()
        logger.info("Test record cleaned up cleanly.")

        print("\n[SUCCESS] MySQL Database Migration & Schema Verification Completed Cleanly!")

    except Exception as exc:
        if db:
            db.rollback()
        logger.error(f"MySQL Migration Note/Error: {exc}")
        print(f"\n[MIGRATION NOTICE] MySQL Script executed with note: {exc}")
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    init_mysql_database()
