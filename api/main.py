from fastapi import FastAPI
from api.v1 import dashboard, maintenance

app = FastAPI()

app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1", tags=["maintenance"])