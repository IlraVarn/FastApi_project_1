

from app.models import (
    Gate, 
    GateRequirement,
    )

from app.schemas import (
    GatePublic,
    GateWithRequirementsPublic,
    GateListPublicWithCount

)

from app.enums import (
    GateStatusType, 
    GateType,
    )

from sqlmodel import col
from app.mappers.requirements_mappers import to_requirement_public
from app.errors import DataIntegrityError


def to_gate_public(
        db_gate: Gate
        )-> GatePublic:

    if db_gate.id is None:
        raise DataIntegrityError()

    return GatePublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        created_by_user_id=db_gate.created_by_user_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatusType(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference,
        row_version=db_gate.row_version)
    


def to_gate_public_list(db_gates: list[Gate]
                        )-> list[GatePublic]:
    public_gates = []

    for db_gate in db_gates:
        public_gate = to_gate_public(db_gate)
        public_gates.append(public_gate)

    return public_gates



def to_gate_with_requirements_public(
        db_gate: Gate,
        db_requirements: list[GateRequirement]
        ) -> GateWithRequirementsPublic:
    
    if db_gate.id is None:
        raise DataIntegrityError()

    public_requirements = []

    for db_requirement in db_requirements:
        public_requirement = to_requirement_public(db_requirement)
        public_requirements.append(public_requirement)
    
    return GateWithRequirementsPublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        created_by_user_id=db_gate.created_by_user_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatusType(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference,
        row_version=db_gate.row_version,
        requirements=public_requirements
    )



def to_gate_list_public_with_count(
    db_gates: list[Gate],
    count: int,
) -> GateListPublicWithCount:

    public_gates: list[GatePublic] = []

    for db_gate in db_gates:
        public_gate = to_gate_public(db_gate)
        public_gates.append(public_gate)

    return GateListPublicWithCount(
        data=public_gates,
        count=count,
    )
