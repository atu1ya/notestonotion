import io
import re
from typing import List, Dict, Tuple
from PIL import Image
import easyocr
import numpy as np


class OCRProcessor:
    """
    OCR processor using EasyOCR for handwriting and text recognition.
    Supports flashcard extraction from Q/A patterns.
    """
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = True):
        """
        Initialize the OCR reader.
        
        Args:
            languages: List of language codes for OCR recognition
            gpu: Whether to use GPU acceleration (if available)
        """
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu)
        except Exception as e:
            # Fallback to CPU if GPU fails
            print(f"GPU initialization failed, falling back to CPU: {e}")
            self.reader = easyocr.Reader(languages, gpu=False)
    
    def process_image(self, image_data: bytes) -> Dict[str, any]:
        """
        Process uploaded image and extract text + flashcards.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing extracted text and flashcards
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL Image to numpy array for EasyOCR
            image_array = np.array(image)
            
            # Perform OCR
            ocr_results = self.reader.readtext(image_array, detail=0)
            
            # Join all text with newlines
            extracted_text = '\n'.join(ocr_results)
            
            # Extract flashcards from the text
            flashcards = self._extract_flashcards(extracted_text)
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "flashcards": flashcards,
                "total_flashcards": len(flashcards)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "flashcards": [],
                "total_flashcards": 0
            }
    
    def _extract_flashcards(self, text: str) -> List[Dict[str, str]]:
        """
        Extract Q/A flashcard pairs from the extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            List of flashcard dictionaries with question and answer
        """
        flashcards = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for question pattern (Q:, Question:, etc.)
            if self._is_question_line(line):
                question = self._clean_question_text(line)
                
                # Look for the corresponding answer in the next few lines
                answer = self._find_answer(lines, i + 1)
                
                if question and answer:
                    flashcards.append({
                        "question": question,
                        "answer": answer
                    })
                    
                    # Skip lines we've already processed
                    i = self._find_next_question_index(lines, i + 1)
                else:
                    i += 1
            else:
                i += 1
        
        return flashcards
    
    def _is_question_line(self, line: str) -> bool:
        """Check if a line contains a question marker."""
        question_patterns = [
            r'^Q\s*:',           # Q:
            r'^Question\s*:',    # Question:
            r'^Q\d+\s*[.:]',     # Q1., Q2:, etc.
            r'^\d+\s*\.\s*',     # 1. 2. etc.
            r'^\?\s*',           # Starting with ?
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        # Also check if line ends with question mark
        return line.rstrip().endswith('?')
    
    def _clean_question_text(self, line: str) -> str:
        """Clean question text by removing markers."""
        # Remove common question prefixes
        cleaned = re.sub(r'^(Q\s*:|Question\s*:|Q\d+\s*[.:|\d+\s*\.\s*)', '', line, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _find_answer(self, lines: List[str], start_index: int) -> str:
        """Find the answer starting from the given index."""
        answer_parts = []
        
        for i in range(start_index, min(start_index + 5, len(lines))):  # Look ahead max 5 lines
            if i >= len(lines):
                break
                
            line = lines[i].strip()
            
            # Stop if we hit another question
            if self._is_question_line(line):
                break
            
            # Check for answer markers
            if self._is_answer_line(line):
                # Clean the answer text
                cleaned_answer = self._clean_answer_text(line)
                if cleaned_answer:
                    answer_parts.append(cleaned_answer)
                
                # Continue collecting multi-line answers
                for j in range(i + 1, min(i + 3, len(lines))):
                    if j >= len(lines):
                        break
                    next_line = lines[j].strip()
                    if next_line and not self._is_question_line(next_line) and not self._is_answer_line(next_line):
                        answer_parts.append(next_line)
                    else:
                        break
                break
            
            # If no explicit answer marker, treat non-empty line as potential answer
            elif line and not self._is_question_line(line):
                answer_parts.append(line)
        
        return ' '.join(answer_parts).strip()
    
    def _is_answer_line(self, line: str) -> bool:
        """Check if a line contains an answer marker."""
        answer_patterns = [
            r'^A\s*:',           # A:
            r'^Answer\s*:',      # Answer:
            r'^Ans\s*:',         # Ans:
            r'^A\d+\s*[.:]',     # A1., A2:, etc.
        ]
        
        for pattern in answer_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _clean_answer_text(self, line: str) -> str:
        """Clean answer text by removing markers."""
        cleaned = re.sub(r'^(A\s*:|Answer\s*:|Ans\s*:|A\d+\s*[.:])', '', line, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _find_next_question_index(self, lines: List[str], start_index: int) -> int:
        """Find the index of the next question line."""
        for i in range(start_index, len(lines)):
            if self._is_question_line(lines[i]):
                return i
        return len(lines)  # No more questions found
