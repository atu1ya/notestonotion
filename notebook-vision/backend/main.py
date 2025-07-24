from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from ocr_utils import OCRProcessor
import logging

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
    allow_headers=["*"],
)

# Initialize OCR processor
try:
    ocr_processor = OCRProcessor(languages=['en'], gpu=True)
    logger.info("OCR processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OCR processor: {e}")
    ocr_processor = None


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
