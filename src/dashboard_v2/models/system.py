"""Pydantic models for System status data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of a single service."""

    name: str
    healthy: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)


class SystemHealthResponse(BaseModel):
    """Response for system health check."""

    status: str = Field(..., description="Overall status: healthy, degraded, unhealthy")
    services: dict[str, ServiceStatus]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "supabase": {
                        "name": "supabase",
                        "healthy": True,
                        "latency_ms": 45.2,
                        "error": None,
                    },
                    "upbit": {
                        "name": "upbit",
                        "healthy": True,
                        "latency_ms": 120.5,
                        "error": None,
                    },
                },
                "timestamp": "2025-12-17T12:00:00Z",
            }
        }


class EmergencyStatus(BaseModel):
    """Emergency stop status."""

    is_active: bool = Field(..., description="Whether emergency stop is active")
    activated_at: Optional[datetime] = None
    reason: Optional[str] = None
    activated_by: Optional[str] = None
