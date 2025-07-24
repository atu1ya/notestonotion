# --- AI-Driven Question Generation with Local LLM (Ollama) ---
@app.post("/api/generate-questions/")
async def generate_questions(payload: dict):
    """
    Generate question-answer pairs from pasted or extracted notes using local Ollama LLM.
    Input: { "text": "<user notes>" }
    Output: { "questions": [ { "type": ..., "question": ..., "answer": ... }, ... ] }
    """
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")

    ollama_url = "http://localhost:11434/api/generate"
    model = "llama3"  # or another math-capable model
    prompt = (
        "You are an expert educator. Given the following notes, generate a set of question-answer pairs that progress from basic recall to conceptual and mathematical/application questions. "
        "Group each pair by type: basic, intermediate, advanced, math. If the topic allows, include at least one math question. "
        "Return a JSON array of objects: { 'type': 'basic|intermediate|advanced|math', 'question': '...', 'answer': '...' }. "
        "Each object MUST have both a 'question' and a correct 'answer'. "
        "Notes: " + text + "\n\nOutput:"
    )
    ollama_payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=ollama_payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        # Try to extract JSON from the LLM response
        import re, json as pyjson
        content = result.get("response", "")
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            questions = pyjson.loads(match.group(0))
        else:
            questions = []
        # Validate that each question has both 'question' and 'answer'
        valid = all(isinstance(q, dict) and q.get('question') and q.get('answer') for q in questions)
        if not valid or not questions:
            raise HTTPException(status_code=500, detail="LLM did not return valid question-answer pairs.")
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama LLM error: {str(e)}")
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import requests
from ocr_utils import (
    OCRProcessor, extract_semantic_flashcards,
    create_deck, rename_deck, delete_deck, add_flashcard, tag_flashcard, untag_flashcard, update_assessment, search_flashcards, DECKS, FLASHCARDS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Notebook Vision API",
    description="OCR API for extracting text and flashcards from handwritten notes",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],

# Initialize OCR processor
try:
    ocr_processor = OCRProcessor(languages=['en'], gpu=True)
    logger.info("OCR processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OCR processor: {e}")
    ocr_processor = None

# --- Deck Management Endpoints ---
@app.post("/api/decks/")
async def api_create_deck(payload: dict):
    name = payload.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Deck name required.")
    deck = create_deck(name)
    if not deck:
        raise HTTPException(status_code=400, detail="Deck already exists.")
    return deck.__dict__

@app.put("/api/decks/{old_name}")
async def api_rename_deck(old_name: str, payload: dict):
    new_name = payload.get("name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New deck name required.")
    if not rename_deck(old_name, new_name):
        raise HTTPException(status_code=400, detail="Rename failed.")
    return {"success": True}

@app.delete("/api/decks/{name}")
async def api_delete_deck(name: str):
    if not delete_deck(name):
        raise HTTPException(status_code=400, detail="Delete failed or cannot delete Default deck.")
    return {"success": True}

@app.get("/api/decks/")
async def api_list_decks():
    return [deck.__dict__ for deck in DECKS.values()]

# --- Flashcard CRUD/Tag/Assessment Endpoints ---
@app.post("/api/flashcards/")
async def api_add_flashcard(payload: dict):
    q = payload.get("question", "").strip()
    a = payload.get("answer", "").strip()
    deck = payload.get("deck", "Default")
    tags = payload.get("tags", [])
    if not q or not a:
        raise HTTPException(status_code=400, detail="Question and answer required.")
    fc = add_flashcard(q, a, deck, tags)
    return fc.to_dict()

@app.post("/api/flashcards/{fc_id}/tag/")
async def api_tag_flashcard(fc_id: str, payload: dict):
    tag = payload.get("tag", "").strip()
    if not tag:
        raise HTTPException(status_code=400, detail="Tag required.")
    if not tag_flashcard(fc_id, tag):
        raise HTTPException(status_code=404, detail="Flashcard not found or already tagged.")
    return {"success": True}

