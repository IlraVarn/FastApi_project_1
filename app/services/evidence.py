
from app.tenancy.context import TenantContext
from app.models.evidence.evidence import Evidence, EvidenceVersion
from app.models import IdempotencyRecord
from sqlmodel import Session
from app.storage.gates import get_active_gate_by_id
from app.errors import ( 
    DataIntegrityError,
    EvidenceNotFoundError,
    IdempotencyConflictError,
    EvidenceStorageError,
    EvidenceUploadNotReadyError,
    EvidenceUploadVerificationError,
    EvidenceVersionNotFoundError,
    EvidenceVersionNotPendingError,
)
from app.storage.evidence import (
    add_evidence_record,
    add_evidence_version_record,
    get_evidence_by_id_and_organization_for_update,
    get_latest_evidence_version_record,
    get_evidence_version_by_id_evidence_and_organization,
    get_evidence_version_by_id_evidence_and_organization_for_update,
    mark_evidence_version_available_record,
    get_evidence_version_by_id_and_evidence
)

from app.infrastructure.s3 import (
    PresignedUpload,
    S3ObjectNotFoundError,
    S3ObjectStore,
    S3ObjectStoreError,
)
from app.services.idempotency import (
    build_idempotency_request_hash,
    resolve_idempotency_attempt
    )

from app.storage.idempotency import (
    try_claim_idempotency_record,
    get_idempotency_record,
    complete_idempotency_record,
)

from sqlalchemy.exc import IntegrityError
from app.models.evidence.evidence import EvidenceVersion, Evidence
from uuid import uuid4
from app.enums import EvidenceUploadStatusType
from datetime import datetime, UTC



CREATE_EVIDENCE_OPERATION = (
    "evidence.create"
)

CREATE_EVIDENCE_VERSION_OPERATION = (
    "evidence.version.create"
)

EVIDENCE_UPLOAD_URL_TTL_SECONDS = 900

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
    checksum_sha256: str,
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
            checksum_sha256=checksum_sha256,
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


#with idempotency
def create_evidence_version_service(
    *,
    tenant: TenantContext,
    evidence_id: int,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    checksum_sha256: str,
    idempotency_key: str,
    session: Session,
) -> EvidenceVersion:

    #fingerprint the request contents
    idempotency_request_hash = build_idempotency_request_hash(
        values={
            "user_id": tenant.user_id,
            "evidence_id": evidence_id,
            "original_filename": original_filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "checksum_sha256": checksum_sha256,
        },
    )

    #Ask idempotency system: NEW or RETRY?
    try:
        (
            idempotency_record_id, existing_record
            ) = resolve_idempotency_attempt(
            organization_id=tenant.organization_id,
            operation=CREATE_EVIDENCE_VERSION_OPERATION,
            idempotency_key=idempotency_key,
            idempotency_request_hash=idempotency_request_hash,
            session=session,
        )

        # REPLAY (return the EvidenceVersion created the first time)
        if existing_record is not None:
            return _replay_evidence_version_create(
                tenant=tenant,
                idempotency_record=existing_record,
                session=session,
            )

        # defensive check if we get (None, None)
        if idempotency_record_id is None:
            raise DataIntegrityError()

        #genuinely new request, so create the new EvidenceVersion
        db_version = _create_new_evidence_version(
            tenant=tenant,
            evidence_id=evidence_id,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
            idempotency_record_id=(
                idempotency_record_id
            ),
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



#for idempotency for EvidenceVersion:
#“This is a retry. Find and return the EvidenceVersion 
# that the original request already created.”
def _replay_evidence_version_create(
    *,
    tenant: TenantContext,
    idempotency_record: IdempotencyRecord,
    session: Session,
) -> EvidenceVersion:

    if idempotency_record.evidence_id is None:
        raise DataIntegrityError()

    if idempotency_record.evidence_version_id is None:
        raise DataIntegrityError()

    db_version = (
        get_evidence_version_by_id_evidence_and_organization(
            evidence_version_id=(
                idempotency_record.evidence_version_id
            ),
            evidence_id=(
                idempotency_record.evidence_id
            ),
            organization_id=(
                tenant.organization_id
            ),
            session=session,
        )
    )

    if db_version is None:
        raise DataIntegrityError()

    return db_version

#helper for idempotency for EvidenceVersion:
#“This is genuinely a new request. 
# Create the next EvidenceVersion.”
def _create_new_evidence_version(
    *,
    tenant: TenantContext,
    evidence_id: int,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    checksum_sha256: str,
    idempotency_record_id: int,
    session: Session,
) -> EvidenceVersion:

    db_evidence = (
        get_evidence_by_id_and_organization_for_update(
            evidence_id=evidence_id,
            organization_id=tenant.organization_id,
            session=session,
        )
    )

    if db_evidence is None:
        raise EvidenceNotFoundError()

    if db_evidence.id is None:
        raise DataIntegrityError()

    verified_evidence_id = db_evidence.id

    latest_version = (
        get_latest_evidence_version_record(
            evidence_id=verified_evidence_id,
            session=session,
        )
    )

    if latest_version is None:
        raise DataIntegrityError()

    version_number = (
        latest_version.version_number + 1
    )

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
        checksum_sha256=checksum_sha256,
        created_by_user_id=tenant.user_id,
        session=session,
    )

    session.flush()

    if db_version.id is None:
        raise DataIntegrityError()


    #the new idempotency record gets linked 
    # to the actual EvidenceVersion that was just created
    result_was_set = (
        complete_idempotency_record(
            idempotency_record_id=(
                idempotency_record_id
            ),
            evidence_id=verified_evidence_id,
            evidence_version_id=db_version.id,
            session=session,
        )
    )
    #if 
    if not result_was_set:
        raise DataIntegrityError()

    return db_version



