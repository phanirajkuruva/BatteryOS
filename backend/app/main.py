from fastapi import FastAPI

from backend.app.routers.batteries import router as battery_router


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