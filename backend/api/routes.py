from fastapi import APIRouter, UploadFile, File, HTTPException
import os

from backend.agents.orchestrator import MainOrchestrator

router = APIRouter()


# ---------------- ORCHESTRATOR ----------------
def get_orchestrator():
    return MainOrchestrator()


# ---------------- MAIN API ----------------
@router.post("/process-rfp")
async def process_rfp(file: UploadFile = File(...)):

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        orchestrator = get_orchestrator()

        # -----------------------------
        # Save file to disk
        # -----------------------------
        os.makedirs("data/rfps", exist_ok=True)

        file_path = f"data/rfps/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # -----------------------------
        # Extracted text (optional for now)
        # -----------------------------
        extracted_text = ""

        # -----------------------------
        # Call orchestrator (CORRECT PARAMS)
        # -----------------------------
        result = orchestrator.start_workflow(
            file_path=file_path,
            extracted_text=extracted_text
        )

        return result

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected internal error: {str(e)}"
        )