@app.post("/api/flashcards/{fc_id}/untag/")
async def api_untag_flashcard(fc_id: str, payload: dict):
    tag = payload.get("tag", "").strip()
    if not tag:
        raise HTTPException(status_code=400, detail="Tag required.")
    if not untag_flashcard(fc_id, tag):
        raise HTTPException(status_code=404, detail="Flashcard not found or tag missing.")
    return {"success": True}

@app.post("/api/flashcards/{fc_id}/assessment/")
async def api_update_assessment(fc_id: str, payload: dict):
    score = payload.get("score", "").strip()
    if not score:
        raise HTTPException(status_code=400, detail="Score required.")
    if not update_assessment(fc_id, score):
        raise HTTPException(status_code=404, detail="Flashcard not found.")
    return {"success": True}

# --- Flashcard Search/Filter ---
@app.get("/api/flashcards/")
async def api_search_flashcards(query: str = None, deck: str = None, tag: str = None, assessment: str = None):
    results = search_flashcards(query, deck, tag, assessment)
    return results
@app.post("/api/upload/semantic/")
async def upload_image_semantic(file: UploadFile = File(...)):
    """
    Upload an image and extract semantic flashcards using local NLP (no paid LLMs).
    """
    # Validate OCR processor availability
    if ocr_processor is None:
        raise HTTPException(
            status_code=500,
            detail="OCR processor is not available. Please check server configuration."
        )
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file (JPEG, PNG, BMP, TIFF)."
        )
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = 0
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB."
            )
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded."
            )
        # Process the image with OCR
        logger.info(f"Processing image (semantic): {file.filename} ({file_size} bytes)")
        result = ocr_processor.process_image(file_content)
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        # Extract semantic flashcards
        semantic_flashcards = extract_semantic_flashcards(result["extracted_text"])
        logger.info(f"Semantic extraction for {file.filename}: {len(semantic_flashcards) if isinstance(semantic_flashcards, list) else 0} flashcards")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text": result["extracted_text"],
                "semantic_flashcards": semantic_flashcards,
                "total_semantic_flashcards": len(semantic_flashcards) if isinstance(semantic_flashcards, list) else 0
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error (semantic) processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Notebook Vision API is running!",
        "status": "healthy",
        "ocr_available": ocr_processor is not None
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ocr_processor_available": ocr_processor is not None,
        "supported_image_types": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    }


@app.post("/api/upload/")
async def upload_and_process_image(file: UploadFile = File(...)):
    """
    Upload an image file and extract text + flashcards using OCR.
    
    Args:
        file: Uploaded image file (JPEG, PNG, BMP, TIFF)
        
    Returns:
        JSON response with extracted text and flashcards
    """
    
    # Validate OCR processor availability
    if ocr_processor is None:
        raise HTTPException(
            status_code=500,
            detail="OCR processor is not available. Please check server configuration."
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file (JPEG, PNG, BMP, TIFF)."
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = 0
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB."
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded."
            )
        
        # Process the image with OCR
        logger.info(f"Processing image: {file.filename} ({file_size} bytes)")
        result = ocr_processor.process_image(file_content)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Log successful processing
        logger.info(f"Successfully processed {file.filename}: extracted {len(result['flashcards'])} flashcards")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text": result["extracted_text"],
                "flashcards": result["flashcards"],
                "total_flashcards": result["total_flashcards"]
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/test-flashcard-extraction/")
async def test_flashcard_extraction(text: str):
    """
    Test endpoint for flashcard extraction from provided text.
    
    Args:
        text: Text content to analyze for Q/A patterns
        
    Returns:
        JSON response with extracted flashcards
    """
    
    if ocr_processor is None:
        raise HTTPException(
            status_code=500,
            detail="OCR processor is not available."
        )
    
    try:
        flashcards = ocr_processor._extract_flashcards(text)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "input_text": text,
                "flashcards": flashcards,
                "total_flashcards": len(flashcards)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in flashcard extraction test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Flashcard extraction failed: {str(e)}"
        )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
