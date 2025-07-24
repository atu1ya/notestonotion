# --- Flashcard Data Model (in-memory for MVP) ---
import uuid
from datetime import datetime

class Deck:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at

class Flashcard:
    def __init__(self, question, answer, deck=None, tags=None):
        self.id = str(uuid.uuid4())
        self.question = question
        self.answer = answer
        self.deck = deck or "Default"
        self.tags = tags or []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.assessment = {"current": None, "history": []}

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "deck": self.deck,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assessment": self.assessment
        }

# In-memory stores (replace with DB in production)
DECKS = {"Default": Deck("Default")}
FLASHCARDS = {}

# --- Deck CRUD ---
def create_deck(name):
    if name in DECKS:
        return None
    deck = Deck(name)
    DECKS[name] = deck
    return deck

def rename_deck(old_name, new_name):
    if old_name not in DECKS or new_name in DECKS:
        return False
    DECKS[new_name] = DECKS.pop(old_name)
    DECKS[new_name].name = new_name
    DECKS[new_name].updated_at = datetime.utcnow().isoformat()
    # Move flashcards
    for fc in FLASHCARDS.values():
        if fc.deck == old_name:
            fc.deck = new_name
    return True

def delete_deck(name):
    if name == "Default" or name not in DECKS:
        return False
    del DECKS[name]
    # Move flashcards to Default
    for fc in FLASHCARDS.values():
        if fc.deck == name:
            fc.deck = "Default"
    return True

# --- Flashcard CRUD/Tag/Assessment ---
def add_flashcard(question, answer, deck="Default", tags=None):
    fc = Flashcard(question, answer, deck, tags)
    FLASHCARDS[fc.id] = fc
    return fc

def tag_flashcard(fc_id, tag):
    fc = FLASHCARDS.get(fc_id)
    if fc and tag not in fc.tags:
        fc.tags.append(tag)
        fc.updated_at = datetime.utcnow().isoformat()
        return True
    return False

def untag_flashcard(fc_id, tag):
    fc = FLASHCARDS.get(fc_id)
    if fc and tag in fc.tags:
        fc.tags.remove(tag)
        fc.updated_at = datetime.utcnow().isoformat()
        return True
    return False

def update_assessment(fc_id, score):
    fc = FLASHCARDS.get(fc_id)
    if fc:
        now = datetime.utcnow().isoformat()
        fc.assessment["current"] = score
        fc.assessment["history"].append({"timestamp": now, "score": score})
        fc.updated_at = now
        return True
    return False

def search_flashcards(query=None, deck=None, tag=None, assessment=None):
    results = list(FLASHCARDS.values())
    if query:
        results = [fc for fc in results if query.lower() in fc.question.lower() or query.lower() in fc.answer.lower()]
    if deck:
        results = [fc for fc in results if fc.deck == deck]
    if tag:
        results = [fc for fc in results if tag in fc.tags]
    if assessment:
        results = [fc for fc in results if fc.assessment["current"] == assessment]
    return [fc.to_dict() for fc in results]
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

# --- Free, Local Semantic Flashcard Extraction ---
def extract_semantic_flashcards(text):
    """
    Extract semantic flashcards using spaCy and regex (no paid LLMs).
    Returns Q/A, definitions, fill-in-the-blanks, and fact pairs.
    """
    import re
    try:
        import spacy
    except ImportError:
        return {"error": "spaCy not installed. Please add 'spacy' to requirements.txt."}
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return {"error": "spaCy English model not installed. Run: python -m spacy download en_core_web_sm"}
    doc = nlp(text)
    flashcards = []
    # Q/A pairs (Q: ... A: ...)
    qa_pattern = re.compile(r"Q[:\.]\s*(.+?)\s*A[:\.]\s*(.+?)(?=\n|$)", re.DOTALL)
    for match in qa_pattern.finditer(text):
        question, answer = match.group(1).strip(), match.group(2).strip()
        if question and answer:
            flashcards.append({"question": question, "answer": answer, "type": "qa"})
    # Definitions (Term: Definition)
    def_pattern = re.compile(r"(.+?):\s*(.+)")
    for match in def_pattern.finditer(text):
        term, definition = match.group(1).strip(), match.group(2).strip()
        if term and definition and len(term.split()) < 6:
            flashcards.append({"question": f"What is {term}?", "answer": definition, "type": "definition"})
    # Fill-in-the-blank (detect sentences with a key entity)
    for sent in doc.sents:
        ents = [ent for ent in sent.ents if ent.label_ in ("PERSON", "ORG", "GPE", "DATE", "EVENT", "WORK_OF_ART")]
        for ent in ents:
            question = sent.text.replace(ent.text, "____")
            answer = ent.text
            if len(answer) > 2 and len(question) > 10:
                flashcards.append({"question": question, "answer": answer, "type": "fill_blank"})
    # Fact pairs (simple SVO extraction)
    for sent in doc.sents:
        subj = None
        obj = None
        verb = None
        for token in sent:
            if token.dep_ == "nsubj":
                subj = token.text
            if token.dep_ == "dobj":
                obj = token.text
            if token.pos_ == "VERB":
                verb = token.text
        if subj and verb and obj:
            question = f"What does {subj} {verb}?"
            answer = obj
            flashcards.append({"question": question, "answer": answer, "type": "fact"})
    # Remove duplicates
    seen = set()
    unique_flashcards = []
    for card in flashcards:
        key = (card["question"].lower(), card["answer"].lower())
        if key not in seen:
            unique_flashcards.append(card)
            seen.add(key)
    return unique_flashcards
    
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
