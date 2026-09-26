from fastapi import FastAPI

from backend.app.routers.batteries import router as battery_router
from backend.app.routers.organizations import router as organization_router
from backend.app.routers.users import router as user_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.inspections import router as inspection_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.certificates import (
    router as certificate_router,
)
from backend.app.routers.attachment import router as attachment_router
from fastapi.staticfiles import StaticFiles
from backend.app.routers.maintenance import router as maintenance_router
from backend.app.routers.alerts import router as alert_router
app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "BatteryOS API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(battery_router)
app.include_router(organization_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(inspection_router)
app.include_router(dashboard_router)
app.include_router(certificate_router)
app.include_router(attachment_router)
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads"),
    name="uploads",
)
app.include_router(maintenance_router)
app.include_router(alert_router)