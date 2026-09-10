from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String(50), unique=True, index=True, nullable=False)

    # Section 1: Origin & Customer Details
    complaint_source = Column(String(100), nullable=True)
    customer_name = Column(String(255), nullable=True)

    # Section 2: Product & Batch Identification
    product_name = Column(String(255), nullable=True)
    product_strength = Column(String(100), nullable=True)
    batch_number = Column(String(100), nullable=True)
    affected_quantity = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)

    # Section 3: Facility & Material Impact
    originating_site_block = Column(String(150), nullable=True)
    impacted_npm = Column(String(150), nullable=True)

    # Section 4: Defect Analysis
    complaint_category = Column(String(150), nullable=True)
    defect_description = Column(Text, nullable=True)

    # AI Copilot Risk Assessment
    severity = Column(String(50), nullable=True)  # 'Critical', 'Major', 'Minor'
    suggested_next_action = Column(Text, nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)

    completeness_score = Column(Integer, default=0, nullable=True)
    status = Column(String(50), default="Logged", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Complaint id={self.id} complaint_id={self.complaint_id} status={self.status}>"

