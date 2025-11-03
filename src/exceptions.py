class BaseException(Exception):
    detail = "Base Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class ObjectNotFoundException(BaseException):
    detail = "Object Not Found"

class BaseServiceError(ValueError):
    detail = "Base Service Error"

class ValidationServiceError(BaseServiceError):
    detail = "Validation error"