
from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from app.tenancy.context import TenantContext
from app.errors import ( GateNotFoundError, 
                    DataIntegrityError, 
                    ConflictError,
                    InvalidGateStateTransitionError,
                    InvalidGateUpdateError,
                    GateArchiveNotAllowedError,
                    )
from app.models import (
    WorkflowRecord
    )
from typing import Literal, Any
from sqlalchemy import asc, desc
from app.storage.gates import (
                    add_gate_record, 
                    get_active_gate_by_id,
                    list_active_gates,
                    count_active_gates_by_filter,
                    update_gate_patch,
                    get_gate_by_id_include_archived,
                    archive_gate_record
                            )
from app.storage.workflow_record import add_workflow_record



def create_workflow_record_service(
    *,
    tenant: TenantContext,
    name: str,
    session: Session,
) -> WorkflowRecord:

    try:
        db_workflow_record = add_workflow_record(
            organization_id=tenant.organization_id,
            created_by_user_id=tenant.user_id,
            name=name,
            session=session,
        )
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_workflow_record)


    return db_workflow_record

