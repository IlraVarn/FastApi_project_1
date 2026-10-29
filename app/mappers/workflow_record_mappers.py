
from app.models import (
    WorkflowRecord
    )

from app.schemas import (
        WorkflowRecordPublic
)

from sqlmodel import col
from app.errors import DataIntegrityError


def to_workflow_record_public(db_workflow_record: WorkflowRecord
                                )-> WorkflowRecordPublic:

    if db_workflow_record.id is None:
        raise DataIntegrityError()

    return WorkflowRecordPublic(
        id=db_workflow_record.id,
        organization_id=db_workflow_record.organization_id,
        created_by_user_id=db_workflow_record.created_by_user_id,
        name=db_workflow_record.name,
        created_at=db_workflow_record.created_at,
        updated_at=db_workflow_record.updated_at,
        archived_at=db_workflow_record.archived_at,
    )



