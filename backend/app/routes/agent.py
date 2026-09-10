import io
import logging
from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from app.agent.graph import process_user_query
from app.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for interactive complaint intake and updates."""
    try:
        result = await process_user_query(
            message=request.message,
            current_form=request.current_form,
            current_risk=request.current_risk,
        )
        return ChatResponse(
            reply=result.get("reply", ""),
            updated_form=result.get("updated_form", {}),
            updated_risk=result.get("updated_risk", {}),
            completeness_score=result.get("completeness_score", 0),
        )
    except Exception as exc:
        logger.exception("Error processing chat message: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to process chat query: {str(exc)}")


@router.post("/upload", response_model=ChatResponse)
async def upload_document_endpoint(file: UploadFile = File(...)) -> ChatResponse:
    """Upload PDF or TXT complaint document/email, extract text, and run QMS intake analysis."""
    try:
        contents = await file.read()
        filename = (file.filename or "").lower()
        extracted_text = ""

        if filename.endswith(".pdf") or file.content_type == "application/pdf":
            try:
                reader = PdfReader(io.BytesIO(contents))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                extracted_text = "\n".join(pages_text).strip()
            except Exception as pdf_err:
                logger.error("Failed to parse PDF: %s", pdf_err)
                raise HTTPException(status_code=400, detail=f"Invalid or corrupted PDF file: {pdf_err}")
        else:
            # Default to text decoding (TXT, EML, CSV, etc.)
            try:
                extracted_text = contents.decode("utf-8", errors="ignore").strip()
            except Exception as txt_err:
                raise HTTPException(status_code=400, detail=f"Could not read text file: {txt_err}")

        if not extracted_text:
            raise HTTPException(status_code=400, detail="No readable text could be extracted from uploaded file.")

        result = await process_user_query(
            message=extracted_text,
            current_form={},
            current_risk={},
        )

        return ChatResponse(
            reply=result.get("reply", "Document processed successfully."),
            updated_form=result.get("updated_form", {}),
            updated_risk=result.get("updated_risk", {}),
            completeness_score=result.get("completeness_score", 0),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing uploaded document: %s", exc)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(exc)}")
