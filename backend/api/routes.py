from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from backend.services.catalogue_service import process_catalogue
from backend.pricing.pricing_loader import load_pricing_from_pdf
from backend.agents.orchestrator import MainOrchestrator


router = APIRouter()


# --------------------------------------------------
# ORCHESTRATOR (SINGLE INSTANCE)
# --------------------------------------------------
orchestrator = MainOrchestrator()


# --------------------------------------------------
# MAIN RFP API
# --------------------------------------------------
@router.post("/process-rfp")
async def process_rfp(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        # -----------------------------
        # Save file (UNIQUE NAME FIX)
        # -----------------------------
        os.makedirs("data/rfps", exist_ok=True)

        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join("data/rfps", unique_name)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # -----------------------------
        # Run workflow
        # -----------------------------
        result = orchestrator.start_workflow(
            file_path=file_path,
            extracted_text=""  # (future: pass pre-extracted text if needed)
        )

        # -----------------------------
        # RESPONSE BUILD
        # -----------------------------
        return {
            "rfp_summary": result.get("rfp_summary", {}),
            "pricing_summary": result.get("pricing_summary", {}),

            "decision_table": result.get("decision_table", []),

            "top_sku_recommendations": result.get("top_sku_recommendations", []),

            "spec_match_scores": result.get("spec_match_scores", {}),

            # 🔥 TECHNICAL INSIGHTS
            "status": result.get("status", "success"),
            "error": result.get("error"),
            "analysis": result.get("analysis"),
            "suggested_skus": result.get("suggested_skus", []),
            "recommendation": result.get("recommendation")
        }

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


# --------------------------------------------------
# PRODUCT CATALOGUE UPLOAD
# --------------------------------------------------
@router.post("/upload-product-catalogue")
async def upload_catalogue(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        file_path = f"temp_{uuid.uuid4()}_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        result = process_catalogue(file_path)

        return {
            "status": "success",
            "message": "Catalogue processed successfully",
            "products_added": result.get("inserted", 0)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Catalogue processing failed: {str(e)}"
        )


# --------------------------------------------------
# PRICING UPLOAD
# --------------------------------------------------
@router.post("/upload-pricing")
async def upload_pricing(file: UploadFile = File(...)):

    try:
        content = await file.read()

        entries_added = load_pricing_from_pdf(content)

        return {
            "status": "success",
            "entries_added": entries_added
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pricing upload failed: {str(e)}"
        )