"""
Health Check Module for Life as a Garden API

Provides comprehensive health checks for all system components including:
- Database connectivity
- OpenAI API availability
- External services (Frontend, rmapi-wrapper)
- File system permissions
- System resources
"""

import httpx
import openai
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from sqlmodel import text

from database import GardenDatabase
from database.base import get_session
from settings import settings


class HealthChecker:
    """Health check service for monitoring system components."""

    def __init__(self, garden_db: GardenDatabase):
        self.garden_db = garden_db
        self._last_notification_time = None
        self._notification_cooldown = 3600  # 1 hour cooldown between notifications

    async def check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for all system components.

        Checks:
        1. Database connectivity
        2. OpenAI API availability and credits
        3. Frontend service availability
        4. rmapi-wrapper service availability
        5. File system permissions
        6. System resources (if available)
        """

        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "issues": [],
        }

        # Run all health checks
        await self._check_database(health_status)
        await self._check_openai(health_status)
        await self._check_frontend(health_status)
        await self._check_rmapi_wrapper(health_status)
        await self._check_file_system(health_status)
        await self._check_system_resources(health_status)

        # Determine final status
        self._determine_final_status(health_status)

        # Send notification if health check failed
        await self._handle_health_notification(health_status)

        # Return appropriate HTTP response
        return self._create_response(health_status)

    async def _handle_health_notification(self, health_status: Dict[str, Any]) -> None:
        """Send email notification if health check failed and cooldown period has passed."""
        if health_status["overall_status"] == "healthy":
            return

        # Check cooldown period
        current_time = datetime.utcnow()
        if (
            self._last_notification_time
            and (current_time - self._last_notification_time).total_seconds()
            < self._notification_cooldown
        ):
            return

        try:
            from utils.email_service import email_service

            success = email_service.send_health_check_failure_notification(
                health_status
            )
            if success:
                self._last_notification_time = current_time
        except Exception as e:
            # Don't let email failures affect health check results
            print(f"Failed to send health check notification: {str(e)}")

    async def _check_database(self, health_status: Dict[str, Any]) -> None:
        """Check PostgreSQL database connectivity and basic operations."""
        try:
            # Test database connection via SQLModel session
            with get_session() as session:
                result = session.exec(
                    text(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                    )
                ).one()
                table_count = result

            # Test database operations through our service
            stats = self.garden_db.get_database_stats()

            health_status["services"]["database"] = {
                "status": "healthy",
                "details": {
                    "type": "postgresql",
                    "tables_count": table_count,
                    "total_plants": stats.get("total_plants", 0),
                    "total_areals": stats.get("total_areals", 0),
                },
            }
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["issues"].append(f"Database: {str(e)}")
            health_status["overall_status"] = "degraded"

    async def _check_openai(self, health_status: Dict[str, Any]) -> None:
        """Check OpenAI API availability and authentication."""
        try:
            client = openai.OpenAI(api_key=settings.openai_api_key)

            # Test with a minimal request to check API availability and credits
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )

            health_status["services"]["openai"] = {
                "status": "healthy",
                "details": {"model_tested": "gpt-3.5-turbo", "response_received": True},
            }
        except openai.AuthenticationError:
            health_status["services"]["openai"] = {
                "status": "unhealthy",
                "error": "Authentication failed - invalid API key",
            }
            health_status["issues"].append("OpenAI: Authentication failed")
            health_status["overall_status"] = "degraded"
        except openai.RateLimitError:
            health_status["services"]["openai"] = {
                "status": "unhealthy",
                "error": "Rate limit exceeded or no credits available",
            }
            health_status["issues"].append("OpenAI: No credits or rate limit exceeded")
            health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["services"]["openai"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["issues"].append(f"OpenAI: {str(e)}")
            health_status["overall_status"] = "degraded"

    async def _check_frontend(self, health_status: Dict[str, Any]) -> None:
        """Check frontend service availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(settings.frontend_base_url)
                if response.status_code == 200:
                    health_status["services"]["frontend"] = {
                        "status": "healthy",
                        "details": {
                            "url": settings.frontend_base_url,
                            "response_code": response.status_code,
                        },
                    }
                else:
                    health_status["services"]["frontend"] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                    }
                    health_status["issues"].append(
                        f"Frontend: HTTP {response.status_code}"
                    )
                    health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["services"]["frontend"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["issues"].append(f"Frontend: {str(e)}")
            health_status["overall_status"] = "degraded"

    async def _check_rmapi_wrapper(self, health_status: Dict[str, Any]) -> None:
        """Check rmapi-wrapper service availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.rmapi_service_url}/health")
                if response.status_code == 200:
                    health_status["services"]["rmapi_wrapper"] = {
                        "status": "healthy",
                        "details": {
                            "url": settings.rmapi_service_url,
                            "response_code": response.status_code,
                        },
                    }
                else:
                    health_status["services"]["rmapi_wrapper"] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                    }
                    health_status["issues"].append(
                        f"rmapi-wrapper: HTTP {response.status_code}"
                    )
                    health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["services"]["rmapi_wrapper"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["issues"].append(f"rmapi-wrapper: {str(e)}")
            health_status["overall_status"] = "degraded"

    async def _check_file_system(self, health_status: Dict[str, Any]) -> None:
        """Check file system permissions and critical directories."""
        try:
            import os

            # Check critical directories
            critical_dirs = ["input", "output"]
            file_system_details = {}

            for dir_name in critical_dirs:
                dir_path = f"./{dir_name}"
                if os.path.exists(dir_path):
                    file_system_details[dir_name] = {
                        "exists": True,
                        "writable": os.access(dir_path, os.W_OK),
                        "readable": os.access(dir_path, os.R_OK),
                    }
                else:
                    file_system_details[dir_name] = {
                        "exists": False,
                        "writable": False,
                        "readable": False,
                    }
                    health_status["issues"].append(
                        f"File system: Directory {dir_name} does not exist"
                    )
                    health_status["overall_status"] = "degraded"

            health_status["services"]["file_system"] = {
                "status": "healthy"
                if all(
                    d["exists"] and d["writable"] and d["readable"]
                    for d in file_system_details.values()
                )
                else "degraded",
                "details": file_system_details,
            }

        except Exception as e:
            health_status["services"]["file_system"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["issues"].append(f"File system: {str(e)}")
            health_status["overall_status"] = "degraded"

    async def _check_system_resources(self, health_status: Dict[str, Any]) -> None:
        """Check system resources like memory and disk usage."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(".")

            health_status["services"]["system_resources"] = {
                "status": "healthy",
                "details": {
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_free_gb": round(disk.free / (1024**3), 2),
                },
            }

            # Warning if resources are getting low
            if memory.percent > 90 or disk.percent > 90:
                health_status["issues"].append("System resources running low")
                health_status["overall_status"] = "degraded"

        except ImportError:
            # psutil not available, skip this check
            health_status["services"]["system_resources"] = {
                "status": "skipped",
                "details": "psutil not available",
            }
        except Exception as e:
            health_status["services"]["system_resources"] = {
                "status": "unhealthy",
                "error": str(e),
            }

    def _determine_final_status(self, health_status: Dict[str, Any]) -> None:
        """Determine the final overall status based on individual service statuses."""
        if health_status["overall_status"] == "healthy" and health_status["issues"]:
            health_status["overall_status"] = "degraded"

        unhealthy_services = [
            name
            for name, service in health_status["services"].items()
            if service["status"] == "unhealthy"
        ]
        if unhealthy_services:
            health_status["overall_status"] = "unhealthy"

    def _create_response(self, health_status: Dict[str, Any]):
        """Create appropriate HTTP response based on health status."""
        if health_status["overall_status"] == "unhealthy":
            raise HTTPException(status_code=503, detail=health_status)
        elif health_status["overall_status"] == "degraded":
            return JSONResponse(content=health_status, status_code=200)
        else:
            return health_status


# Helper functions for FastAPI endpoints
def create_health_checker(garden_db: GardenDatabase) -> HealthChecker:
    """Factory function to create a HealthChecker instance."""
    return HealthChecker(garden_db)
