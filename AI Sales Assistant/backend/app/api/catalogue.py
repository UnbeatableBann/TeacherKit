from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.plugins.catalogue_connectors.csv_connector import ingest_csv

router = APIRouter()

@router.post("/upload")
async def upload_catalogue(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    # Schedule ingest in background
    background_tasks.add_task(ingest_csv, tenant_id, content.decode("utf-8"), db)
    return {"status": "accepted", "message": "Catalogue ingestion started in background"}