#for URL
def create_evidence_version_upload_url_service(
    *,
    tenant: TenantContext,
    evidence_id: int,
    evidence_version_id: int,
    object_store: S3ObjectStore,
    session: Session,
) -> PresignedUpload:

    """Given:
    - current tenant
    - evidence_id
    - evidence_version_id

    prove that this tenant owns that exact EvidenceVersion
            ↓
    prove the version is still PENDING
            ↓
    ask S3ObjectStore to create temporary PUT permission
            ↓
    return that permission to the router to upload the file directly to S3"""

    db_version = (
        get_evidence_version_by_id_evidence_and_organization(
            evidence_version_id=(
                evidence_version_id
            ),
            evidence_id=evidence_id,
            organization_id=(
                tenant.organization_id
            ),
            session=session,
        )
    )

    if db_version is None:
        raise EvidenceVersionNotFoundError()

    if (
        db_version.upload_status
        != EvidenceUploadStatusType.PENDING.value
    ):
        raise EvidenceVersionNotPendingError()

    
    #S3 infrastructure adapter boundary:
    # create a temporary PUT permission
    # allowing the browser to upload the expected bytes
    # to this exact object key using these required properties
    # returns PresignedUpload tied to a PUT method


    try: 
        return object_store.create_presigned_upload(
            storage_key=db_version.storage_key,
            content_type=db_version.content_type,
            checksum_sha256=db_version.checksum_sha256,
            expires_in_seconds=(
                EVIDENCE_UPLOAD_URL_TTL_SECONDS
            ),
        )

    except ValueError as error:
        raise DataIntegrityError() from error

    except S3ObjectStoreError as error:
        raise EvidenceStorageError() from error


def complete_evidence_version_upload_service(
    *,
    tenant: TenantContext,
    evidence_id: int,
    evidence_version_id: int,
    object_store: S3ObjectStore,
    session: Session,
) -> EvidenceVersion:


        #get db values recorded BEFORE the upload happened
    try:
        db_version = (
            get_evidence_version_by_id_evidence_and_organization(
                evidence_version_id=(evidence_version_id),
                evidence_id=evidence_id,
                organization_id=(tenant.organization_id),
                session=session,
            )
        )

        if db_version is None:
            raise EvidenceVersionNotFoundError()


        if (
            db_version.upload_status
            == EvidenceUploadStatusType.AVAILABLE.value
        ):
            return db_version
        

        if (
            db_version.upload_status
            != EvidenceUploadStatusType.PENDING.value
        ):
            raise EvidenceVersionNotPendingError()

        #copy the values and end the db session
        expected_storage_key = (
            db_version.storage_key
        )

        expected_size_bytes = (
            db_version.size_bytes
        )

        expected_checksum_sha256 = (
            db_version.checksum_sha256
        )


        # End the read transaction before
        # the external (S3) network operation.
        session.rollback()


        #S3 boundary: ask S3 what actually exists
        #object_store is your S3ObjectMetadata
        #DO NOT ALLOW THE BROWSER TO SUPPLY THIS
        try:
            metadata = (
                object_store.get_object_metadata(
                    storage_key=(
                        expected_storage_key
                    )
                )
            )
        #no file exists:
        except S3ObjectNotFoundError as error:
            raise EvidenceUploadNotReadyError() from error 
        #S3 cannot be reached:
        except S3ObjectStoreError as error:
            raise EvidenceStorageError() from error


        #compare actual size (can only be an int so we compare right away)
        if metadata.size_bytes != expected_size_bytes:
            raise EvidenceUploadVerificationError()
        
        #get actual checksum (can be int or None so extract first)
        actual_checksum_sha256 = metadata.checksum_sha256

        if actual_checksum_sha256 is None:
            raise EvidenceUploadVerificationError()
    
        if actual_checksum_sha256 != expected_checksum_sha256:
            raise EvidenceUploadVerificationError()


        #at this point, still do not mark it AVAILABLE yet.
        # There is one more concurrency problem to solve.
        # since last time we contacted s3, another /complete request could have
        #changed pending -> available. So we can't trust the old db_version anymore
        #Go back to PostgreSQL, get the CURRENT version of this row, 
        # and lock it so nobody else can change it while I finish.

        locked_version = (
            get_evidence_version_by_id_evidence_and_organization_for_update(
                evidence_version_id=(
                    evidence_version_id
                ),
                evidence_id=evidence_id,
                organization_id=(
                    tenant.organization_id
                ),
                session=session,
            )
        )

        if locked_version is None:
            raise EvidenceVersionNotFoundError()

        # Another request may have completed
        # this exact version meanwhile.
        if (
            locked_version.upload_status
            == EvidenceUploadStatusType.AVAILABLE.value
        ):
            session.commit()

            return locked_version

        if (
            locked_version.upload_status
            != EvidenceUploadStatusType.PENDING.value
        ):
            raise EvidenceVersionNotPendingError()

        # Recheck the immutable values after
        # obtaining the DB lock.
        if (
            locked_version.storage_key
            != expected_storage_key
        ):
            raise DataIntegrityError()

        if (
            locked_version.size_bytes
            != expected_size_bytes
        ):
            raise DataIntegrityError()


        if (
            locked_version.checksum_sha256
            != expected_checksum_sha256
        ):
            raise DataIntegrityError()

        mark_evidence_version_available_record(
            db_version=locked_version,
            available_at=datetime.now(UTC),
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(locked_version)

    return locked_version


