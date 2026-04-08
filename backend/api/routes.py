from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from backend.services.catalogue_service import process_catalogue
from backend.pricing.pricing_loader import load_pricing_from_pdf

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



#Related to catalogue uploading



@router.post("/upload-product-catalogue")
async def upload_catalogue(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = process_catalogue(file_path)

    return {
        "message": "Catalogue processed successfully",
        "products_added": result["inserted"]
    }

#===============PRICING RELATED==================

@router.post("/upload-pricing")
async def upload_pricing(file: UploadFile = File(...)):

    content = await file.read()

    entries_added = load_pricing_from_pdf(content)

    return {
        "status": "success",
        "entries_added": entries_added
    }