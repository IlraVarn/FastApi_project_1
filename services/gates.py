from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from tenancy.context import TenantContext
from errors import ( GateNotFoundError, 
                    DataIntegrityError, 
                    ConflictError,
                    InvalidGateStateTransitionError,
                    InvalidGateUpdateError,
                    GateArchiveNotAllowedError,
                    )
from models import (Gate, 
                    GateType,
                    GateRequirement, 
                    GateSortDirection, 
                    GateSortBy, 
                    GateStatus,
                    GateRequirementType
                    )
from typing import Literal, Any
from sqlalchemy import asc, desc
from storage.gates import (
                    add_gate_record, 
                    get_active_gate_by_id,
                    list_active_gates,
                    count_active_gates_by_filter,
                    update_gate_patch,
                    get_gate_by_id_include_archived,
                    archive_gate_record
                            )

from storage.requirements import (add_gate_requirement_record,
                           list_requirements_by_gate_id,)




def create_gate_with_requirements_service(
    *,
    tenant: TenantContext,
    gate_type: GateType,
    requirement_types: list[GateRequirementType],
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    try:
        db_gate = add_gate_record(
            organization_id=tenant.organization_id,
            gate_type=gate_type,
            status=GateStatus.DRAFT,
            session=session,
        )

        session.flush()

        gate_id = db_gate.id

        if gate_id is None:
            session.rollback()
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
    gate_id: int,
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    db_gate = get_active_gate_by_id(
        gate_id=gate_id, 
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
        gate_type: GateType | None,
        status: GateStatus | None,
        sort_by: GateSortBy,
        sort_dir: GateSortDirection,
        offset: int,
        limit: int,
        tenant: TenantContext
) -> tuple[list[Gate], int]:
    
    db_gates = list_active_gates(
        gate_type=gate_type,
        session=session,               
        status=status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
        organization_id=tenant.organization_id
       )

    gate_count_with_filter = count_active_gates_by_filter(
            gate_type=gate_type,
            session=session,               
            status=status,
            organization_id=tenant.organization_id
           )

    return db_gates, gate_count_with_filter


def update_gate_patch_service(
    *,
    gate_id: int,
    tenant: TenantContext,
    update_data: dict[str, Any],
    session: Session,
) -> Gate:
    """Partially update an existing gate and commit the valid result.

    Only fields supplied by the client are changed.

    Raises:
        GateNotFoundError: The requested gate does not exist.
        InvalidGateUpdateError: The request is empty or supplies null.
        DataIntegrityError: Stored relationships or database writes fail.
    """

    db_gate = get_active_gate_by_id(
        gate_id=gate_id, 
        organization_id=tenant.organization_id,
        session=session)

    if db_gate is None:
        raise GateNotFoundError()

    #working with the dict
    if not update_data:
        raise InvalidGateUpdateError()

    for value in update_data.values():
        if value is None:   
            raise InvalidGateUpdateError()

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

    db_gate = get_gate_by_id_include_archived(
        gate_id=gate_id,
        organization_id=tenant.organization_id,
        session=session,
    )

    if db_gate is None:
        raise GateNotFoundError()

    if db_gate.archived_at is not None:
        return 
    
    if db_gate.status == 'draft':
        raise GateArchiveNotAllowedError()
    
    try:
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



