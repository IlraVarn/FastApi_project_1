

class AppError(Exception):
    default_detail = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)

class DataIntegrityError(Exception):
    default_detail = "database integrity error"


class DuplicateCustomerEmailError(AppError):
    default_detail = "customer email already exists"


class CustomerNotFoundError(AppError):
    default_detail = "customer not found"


class NotFoundError(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail

class ConflictError(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail
