
from app.tenancy.context import TenantContext
from app.models.evidence import Evidence, EvidenceVersion
from sqlmodel import Session
from app.storage.gates import get_active_gate_by_id
from app.errors import ( 
    DataIntegrityError,
    EvidenceNotFoundError,
)
from app.storage.evidence import (
    add_evidence_record, 
    add_evidence_version_record,
    get_evidence_by_id_and_organization_for_update,
    get_latest_evidence_version_record
)
from sqlalchemy.exc import IntegrityError
from app.models.evidence import EvidenceVersion, Evidence
from uuid import uuid4
from app.enums import EvidenceUploadStatusType



def build_evidence_version_storage_key(
    *,
    organization_id: int,
    evidence_id: int,
    version_number: int,
) -> str:
    return (
        f"organizations/{organization_id}"
        f"/evidence/{evidence_id}"
        f"/versions/{version_number}"
        f"/{uuid4().hex}"
    )


def create_evidence_service(
    *,
    tenant: TenantContext,
    name: str,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    session: Session,
) -> tuple[Evidence, EvidenceVersion]:

    try:
        db_evidence = add_evidence_record(
            organization_id=tenant.organization_id,
            name=name,
            session=session,
        )

        session.flush()

        if db_evidence.id is None:
            raise DataIntegrityError()
        
        created_evidence_id = db_evidence.id

        version_number = 1

        storage_key = (
            build_evidence_version_storage_key(
                organization_id=(
                    tenant.organization_id
                ),
                evidence_id=created_evidence_id,
                version_number=version_number,
            )
        )

        db_version = add_evidence_version_record(
            evidence_id=created_evidence_id,
            version_number=version_number,
            storage_key=storage_key,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            created_by_user_id=tenant.user_id,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_evidence)
    session.refresh(db_version)

    return db_evidence, db_version


def create_evidence_version_service(
    *,
    tenant: TenantContext,
    evidence_id: int,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    session: Session,
) -> EvidenceVersion:
    try:

        db_evidence = get_evidence_by_id_and_organization_for_update(
            evidence_id=evidence_id,
            organization_id=tenant.organization_id,
            session=session,
        )

        if db_evidence is None:
            raise EvidenceNotFoundError()
        
        if db_evidence.id is None:
            raise DataIntegrityError()

        verified_evidence_id = db_evidence.id

        latest_version = get_latest_evidence_version_record(
            evidence_id=verified_evidence_id,
            session=session,
        )

        if latest_version is None:
            raise DataIntegrityError()

        version_number = latest_version.version_number + 1

        storage_key = build_evidence_version_storage_key(
            organization_id=tenant.organization_id,
            evidence_id=verified_evidence_id,
            version_number=version_number,
        )

        db_version = add_evidence_version_record(
            evidence_id=verified_evidence_id,
            version_number=version_number,
            storage_key=storage_key,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            created_by_user_id=tenant.user_id,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_version)

    return db_version


