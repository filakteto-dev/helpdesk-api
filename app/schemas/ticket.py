from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TicketStatus
    owner_id: int
    created_at: datetime


class TicketStatusUpdate(BaseModel):
    status: TicketStatus