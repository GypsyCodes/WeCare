"""
Custom exception classes for We Care application
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class WeCareException(Exception):
    """Base exception for We Care application"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(WeCareException):
    """Validation error exception"""
    pass


class NotFoundError(WeCareException):
    """Resource not found exception"""
    pass


class PermissionDeniedError(WeCareException):
    """Permission denied exception"""
    pass


class BusinessRuleError(WeCareException):
    """Business rule violation exception"""
    pass


class ProcessingError(WeCareException):
    """Processing error exception"""
    pass


class GPSValidationError(WeCareException):
    """GPS validation error exception"""
    pass


class CheckinError(WeCareException):
    """Check-in related error exception"""
    pass


class DocumentProcessingError(WeCareException):
    """Document processing error exception"""
    pass


class ReportGenerationError(WeCareException):
    """Report generation error exception"""
    pass


# HTTP Exception helpers
def raise_validation_error(message: str, details: Optional[Dict[str, Any]] = None):
    """Raise HTTP validation error"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": message,
            "type": "validation_error",
            "details": details or {}
        }
    )


def raise_not_found_error(resource: str, identifier: Any = None):
    """Raise HTTP not found error"""
    message = f"{resource} not found"
    if identifier:
        message += f" (ID: {identifier})"
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": message,
            "type": "not_found_error",
            "resource": resource,
            "identifier": identifier
        }
    )


def raise_permission_denied_error(message: str = "Permission denied"):
    """Raise HTTP permission denied error"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "message": message,
            "type": "permission_denied_error"
        }
    )


def raise_business_rule_error(message: str, rule: str, details: Optional[Dict[str, Any]] = None):
    """Raise HTTP business rule error"""
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": message,
            "type": "business_rule_error",
            "rule": rule,
            "details": details or {}
        }
    ) 