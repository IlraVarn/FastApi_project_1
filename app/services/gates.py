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
                    WorkflowRecordNotFoundError,
                    StaleGateError
                    )
from app.models import (
    Gate, 
    GateRequirement, 
    )
from app.schemas import GateSortBy, GateSortDirection
from app.enums import GateRequirementType, GateStatusType, GateType
from typing import Literal, Any
from sqlalchemy import asc, desc
from app.storage.gates import (
                    add_gate_record, 
                    get_active_gate_by_id,
                    list_active_gates,
                    count_active_gates_by_filter,
                    update_gate_patch,
                    get_gate_by_id_include_archived_for_update,
                    archive_gate_record,
                    get_active_gate_by_id_for_update
                            )

from app.storage.requirements import (add_gate_requirement_record,
                           list_requirements_by_gate_id,)
from app.storage.workflow_record import get_active_workflow_record_by_id




def create_gate_with_requirements_service(
    *,
    tenant: TenantContext,
    gate_type: GateType,
    workflow_record_id: int,
    requirement_types: list[GateRequirementType],
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    # The URL value is untrusted input for workflow_record_id
    # Before add_gate_record(), verify:

    db_workflow_record = get_active_workflow_record_by_id(
        workflow_record_id=workflow_record_id,
        organization_id=tenant.organization_id,
        session=session,
    )

    if db_workflow_record is None:
        raise WorkflowRecordNotFoundError()

    try:
        db_gate = add_gate_record(
            organization_id=tenant.organization_id,
            workflow_record_id=workflow_record_id,
            created_by_user_id=tenant.user_id,
            gate_type=gate_type,
            status=GateStatusType.DRAFT,
            session=session,
        )

        session.flush()

        gate_id = db_gate.id
        if gate_id is None:
            raise DataIntegrityError()


        db_requirements: list[GateRequirement] = []

        for requirement_type in requirement_types:
            db_requirement = add_gate_requirement_record(
                gate_id=gate_id,
                requirement_type=requirement_type.value,
                session=session,
            )

            db_requirements.append(db_requirement)

        session.commit()


    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_gate)

    for db_requirement in db_requirements:
        session.refresh(db_requirement)

    return db_gate, db_requirements


def get_gate_with_requirements_service(*,
    tenant: TenantContext,         
    workflow_record_id: int,                          
    gate_id: int,
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    db_gate = get_active_gate_by_id(
        gate_id=gate_id, 
        workflow_record_id=workflow_record_id,
        organization_id=tenant.organization_id,
        session=session)

    if db_gate is None:
        raise GateNotFoundError()

    db_requirements = list_requirements_by_gate_id(
        gate_id=gate_id, session=session)

    return db_gate, db_requirements


def list_active_gates_with_count_service(
        *,
        session: Session,      
        workflow_record_id: int,    
        gate_type: GateType | None,
        status: GateStatusType | None,
        sort_by: GateSortBy,
        sort_dir: GateSortDirection,
        offset: int,
        limit: int,
        tenant: TenantContext
) -> tuple[list[Gate], int]:

    #check for workflow_record to differentiate betw no wfr vs no gates
    db_workflow_record = get_active_workflow_record_by_id(
        workflow_record_id=workflow_record_id,
        organization_id=tenant.organization_id,
        session=session,
    )

    if db_workflow_record is None:
        raise WorkflowRecordNotFoundError()

    
    db_gates = list_active_gates(
        gate_type=gate_type,
        workflow_record_id=workflow_record_id,
        session=session,               
        status=status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
        organization_id=tenant.organization_id
       )

    db_gates_count = count_active_gates_by_filter(
            gate_type=gate_type,
            workflow_record_id=workflow_record_id,
            session=session,               
            status=status,
            organization_id=tenant.organization_id
           )

    return db_gates, db_gates_count


def update_gate_patch_service(
    *,
    gate_id: int,
    tenant: TenantContext,
    workflow_record_id: int,
    expected_row_version: int,
    update_data: dict[str, Any],
    session: Session,
) -> Gate:
    """Partially update an existing gate if the client edited the current version
      and commit the valid result.

    Only fields supplied by the client are changed.

    Raises:
        GateNotFoundError: The requested gate does not exist.
        InvalidGateUpdateError: The request is empty or supplies null.
        DataIntegrityError: Stored relationships or database writes fail.
    """
    #working with the dict
    #checks that do not require the Gate before acquiring the lock
    if not update_data:
        raise InvalidGateUpdateError()

    for value in update_data.values():
        if value is None:   
            raise InvalidGateUpdateError()

        
    db_gate = get_active_gate_by_id_for_update(
            gate_id=gate_id,
            workflow_record_id=workflow_record_id,
            organization_id=tenant.organization_id,
            session=session,
        )
    
    if db_gate is None:
        raise GateNotFoundError()
    
    if db_gate.row_version != expected_row_version:
        raise StaleGateError()

    try:
        update_gate_patch(
            db_gate=db_gate,
            update_data=update_data,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_gate)

    return db_gate


def archive_gate_service(
    *,
    gate_id: int,
    workflow_record_id: int,
    expected_row_version: int,
    tenant: TenantContext,
    session: Session,
) -> None:
    """Archive one gate.

    Repeated archive requests for the same existing gate succeed 
    without changing its original archive timestamp.

    Raises:
        GateNotFoundError: No gate exists with the requested ID 
        within the organization.
        DataIntegrityError: The database write fails.
    """
    try:

        db_gate = get_gate_by_id_include_archived_for_update(
            gate_id=gate_id,
            workflow_record_id=workflow_record_id,
            organization_id=tenant.organization_id,
            session=session,
        )

        if db_gate is None:
            raise GateNotFoundError()

        if db_gate.archived_at is not None:
            session.rollback()
            return 
        
        if db_gate.status == 'draft':
            raise GateArchiveNotAllowedError()
        
        if db_gate.row_version != expected_row_version:
            raise StaleGateError()

    
        archive_gate_record(
            db_gate=db_gate,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error
    
    except Exception:
        session.rollback()
        raise



