From the user’s perspective:
Choose file
↓
Upload
↓
Available
Behind the scenes:

1. Browser examines file
    Computes checksum sha256
    Browser generates/reuses Idempotency-Key
        ↓
2. Browser → FastAPI
   Create EvidenceVersion
   FastAPI builds request hash
        ↓
3. resolve idempotency attempt
    ├─ same key + same hash
            → return original EvidenceVersion
            → original storage_key is reused

    └─ new key → 
            → claim IdempotencyRecord
            → lock parent Evidence
            → read latest version
            → calculate next version number
            → build storage_key
            → create PENDING EvidenceVersion with that storage_key
            → flush to get EvidenceVersion ID
            → store EvidenceVersion ID in IdempotencyRecord
            → COMMIT

        ↓
4. Browser → FastAPI
   request upload URL
        ↓
5. FastAPI → AWS SDK
   create temporary S3 permission
        ↓
6. FastAPI → Browser
   presigned URL + required headers
        ↓
7. Browser → S3
   PUT actual file bytes
        ↓
8. Browser → FastAPI
   complete upload
        ↓
9. FastAPI → S3
   HEAD object
        ↓
10. FastAPI compares:
    expected size/checksum
    vs
    actual S3 size/checksum
        ↓
11. PostgreSQL
    PENDING → AVAILABLE

That entire sequence can happen from one Upload button.
