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
  │ organization_id
  ▼
Gate
  │
  ├──────── gate_id ────────► GateRequirement
  │
  ├──────── gate_id ────────► GateEvidence
  │
  └──────── gate_id ────────► GateStateTransition


  


TOKEN
  │
  ▼
get_current_user
  │
  ▼
AuthContext
user_id
  │
  │
  ▼
MEMBERSHIP TABLE ◄──── ORGANIZATION
  │                       │
  │ verified              │
  ▼                       │
TenantContext             │
user_id                   │
organization_id ──────────┘
  │
  ▼
GATE
organization_id

