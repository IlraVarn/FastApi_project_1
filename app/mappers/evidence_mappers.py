
from app.errors import DataIntegrityError
from app.infrastructure.s3 import PresignedUpload

from app.models import (
    Evidence,
    EvidenceVersion,
)
from app.schemas import (
    EvidencePublic,
    EvidenceVersionPublic,
    EvidenceCreatedPublic,
    EvidenceUploadUrlPublic
)
from app.enums import EvidenceUploadStatusType

def to_evidence_public(
    db_evidence: Evidence,
) -> EvidencePublic:
    
    if db_evidence.id is None:
        raise DataIntegrityError()

    return EvidencePublic(
        id=db_evidence.id,
        name=db_evidence.name,
        organization_id=db_evidence.organization_id
    )


def to_evidence_version_public(
    db_version: EvidenceVersion,
) -> EvidenceVersionPublic:
    
    if db_version.id is None:
        raise DataIntegrityError()

    return EvidenceVersionPublic(
        id=db_version.id,
        evidence_id=db_version.evidence_id,
        version_number=db_version.version_number,
        original_filename=db_version.original_filename,
        content_type=db_version.content_type,
        size_bytes=db_version.size_bytes,
        upload_status=EvidenceUploadStatusType(db_version.upload_status),
        created_by_user_id=db_version.created_by_user_id,
        created_at=db_version.created_at,
    )


def to_evidence_created_public(
    db_evidence: Evidence,
    db_version: EvidenceVersion,
) -> EvidenceCreatedPublic:
    
    return EvidenceCreatedPublic(
        evidence=to_evidence_public(
            db_evidence
        ),
        version=to_evidence_version_public(
            db_version
        ),
    )



def to_evidence_upload_url_public(
    upload: PresignedUpload,
) -> EvidenceUploadUrlPublic:

    return EvidenceUploadUrlPublic(
        method="PUT",
        upload_url=upload.url,
        headers=upload.headers,
        expires_in_seconds=(
            upload.expires_in_seconds
        ),
    )



