

from app.models import (
    Gate, 
    GateRequirement,
    Organization,
    GateSubmission
    )

from app.schemas import (
    GatePublic,
    GateWithRequirementsPublic,
    OrganizationPublic,
    GateRequirementPublic,
    GateListPublicWithCount,
    GateSubmissionPublic,
)

from app.enums import (
    GateStatusType, 
    GateRequirementType,
    GateType,
    EvidenceUploadStatusType)

from sqlmodel import col
from app.mappers.requirements_mappers import to_requirement_public
from app.errors import DataIntegrityError


def to_gate_submission_public(
        db_gate_submission: GateSubmission
        )-> GateSubmissionPublic:

    if db_gate_submission.id is None:
        raise DataIntegrityError()

    return GateSubmissionPublic(
        id=db_gate_submission.id,
        gate_id=db_gate_submission.gate_id,
        submission_numer=db_gate_submission.submission_number,
        submitted_by_user_id=db_gate_submission.submitted_by_user_id,
        submitted_at=db_gate_submission.submitted_at
    )
    

