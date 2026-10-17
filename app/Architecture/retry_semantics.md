Repeated request semantics across current endpoints

### Create EvidenceVersion

- **Retry mechanism:** Idempotency-Key + request hash + stored result
- **Result:** same EvidenceVersion

### Request upload URL

- **Retry mechanism:** existing PENDING version
- **Result:** new temporary URL is okay

### S3 PUT

- **Retry mechanism:** exact key + checksum + If-None-Match: *
- **Result:** cannot silently overwrite existing object

### /complete

- **Retry mechanism:** state-based idempotency
- **Result:** already AVAILABLE returns same version

### Reads/GETs

- **Retry mechanism:** naturally read-only
- **Result:** no Idempotency-Key needed

