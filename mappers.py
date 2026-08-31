from models import (Gate, 
                    GateStatus,
                    GateType,
                    GatePublic,
                    GateWithRequirementsPublic,
                    GateRequirementType,
                    GateRequirementPublic,
                    GateRequirement,
                    Organization,
                    OrganizationPublic)

from sqlmodel import col



def to_gate_public(db_gate: Gate)-> GatePublic:
    assert db_gate.id is not None

    return GatePublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatus(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference
    )


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
    
    assert db_gate.id is not None

    public_requirements = []

    for db_requirement in db_requirements:
        public_requirement = to_requirement_public(db_requirement)
        public_requirements.append(public_requirement)
    
    return GateWithRequirementsPublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatus(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference,
        requirements=public_requirements
    )


def to_requirement_public_list(
        db_requirements: list[GateRequirement]
        )-> list[GateRequirementPublic]:
    
    public_requirements=[]
    for db_requirement in db_requirements:
        public_requirement= to_requirement_public(db_requirement)
        public_requirements.append(public_requirement)

    return public_requirements


def to_requirement_public(
        db_requirement: GateRequirement
    )-> GateRequirementPublic:
    
    assert db_requirement.id is not None

    return GateRequirementPublic(
        id=db_requirement.id,
        requirement_type=GateRequirementType(db_requirement.requirement_type),
        created_at=db_requirement.created_at
    )


def to_organization_public(db_organization: Organization) -> OrganizationPublic:
    assert db_organization.id is not None
    
    return OrganizationPublic(
        id= db_organization.id,
        name=db_organization.name,
    )




