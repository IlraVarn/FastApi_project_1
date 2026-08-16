

class AppError(Exception):
    default_detail = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)




class DataIntegrityError(AppError):
    default_detail = "database integrity error"

class DuplicateCustomerEmailError(AppError):
    default_detail = "customer email already exists"

class CustomerNotFoundError(AppError):
    default_detail = "customer not found"

class OrderNotFoundError(AppError):
    default_detail = "order not found"

class ItemNotFoundError(AppError):
    default_detail = "item not found"

class ConflictError(AppError):
    default_detail = "conflict"

class InvalidOrderUpdateError(AppError):
    default_detail = "request is empty or supplies null"

class InvalidOrderStateTransitionError(AppError):
    default_detail = "requested change conflicts with the order's current state"


class UserNotFoundError(AppError):
    default_detail = "user not found"


# application/domain error. It does not know anything about HTTP.
class TenantAccessDeniedError(Exception):
    pass

