from sqlalchemy import Column, Integer, String, Boolean, UUID, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

class Invoice(Base):
    __tablename__="invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    issue_date = Column(Date, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="invoices")