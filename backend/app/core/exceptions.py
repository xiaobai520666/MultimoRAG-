"""异常体系"""


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, code: int, message: str, detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ParamError(AppException):
    """参数错误 4001"""

    def __init__(self, message: str = "参数错误", detail: str = ""):
        super().__init__(code=4001, message=message, detail=detail)


class NotFoundError(AppException):
    """资源不存在 4004"""

    def __init__(self, message: str = "资源不存在", detail: str = ""):
        super().__init__(code=4004, message=message, detail=detail)


class InternalError(AppException):
    """内部错误 5001"""

    def __init__(self, message: str = "内部错误", detail: str = ""):
        super().__init__(code=5001, message=message, detail=detail)


class APIError(AppException):
    """外部 API 调用失败 5002"""

    def __init__(self, message: str = "外部 API 调用失败", detail: str = ""):
        super().__init__(code=5002, message=message, detail=detail)
