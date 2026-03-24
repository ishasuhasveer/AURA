from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.agents.orchestrator import MainOrchestrator

router = APIRouter()


# ---------------- ORCHESTRATOR ----------------
def get_orchestrator():
    return MainOrchestrator()


# ---------------- NLP STUB (STRUCTURED OUTPUT) ----------------
def extract_text_stub(file: UploadFile) -> dict:
    """
    TEMPORARY structured stub.
    This simulates NLP output (RFP → structured JSON).
    """

    return {
        "technical_requirements": [
            {
                "voltage": 11,
                "conductor": "Copper",
                "cores": 3,
                "size_sqmm": 35,
                "insulation": "XLPE"
            }
        ],
        "quantities": {
            "CU_3C_35_11KV": 10
        }
    }


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

        # Read file (not used yet, but required for real pipeline)
        contents = await file.read()

        # 🔥 FIX: structured data instead of raw string
        rfp_data = extract_text_stub(file)

        # 🔥 FIX: pass structured data to workflow
        result = orchestrator.start_workflow(
            file_name=file.filename,
            rfp_data=rfp_data
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