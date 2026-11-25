"""Custom application exceptions."""

from fastapi import HTTPException, status


class AirGuardException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class ResourceNotFoundException(AirGuardException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ExternalServiceError(AirGuardException):
    def __init__(self, detail: str = "External atmospheric service unavailable"):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


class UpstreamServiceUnavailableException(AirGuardException):
    def __init__(self, detail: str = "Upstream environmental data service unavailable"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class UnauthorizedException(AirGuardException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
