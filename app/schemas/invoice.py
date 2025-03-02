from pydantic import BaseModel, UUID4
from datetime import date
from typing import Optional

class InvoiceBase(BaseModel):
    file_name: str
    issue_date: date

class InvoiceCreate(InvoiceBase):
    user_id: UUID4

class InvoiceUpdate(BaseModel):
    file_name: Optional[str]
    issue_date: Optional[date]

class InvoiceOut(InvoiceBase):
    id: UUID4
    user_id: UUID4

    class Config:
        orm_mode = True