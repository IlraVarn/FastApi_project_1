from app.tenancy.context import TenantContext
from app.tenancy.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
                     Path,
    )
from sqlmodel import Session

from app.db import get_session

from app.schemas import (
   EvidenceCreatedPublic,
   EvidenceCreate,
   EvidenceVersionCreate,
   EvidenceVersionPublic,
    )

from app.services.evidence import (
    create_evidence_service,
    create_evidence_version_service,
    )

from app.errors import (
    EvidenceNotFoundError, 
    DataIntegrityError,
    )

from app.mappers.evidence_mappers import (
    to_evidence_public,
    to_evidence_version_public,
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


@router.post(
    "/{evidence_id}/versions",
    response_model=EvidenceVersionPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_version(
    request: EvidenceVersionCreate,
    evidence_id: int = Path(gt=0),
    tenant: TenantContext = Depends(get_tenant_context),
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
            session=session,
        )

    except EvidenceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evidence version could not be created",
        ) from error

    return to_evidence_version_public(
        db_version
    )


