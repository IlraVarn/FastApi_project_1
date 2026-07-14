

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

    

