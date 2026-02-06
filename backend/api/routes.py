from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.agents.orchestrator import MainOrchestrator

router = APIRouter()
orchestrator = MainOrchestrator()

def extract_text_stub(file: UploadFile) -> str:
    """
    TEMPORARY stub.
    Replaced later by real PDF extraction pipeline.
    """
    return """
    RFP for electrical cable supply.
    Deadline: 15 February 2026
    """

@router.post("/process-rfp")
async def process_rfp(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        extracted_text = extract_text_stub(file)

        result = orchestrator.start_workflow(
            file_path=file.filename,
            extracted_text=extracted_text
        )

        return result

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected internal error"
        )