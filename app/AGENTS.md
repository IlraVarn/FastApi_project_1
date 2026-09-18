# CODEx OPERATING CONTRACT

## Source of truth

The repository is authoritative for the CURRENT IMPLEMENTATION.
Architecture documents/contracts are authoritative for INTENDED ARCHITECTURE.

Before answering architectural questions or modifying code:

1. Inspect the relevant current source files.
2. Inspect relevant architecture documents.
3. Search for all equivalent implementations and call sites.
4. Do not infer current architecture from generic FastAPI, SQLModel,
   AWS, or SaaS conventions.
5. If repository evidence is missing or contradictory, stop and state
   exactly what is unresolved.

## Pre-code reconciliation gate

Before changing:

- auth
- tenancy
- S3/storage
- idempotency
- transactions
- evidence lifecycle
- gate lifecycle
- domain state
- retry behavior

you MUST:

1. Reconstruct the existing implementation.
2. Identify every affected create/mutation path.
3. State existing invariants.
4. Identify the source and timing of every proposed new value.
5. Identify which layer owns every responsibility.
6. Trace:
   creation → mutation → retry → terminal state.
7. Check tenant isolation.
8. Check database/external-system split failures.
9. Verify implementation-sensitive external behavior against
   authoritative primary documentation.
10. Do not write code until reconciliation is complete.
11. Never resolve a conflict by selecting a generic industry pattern.
    Surface the conflict and wait for resolution.

## Teaching contract

I am learning the backend while building it.

When explaining code:

1. Explain the actual production implementation, not a toy alternative.
2. Trace execution in exact order.
3. For every important value state:
   - where it originates
   - which parameter receives it
   - which function uses it
   - what the function returns
   - where the return value goes
4. Explain why each responsibility belongs in its current layer.
5. Explicitly distinguish:
   - request state
   - domain state
   - database state
   - external-system state
6. Do not simplify using code that would later require architectural rewrite.

## Architecture drift rule

Never replace an established Acta Secura architectural decision with
another valid generic pattern without explicitly identifying the conflict.

If current code, documentation, external standards, or prior architectural
contracts disagree:

STOP.

Return:

ARCHITECTURE CONFLICT

