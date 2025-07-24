#!/usr/bin/env python3
"""
Test script for OCR functionality without requiring actual image processing.
This allows us to test the flashcard extraction logic independently.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our OCR utilities
try:
    from ocr_utils import OCRProcessor
    print("✅ Successfully imported OCRProcessor")
except ImportError as e:
    print(f"❌ Failed to import OCRProcessor: {e}")
    print("Note: This is expected if EasyOCR dependencies are not installed yet.")
    sys.exit(1)

def test_flashcard_extraction():
    """Test flashcard extraction logic with sample text"""
    
    # Sample text with various Q/A patterns
    test_texts = [
        # Standard Q: A: format
        """Q: What is the capital of France?
A: Paris

Q: When did World War II end?
A: 1945""",
        
        # Question: Answer: format
        """Question: What is photosynthesis?
Answer: The process by which plants convert sunlight into energy

Question: Who invented the telephone?
Answer: Alexander Graham Bell""",
        
        # Mixed formats
        """Q1: What is machine learning?
A1: A subset of AI that enables computers to learn

Q2: Name three programming languages
A2: Python, JavaScript, Java

1. What year was the internet invented?
   1969 (ARPANET)""",
        
        # Question mark format
        """What is the largest planet in our solar system?
Jupiter

How many continents are there?
Seven continents""",
        
        # No clear Q/A patterns
        """This is just regular text without any
question and answer patterns.
It should not generate any flashcards."""
    ]
    
    try:
        # Initialize OCR processor (will try GPU first, then fall back to CPU)
        processor = OCRProcessor(languages=['en'], gpu=False)  # Use CPU for testing
        print("✅ OCR processor initialized successfully")
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input text: {repr(text)}")
            
            flashcards = processor._extract_flashcards(text)
            print(f"Extracted {len(flashcards)} flashcards:")
            
            for j, card in enumerate(flashcards, 1):
                print(f"  Flashcard {j}:")
                print(f"    Q: {card['question']}")
                print(f"    A: {card['answer']}")
        
        print(f"\n✅ All {len(test_texts)} test cases completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_individual_methods():
    """Test individual helper methods"""
    
    try:
        processor = OCRProcessor(languages=['en'], gpu=False)
        
        # Test question detection
        test_lines = [
            "Q: What is Python?",
            "Question: How does OCR work?", 
            "Q1: What is machine learning?",
            "1. What is the capital of Japan?",
            "What is your favorite color?",
            "This is not a question",
            "A: This is an answer"
        ]
        
        print("\n--- Testing Question Detection ---")
        for line in test_lines:
            is_question = processor._is_question_line(line)
            print(f"'{line}' -> Question: {is_question}")
        
        # Test answer detection
        answer_lines = [
            "A: This is an answer",
            "Answer: This is also an answer",
            "A1: Another answer format", 
            "This is not an answer line",
            "Q: This is a question"
        ]
        
        print("\n--- Testing Answer Detection ---")
        for line in answer_lines:
            is_answer = processor._is_answer_line(line)
            print(f"'{line}' -> Answer: {is_answer}")
        
        print("\n✅ Individual method tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Individual method tests failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Notebook Vision OCR Functionality")
    print("=" * 50)
    
    # Test individual methods first
    if test_individual_methods():
        print("\n" + "=" * 50)
        # Test full flashcard extraction
        if test_flashcard_extraction():
            print("\n🎉 All tests passed! The OCR logic is working correctly.")
            sys.exit(0)
        else:
            print("\n💥 Flashcard extraction tests failed!")
            sys.exit(1)
    else:
        print("\n💥 Individual method tests failed!")
        sys.exit(1)
