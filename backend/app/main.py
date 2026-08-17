from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models import Battery as BatteryModel
from enum import Enum
from datetime import date

class BatteryStatus(str,Enum):
    ACTIVE="Active"
    INACTIVE = "Inactive"
    MAINTENANCE = "Maintenance"

class BatteryCreate(BaseModel):
    serial_number: str = Field(
        min_length=3,
        max_length=100
    )
    manufacturer: str = Field(
        min_length=2,
        max_length=100
    )
    model: str = Field(
        min_length=2,
        max_length=100
    )
    chemistry: str = Field(
        min_length=2,
        max_length=50
    )
    capacity: float = Field(
        gt=0
    )
    voltage: float = Field(
        gt=0
    )
    status: BatteryStatus
    manufacturing_date: date
    installation_date: date | None = None
class BatteryResponse(BaseModel):
    id: int
    serial_number: str
    manufacturer: str
    model: str
    chemistry: str
    capacity: float
    voltage: float
    status: BatteryStatus
    manufacturing_date: date
    installation_date: date | None = None

    class Config:
        from_attributes = True
app=FastAPI()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "BatteryOS API is running"}

@app.get("/health")#route decorator
def health_check():
    return {"status":"healthy"}

@app.get("/batteries",response_model=list[BatteryResponse])
def get_batteries(db: Session = Depends(get_db)):
    return db.query(BatteryModel).all()

@app.get("/batteries/{battery_id}",response_model=BatteryResponse)
def get_battery(battery_id:int,db:Session=Depends(get_db)):
    battery=db.query(BatteryModel).filter(
        BatteryModel.id==battery_id
    ).first()

    if battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found"
        )
    return battery
@app.post("/batteries",response_model=BatteryResponse)
def create_battery(battery:BatteryCreate,
                   db : Session=Depends(get_db)):
    new_battery=BatteryModel(
        serial_number=battery.serial_number,
        manufacturer=battery.manufacturer,
        model=battery.model,
        chemistry=battery.chemistry,
        capacity=battery.capacity,
        voltage=battery.voltage,
        status=battery.status,
        manufacturing_date=battery.manufacturing_date,
        installation_date=battery.installation_date
    )

    db.add(new_battery)
    db.commit()
    db.refresh(new_battery)

    return new_battery
@app.put("/batteries/{battery_id}",response_model=BatteryResponse)
def update_battery(
    battery_id:int,
    battery:BatteryCreate,
    db:Session=Depends(get_db)
):
    existing_battery=db.query(BatteryModel).filter(
        BatteryModel.id==battery_id
    ).first()

    if existing_battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery Not Found"
        )
    existing_battery.serial_number = battery.serial_number
    existing_battery.manufacturer = battery.manufacturer
    existing_battery.model = battery.model
    existing_battery.chemistry = battery.chemistry
    existing_battery.capacity = battery.capacity
    existing_battery.voltage = battery.voltage
    existing_battery.status = battery.status
    existing_battery.manufacturing_date = battery.manufacturing_date
    existing_battery.installation_date = battery.installation_date

    db.commit()
    db.refresh(existing_battery)

    return existing_battery
@app.delete("/batteries/{battery_id}")
def delete_battery(
    battery_id:int,
    db:Session=Depends(get_db)
):
    existing_battery=db.query(BatteryModel).filter(
        BatteryModel.id==battery_id
    ).first()

    if existing_battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery Not found"
        )
    db.delete(existing_battery)
    db.commit()

    return {
        "message":"Battery deleted succesfully",
        "battery_id":battery_id
    }