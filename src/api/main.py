from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
from typing import Dict, Any
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SupermarketAIException
from src.api.routes import (
    forecast_router,
    inventory_router,
    analytics_router,
    products_router,
    assistant_router,
)

logger = get_logger(__name__)

app = FastAPI(
    title="AI Supermarket Demand Forecasting & Inventory Assistant",
    description="End-to-end AI platform for supermarket analytics",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={"method": request.method, "path": request.url.path},
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - {process_time:.3f}s",
        extra={
            "status_code": response.status_code,
            "process_time": process_time,
        },
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(SupermarketAIException)
async def supermarket_ai_exception_handler(
    request: Request,
    exc: SupermarketAIException,
) -> JSONResponse:
    logger.error(f"SupermarketAIException: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.error(f"Validation error: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    logger.error(f"HTTPException: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# Include routers
app.include_router(forecast_router, prefix="/api/v1/forecast", tags=["Forecast"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(assistant_router, prefix="/api/v1/assistant", tags=["Assistant"])


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Supermarket Platform",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "AI Supermarket Demand Forecasting & Inventory Assistant",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
    }