from sqlalchemy import Column, String, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database.session import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_hash = Column(String(200), unique=True, nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    verified = Column(Boolean, default=False)
    settled = Column(Boolean, default=False)
    user_identifier = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    settled_at = Column(DateTime)