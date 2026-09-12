


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
  │
  └────────► WorkflowRecord
                  │
                  └────────► Gate
                               │
                               ├────────► GateRequirement
                               │              │
                               │              └────────► EvidenceUse
                               │                           │
                               │                           └────────►EvidenceVersion
                               │
                               └────────► GateStateTransition


User
  │
  │ user_id
  ▼
Membership
  ▲
  │ organization_id
  │
Organization
  │
  ├──────── organization_id ────────► WorkflowRecord
  │                                      │
  │                                      │ workflow_record_id
  │                                      ▼
  │                                    Gate
  │                                      │
  │                                      ├── gate_id ──► GateRequirement
  │                                      │                  │
  │                                      │                  │ gate_requirement_id
  │                                      │                  ▼
  │                                      │              EvidenceUse
  │                                      │                  │
  │                                      └── gate_id ──► GateStateTransition
  │
  └──────── organization_id ────────► Evidence
                                         │
                                         │ evidence_id
                                         ▼
                                   EvidenceVersion
                                         ▲
                                         │ evidence_version_id
                                         │
                                    EvidenceUse

*One EvidenceVersion can have multiple EvidenceUse records, allowing it to support requirements in several gates.



TOKEN
  │
  ▼
get_current_user
  │
  ▼
AuthContext(user_id)
  │
  │ + organization_id from URL
  ▼
get_tenant_context
  │
  ▼
Membership verification
  │
  ▼
TenantContext(user_id, organization_id)
  │
  ▼
Organization
  │
  ├── WorkflowRecord
  │      │
  │      └── Gate
  │             │
  │             ├── GateRequirement
  │             │       │
  │             │       └── EvidenceUse ──► EvidenceVersion
  │             │
  │             └── GateStateTransition
  │
  └── Evidence
         │
         └── EvidenceVersion



execution architecture:

AUTH DEPENDENCY
→ credential validation
→ AuthContext

TENANCY DEPENDENCY + TENANCY SERVICE
→ Membership verification
→ TenantContext

ROUTER
→ HTTP path/query/body binding
→ dependency injection
→ domain-error → HTTP-error mapping

REQUEST MODEL
→ client-input contract
→ basic field/type validation

SERVICE
→ business rules
→ orchestration
→ transaction ownership
→ commit / rollback
→ enforce operation invariants needed to complete the transaction
→ enforce tenant/resource authorization for protected operations
→ calls Provider Adapter when needed

PROVIDER ADAPTER
→ S3
→ AI provider
→ email/webhooks/etc.

STORAGE
→ SQL queries
→ tenant-scoped/resource-scoped lookups
→ ORM loading
→ staged DB writes
→ DB locks / flush when required

ORM MODEL
→ database representation

MAPPER
→ ORM/internal result → public response model
→ enforce public-output invariants
   e.g. persisted entity ID must exist

RESPONSE MODEL
→ public output contract

FASTAPI
→ response model validation/filtering
→ JSON serialization
→ HTTP response



