from __future__ import annotations
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC

class WorkflowRecordCreateRequest(SQLModel):
    reference: str = Field(default=None, min_length=1)


class WorkflowRecordPublic(SQLModel):
    id: int
    organization_id: int
    created_by_user_id: int
    reference: str
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None