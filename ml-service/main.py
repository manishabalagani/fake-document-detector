from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from services.document_analyzer import analyze_pdf


app = FastAPI(
    title="Fake Document Detection ML Service",
    description="Document analysis and fake-document risk detection service",
    version="1.0.0"
)


UPLOAD_DIR = Path("temporary_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Fake Document Detection ML Service is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported at this stage"
        )

    file_path = UPLOAD_DIR / file.filename

    try:

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = analyze_pdf(str(file_path))

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if file_path.exists():
            file_path.unlink()