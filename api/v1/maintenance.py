from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from db.config import maintenance_history_collection
import uuid
from datetime import datetime, timezone
from api.v1.utils import enter_maintenance_mode, exist_maintenance_mode


router = APIRouter()
scheduler = BackgroundScheduler()
scheduler.start()

class CallbackRequest(BaseModel):
    start: datetime
    end: datetime
    description: str
    related_services: list

@router.post("/schedule-maintenance")
def schedule_callback(data: CallbackRequest):
    delay_id = str(uuid.uuid4())
    if data.start <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="callback_time must be in the future")
    
    # Callback to enter maintenance mode
    scheduler.add_job(
        func=enter_maintenance_mode,
        trigger="date",
        run_date=data.start,
        args=[data.description, data.related_services, data.start],
        id=delay_id,
        replace_existing=True
    )
    print("Scheduling a job for entering maintenance mode ...")
    delay_id = str(uuid.uuid4())
    # Callback to exit maintenance mode
    scheduler.add_job(
        func=exist_maintenance_mode,
        trigger="date",
        run_date=data.end,
        args=[data.description, data.related_services, data.end],
        id=delay_id,
        replace_existing=True
    )
    print("Scheduling a job for exiting maintenance mode ...")
    maintenance_history_collection.insert_one(data.model_dump())