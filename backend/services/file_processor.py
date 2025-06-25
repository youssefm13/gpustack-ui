import pdfplumber
from docx import Document
from PIL import Image
import io
from fastapi import UploadFile

async def process_file(file: UploadFile):
    content = ""

    if file.content_type == "application/pdf":
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                content += page.extract_text() or ""

    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file.file)
        content = "\n".join(paragraph.text for paragraph in doc.paragraphs)

    elif file.content_type.startswith("image/"):
        img = Image.open(io.BytesIO(await file.read()))
        content = f"[Image uploaded: {img.size}, format: {img.format}]"

    else:
        content = (await file.read()).decode("utf-8")

    return content

