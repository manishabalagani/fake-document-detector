import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from services.document_analyzer import analyze_pdf
from services.ml_predictor import get_model_info

app = FastAPI(title="Fake Document Detector ML Service")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "fake-document-detector-ml"}

@app.get("/model-info")
def model_info():
    try:
        return get_model_info()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Model is unavailable: {exc}") from exc

@app.post("/analyze")
async def analyze_document(document: UploadFile = File(...)):
    filename = document.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF documents are supported by the ML service.")

    content = await document.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded document is empty.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="The uploaded document exceeds the 10 MB limit.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        return analyze_pdf(str(temp_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {exc}") from exc
    finally:
        if temp_path and temp_path.exists():
            os.remove(temp_path)
