class NotFoundError(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail

class ConflictError(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail