                         POST create version
Browser ─────────────────────────────────────────→ FastAPI
                                                      │
                                                      ▼
                                                PostgreSQL
                                               EvidenceVersion
                                                   PENDING
                                                      │
                         POST upload-url              │
Browser ─────────────────────────────────────────→ FastAPI
                                                      │
                                                      ▼
                                                 S3 adapter
                                                      │
                                                      ▼
                                                   AWS S3
                                                      │
                     presigned PUT URL                │
Browser ←─────────────────────────────────────────────┘
   │
   │ PUT actual bytes
   ▼
AWS S3
   │
   │ stores object
   ▼

Browser ───────────── POST /complete ─────────────→ FastAPI
                                                      │
                                                      ▼
                                                 S3 adapter
                                                      │
                                                      ▼
                                                HeadObject
                                                      │
                                      size + SHA-256 metadata
                                                      │
                                                      ▼
                                                   Service
                                                      │
                                 expected == actual?
                                      │               │
                                     no              yes
                                      │               │
                                   reject             ▼
                                               PostgreSQL
                                           PENDING → AVAILABLE



Files belong in S3, not PostgreSQL.

Browser does not receive AWS credentials.

Backend authorizes before issuing presigned access.

Backend chooses the storage key.

Browser uploads bytes directly to S3.

Client's Content-Type is not proof of file type.

Checksum proves byte integrity, not safety.

S3 success does not automatically make evidence AVAILABLE.

Backend independently checks S3.

Only verified object:
PENDING → AVAILABLE.

S3 adapter owns AWS mechanics.

Service owns business decisions.

Tenant authorization happens in backend,
not inside S3.

Presigned URLs are temporary, scoped permissions—not AWS credentials.

PostgreSQL and S3 can temporarily disagree.

PENDING is the safe intermediate state until verification succeeds.



S3 ADAPTER
(app.infrastructure.s3)

Role:
→ translate Acta Secura's storage needs into AWS S3 operations

Owns:
→ boto3 S3 client interaction

→ presigned PUT generation

→ S3 request parameters / headers

→ SHA-256 hex ↔ S3 checksum representation conversion

→ HeadObject calls

→ retrieval of S3 object metadata:
    size
    checksum

→ translation of AWS/boto errors into
   application-facing S3 adapter errors

Does NOT own:
→ tenant authorization

→ EvidenceVersion business rules

→ PENDING / AVAILABLE decisions

→ PostgreSQL transactions

→ database writes

→ version-number allocation

→ HTTP responses

→ public API schemas

→ deciding whether evidence may be used by a Gate


S3 EXECUTION PATH

SERVICE
↓
already-authorized / tenant-scoped EvidenceVersion
↓
S3ObjectStore
↓
AWS S3
↓
PresignedUpload or S3ObjectMetadata
↓
SERVICE
↓
business decision / DB state transition


CURRENT S3 USE CASES

1. CREATE PRESIGNED UPLOAD

SERVICE
↓
validated tenant-owned PENDING EvidenceVersion
↓
S3 ADAPTER
↓
generate presigned PUT
↓
PresignedUpload
↓
SERVICE
↓
MAPPER
↓
EvidenceUploadUrlPublic


2. VERIFY COMPLETED UPLOAD

SERVICE
↓
expected:
storage_key
size_bytes
checksum_sha256
↓
S3 ADAPTER
↓
HeadObject
↓
S3ObjectMetadata:
actual size
actual checksum
↓
SERVICE compares:
expected vs actual
↓
if valid:
PENDING → AVAILABLE
↓
PostgreSQL commit



