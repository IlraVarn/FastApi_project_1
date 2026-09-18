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
