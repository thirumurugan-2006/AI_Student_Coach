from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from core.logger import logger
from typing import Any


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(AppException):
    """Database-related exceptions."""
    pass


class AuthenticationException(AppException):
    """Authentication-related exceptions."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(AppException):
    """Authorization-related exceptions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class ValidationException(AppException):
    """Validation-related exceptions."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class LLMException(AppException):
    """LLM/Groq-related exceptions."""
    def __init__(self, message: str = "LLM service error"):
        super().__init__(message, status_code=503)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Global exception handler for custom application exceptions.
    """
    logger.error(f"Application exception: {exc.message} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Global exception handler for HTTP exceptions.
    """
    logger.error(f"HTTP exception: {exc.detail} - Status: {exc.status_code} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )
