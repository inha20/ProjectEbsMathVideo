"""
core/exceptions.py - 비즈니스 예외 정의 계층
"""
from fastapi import status

class BaseBusinessException(Exception):
    """모든 비즈니스 예외의 기본 클래스"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(BaseBusinessException):
    """인증 관련 예외"""
    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class ResourceNotFoundError(BaseBusinessException):
    """리소스를 찾을 수 없는 경우"""
    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class ExternalAPIError(BaseBusinessException):
    """외부 API 연동 실패 (OpenAI, YouTube 등)"""
    def __init__(self, message: str = "외부 서비스 연동 중 오류가 발생했습니다"):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)
