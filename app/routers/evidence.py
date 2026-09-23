from app.tenancy.context import TenantContext
from app.tenancy.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
                     Path,
                     Header
    )
from sqlmodel import Session

from app.db import get_session
from app.infrastructure.s3 import get_s3_object_store

from app.schemas import (
   EvidenceCreatedPublic,
   EvidenceCreate,
   EvidenceVersionCreate,
   EvidenceVersionPublic,
   EvidenceUploadUrlPublic
    )

from app.services.evidence import (
    create_evidence_service,
    create_evidence_version_service,
    create_evidence_version_upload_url_service,
    complete_evidence_version_upload_service,
    )

from app.infrastructure.s3 import S3ObjectStore

from app.errors import (
    EvidenceNotFoundError, 
    DataIntegrityError,
    IdempotencyConflictError,
    EvidenceStorageError,
    EvidenceUploadNotReadyError,
    EvidenceUploadVerificationError,
    EvidenceVersionNotFoundError,
    EvidenceVersionNotPendingError,

    )

from app.mappers.evidence_mappers import (
    to_evidence_public,
    to_evidence_version_public,
    to_evidence_upload_url_public
)
"""
User
  │
  ▼
Membership
  ▲
  │
Organization
  │
  ├────────► Evidence
  │             │
  │             └────────► EvidenceVersion ────────► EvidenceUse
  """



router = APIRouter(prefix="/organizations/{organization_id}/evidence", 
                   tags=["evidence"])


@router.post(
    "",
    response_model=EvidenceCreatedPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence(
    request: EvidenceCreate,
    tenant: TenantContext = Depends(
        get_tenant_context
    ),
    session: Session = Depends(
        get_session
    ),
) -> EvidenceCreatedPublic:
    
    try:
        db_evidence, db_version = (
            create_evidence_service(
                tenant=tenant,
                name=request.name,
                original_filename=(
                    request.version.original_filename
                ),
                content_type=(
                    request.version.content_type
                ),
                size_bytes=(
                    request.version.size_bytes
                ),
                checksum_sha256=request.version.checksum_sha256,
                session=session,
            )
        )

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evidence could not be created",
        ) from error

    return EvidenceCreatedPublic(
        evidence=to_evidence_public(
            db_evidence,
        ),
        version=to_evidence_version_public(
            db_version,
        ),
    )


#creates EvidenceVersion as pending
@router.post(
    "/{evidence_id}/versions",
    response_model=EvidenceVersionPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_version(
    request: EvidenceVersionCreate,
    evidence_id: int = Path(gt=0),
    tenant: TenantContext = Depends(get_tenant_context),
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=128,
    ),
    session: Session = Depends(get_session),
    
) -> EvidenceVersionPublic:
    
    try:
        db_version = create_evidence_version_service(
            tenant=tenant,
            evidence_id=evidence_id,
            original_filename=(
                request.original_filename
            ),
            content_type=request.content_type,
            size_bytes=request.size_bytes,
            idempotency_key=idempotency_key,
            checksum_sha256=request.checksum_sha256,

            session=session,
        )

    except EvidenceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        ) from error
    
    except IdempotencyConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Idempotency-Key was already used "
                "for a different request"
            ),
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evidence version could not be created",
        ) from error

    return to_evidence_version_public(
        db_version
    )


#generates the presigned S3 PUT URL
@router.post(
    "/{evidence_id}/versions/{evidence_version_id}/upload-url",
    response_model=EvidenceUploadUrlPublic,
    status_code=status.HTTP_200_OK,
)
def create_evidence_version_upload_url(
    evidence_id: int = Path(gt=0),
    evidence_version_id: int = Path(gt=0),
    tenant: TenantContext = Depends(
        get_tenant_context
    ),
    session: Session = Depends(
        get_session
    ),
    object_store: S3ObjectStore = Depends(
        get_s3_object_store #talks to S3
    ),
) -> EvidenceUploadUrlPublic:

    try:
        upload = (
            create_evidence_version_upload_url_service(
                tenant=tenant,
                evidence_id=evidence_id,
                evidence_version_id=(
                    evidence_version_id
                ),
                object_store=object_store,
                session=session,
            )
        )

    except EvidenceVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence version not found",
        ) from error

    except EvidenceVersionNotPendingError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Evidence version is not pending"
            ),
        ) from error

    except EvidenceStorageError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Evidence storage is unavailable"
            ),
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Evidence upload URL "
                "could not be created"
            ),
        ) from error

    return to_evidence_upload_url_public(
        upload
    )





@router.post(
    "/{evidence_id}/versions/{evidence_version_id}/complete",
    response_model=EvidenceVersionPublic,
    status_code=status.HTTP_200_OK,
)
def complete_evidence_version_upload(
    evidence_id: int = Path(gt=0),
    evidence_version_id: int = Path(gt=0),
    tenant: TenantContext = Depends(
        get_tenant_context
    ),
    session: Session = Depends(
        get_session
    ),
    object_store: S3ObjectStore = Depends(
        get_s3_object_store
    ),
) -> EvidenceVersionPublic:
    
    try:
        db_version = (
            complete_evidence_version_upload_service(
                tenant=tenant,
                evidence_id=evidence_id,
                evidence_version_id=(
                    evidence_version_id
                ),
                object_store=object_store,
                session=session,
            )
        )

    except EvidenceVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence version not found",
        ) from error
    
    except EvidenceVersionNotPendingError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Evidence version cannot be "
                "completed from its current state"
            ),
        ) from error
    
    except EvidenceUploadNotReadyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evidence upload is not ready",
        ) from error
    
    except EvidenceStorageError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Evidence storage is temporarily "
                "unavailable"
            ),
        ) from error
    
    except EvidenceUploadVerificationError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evidence upload verification failed",
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Evidence upload could not be "
                "completed"
            ),
        ) from error

    return to_evidence_version_public(
        db_version
    )


