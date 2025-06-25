from fastapi import APIRouter, UploadFile, File
from services.file_processor import process_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await process_file(file)
    return {"content": content}
