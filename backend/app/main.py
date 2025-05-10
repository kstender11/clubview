from fastapi import FastAPI
from app.api.venues import router as venues_router
from app.api.reports import router as reports_router

app = FastAPI()
app.include_router(venues_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("path/to/favicon.ico")
