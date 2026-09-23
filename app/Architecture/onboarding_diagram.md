                    USER / ORG ONBOARDING DIAGRAM 

SELF-SERVICE                              ORG-FIRST
────────────                              ─────────

User authenticates                       Platform creates Organization
↓                                        ↓
AuthContext(user_id)                     Organization exists
↓                                        ↓
POST /organizations                      invite / provisioning process
↓                                        ↓
create Organization                      DEV: simulate acceptance
+                                        PROD: IdP handles acceptance
create active Membership                 ↓
(admin)                                  create/link User
                                         +
                                         create active Membership

              \                          /
               \                        /
                └────── CONVERGE ──────┘
                           ↓
                  User + Organization
                    + active Membership
                           ↓


                       NORMAL USE

Client sends:

GET /organizations/17/orders
                  ↑
          organization_id = 17
              UNTRUSTED
                  │
                  │
credential ───────┘
    ↓
get_current_user()
    ↓
AuthContext(user_id)
    │
    └──────────────┐
                   ↓
          get_tenant_context(
              AuthContext,
              organization_id
          )
                   ↓
       look up active Membership:
       user_id + organization_id
                   ↓
            membership exists?
             /            \
           NO              YES
           ↓                ↓
          403        TenantContext(
                         user_id,
                         organization_id
                     )
                         ↓
                     endpoint
                         ↓
                 operation service
                         ↓
                tenant-scoped storage
                         ↓
             WHERE organization_id =
                   verified tenant



The role="admin" assignment during self-service is provisioning authorization data. The actual authorization decision occurs later when that membership/role is checked for a request.


User → Membership ← Organization → Order → OrderItem

foreign keys:

Membership.user_id
→ users.id

Membership.organization_id
→ organizations.id

Order.organization_id
→ organizations.id

OrderItem.order_id
→ orders.id
