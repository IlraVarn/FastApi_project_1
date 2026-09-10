


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
→ AuthContext

TENANCY DEPENDENCY + TENANCY SERVICE
→ Membership verification
→ TenantContext

ROUTER
→ HTTP parsing / dependencies / error mapping

REQUEST MODEL
→ client-input validation

SERVICE
→ business rules / orchestration / transaction ownership

STORAGE
→ SQL queries / persistence / DB representation conversion

ORM MODEL
→ database representation

MAPPER
→ ORM → public response model

FASTAPI
→ public model → JSON