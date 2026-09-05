from typing import Optional, Any


class SupermarketAIException(Exception):
    """Base exception for the application"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class DataValidationError(SupermarketAIException):
    """Raised when data validation fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=400, details=details)


class DataGenerationError(SupermarketAIException):
    """Raised when data generation fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class ModelTrainingError(SupermarketAIException):
    """Raised when model training fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class ModelNotFoundError(SupermarketAIException):
    """Raised when model is not found"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=404, details=details)


class ForecastError(SupermarketAIException):
    """Raised when forecasting fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class RAGError(SupermarketAIException):
    """Raised when RAG operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class LLMError(SupermarketAIException):
    """Raised when LLM operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class DatabaseError(SupermarketAIException):
    """Raised when database operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)