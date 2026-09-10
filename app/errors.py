

class AppError(Exception):
    default_detail = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class DataIntegrityError(AppError):
    default_detail = "database integrity error"

class DuplicateCustomerEmailError(AppError):
    default_detail = "customer email already exists"


class GateNotFoundError(AppError):
    default_detail = "gate not found"

class ItemNotFoundError(AppError):
    default_detail = "item not found"

class ConflictError(AppError):
    default_detail = "conflict"

class InvalidGateUpdateError(AppError):
    default_detail = "request is empty or supplies null"

class InvalidGateStateTransitionError(AppError):
    default_detail = "requested change conflicts with the gate's current state"


class UserNotFoundError(AppError):
    default_detail = "user not found"


# application/domain error. It does not know anything about HTTP.
class TenantAccessDeniedError(Exception):
    pass

class RejectionReasonRequiredError(AppError):
    default_detail = "rejection reason required"


class GateArchiveNotAllowedError(AppError):
    default_detail = "draft gate cannot be archived"

class EvidenceNotFoundError(AppError):
    default_detail = "evidence not found"

