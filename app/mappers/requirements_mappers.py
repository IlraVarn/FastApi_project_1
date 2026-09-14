from app.models import (
    Gate, 
    GateRequirement,
    Organization,
    )

from app.schemas import (
    GatePublic,
    GateWithRequirementsPublic,
    OrganizationPublic,
    GateRequirementPublic
)

from app.enums import (
    GateStatusType, 
    GateRequirementType,
    GateType,
    EvidenceUploadStatusType
)
from sqlmodel import col
from app.errors import DataIntegrityError


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
    if db_requirement.id is None:
        raise DataIntegrityError()

    return GateRequirementPublic(
        id=db_requirement.id,
        requirement_type=GateRequirementType(db_requirement.requirement_type),
        created_at=db_requirement.created_at
    )

