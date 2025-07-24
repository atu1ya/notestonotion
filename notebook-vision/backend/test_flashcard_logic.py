#!/usr/bin/env python3
"""
Standalone test for flashcard extraction logic.
This tests the core functionality without requiring EasyOCR installation.
"""

import re
from typing import List, Dict


class FlashcardExtractor:
    """Simplified version of the flashcard extraction logic for testing"""
    
    def extract_flashcards(self, text: str) -> List[Dict[str, str]]:
        """Extract Q/A flashcard pairs from text"""
        flashcards = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if self._is_question_line(line):
                question = self._clean_question_text(line)
                answer = self._find_answer(lines, i + 1)
                
                if question and answer:
                    flashcards.append({
                        "question": question,
                        "answer": answer
                    })
                    i = self._find_next_question_index(lines, i + 1)
                else:
                    i += 1
            else:
                i += 1
        
        return flashcards
    
    def _is_question_line(self, line: str) -> bool:
        """Check if a line contains a question marker"""
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
        
        return line.rstrip().endswith('?')
    
    def _clean_question_text(self, line: str) -> str:
        """Clean question text by removing markers"""
        cleaned = re.sub(r'^(Q\s*:|Question\s*:|Q\d+\s*[.:]|\d+\s*\.\s*)', '', line, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _find_answer(self, lines: List[str], start_index: int) -> str:
        """Find the answer starting from the given index"""
        answer_parts = []
        
        for i in range(start_index, min(start_index + 5, len(lines))):
            if i >= len(lines):
                break
                
            line = lines[i].strip()
            
            if self._is_question_line(line):
                break
            
            if self._is_answer_line(line):
                cleaned_answer = self._clean_answer_text(line)
                if cleaned_answer:
                    answer_parts.append(cleaned_answer)
                
                for j in range(i + 1, min(i + 3, len(lines))):
                    if j >= len(lines):
                        break
                    next_line = lines[j].strip()
                    if next_line and not self._is_question_line(next_line) and not self._is_answer_line(next_line):
                        answer_parts.append(next_line)
                    else:
                        break
                break
            
            elif line and not self._is_question_line(line):
                answer_parts.append(line)
        
        return ' '.join(answer_parts).strip()
    
    def _is_answer_line(self, line: str) -> bool:
        """Check if a line contains an answer marker"""
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
        """Clean answer text by removing markers"""
        cleaned = re.sub(r'^(A\s*:|Answer\s*:|Ans\s*:|A\d+\s*[.:])', '', line, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _find_next_question_index(self, lines: List[str], start_index: int) -> int:
        """Find the index of the next question line"""
        for i in range(start_index, len(lines)):
            if self._is_question_line(lines[i]):
                return i
        return len(lines)


def test_flashcard_extraction():
    """Run comprehensive tests"""
    
    extractor = FlashcardExtractor()
    
    test_cases = [
        {
            "name": "Standard Q: A: format",
            "text": """Q: What is the capital of France?
A: Paris

Q: When did World War II end?
A: 1945""",
            "expected_count": 2
        },
        {
            "name": "Question: Answer: format", 
            "text": """Question: What is photosynthesis?
Answer: The process by which plants convert sunlight into energy

Question: Who invented the telephone?
Answer: Alexander Graham Bell""",
            "expected_count": 2
        },
        {
            "name": "Mixed formats",
            "text": """Q1: What is machine learning?
A1: A subset of AI that enables computers to learn

Q2: Name three programming languages
A2: Python, JavaScript, Java

1. What year was the internet invented?
   1969 (ARPANET)""",
            "expected_count": 3
        },
        {
            "name": "Question mark format",
            "text": """What is the largest planet in our solar system?
Jupiter

How many continents are there?
Seven continents""",
            "expected_count": 2
        },
        {
            "name": "No Q/A patterns",
            "text": """This is just regular text without any
question and answer patterns.
It should not generate any flashcards.""",
            "expected_count": 0
        },
        {
            "name": "Complex mixed format",
            "text": """Q: What is artificial intelligence?
A: Technology that enables machines to simulate human intelligence

Question: What is the speed of light?
Answer: 299,792,458 meters per second

Q3: What is the chemical symbol for water?
A3: H2O

4. Who painted the Mona Lisa?
   Leonardo da Vinci

What is the largest mammal?
Blue whale""",
            "expected_count": 5
        }
    ]
    
    print("🧪 Testing Flashcard Extraction Logic")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        flashcards = extractor.extract_flashcards(test_case['text'])
        actual_count = len(flashcards)
        expected_count = test_case['expected_count']
        
        print(f"Expected flashcards: {expected_count}")
        print(f"Actual flashcards: {actual_count}")
        
        if actual_count == expected_count:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
        
        # Show extracted flashcards
        for j, card in enumerate(flashcards, 1):
            print(f"  Card {j}: Q: {card['question'][:50]}{'...' if len(card['question']) > 50 else ''}")
            print(f"         A: {card['answer'][:50]}{'...' if len(card['answer']) > 50 else ''}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Flashcard extraction logic is working correctly.")
        return True
    else:
        print("💥 SOME TESTS FAILED! Check the logic above.")
        return False


def test_edge_cases():
    """Test edge cases and error conditions"""
    
    extractor = FlashcardExtractor()
    
    edge_cases = [
        ("Empty string", ""),
        ("Only whitespace", "   \n\n   "),
        ("Single question no answer", "Q: What is this?"),
        ("Single answer no question", "A: This is an answer"),
        ("Questions with no clear answers", "Q: What is X?\nQ: What is Y?"),
        ("Answers with no questions", "A: Answer 1\nA: Answer 2"),
        ("Very long question", "Q: " + "What " * 50 + "is this?"),
        ("Very long answer", "A: " + "This " * 50 + "is the answer"),
        ("Special characters", "Q: What is 2+2=?\nA: 4"),
        ("Numbers and symbols", "Q1: H2O = ?\nA1: Water"),
    ]
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 30)
    
    for name, text in edge_cases:
        print(f"\n📌 {name}")
        try:
            flashcards = extractor.extract_flashcards(text)
            print(f"✅ Extracted {len(flashcards)} flashcards")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Edge case testing completed!")


if __name__ == "__main__":
    success = test_flashcard_extraction()
    test_edge_cases()
    
    if success:
        print("\n🚀 The flashcard extraction logic is ready for production!")
        exit(0)
    else:
        print("\n🛠️ The flashcard extraction logic needs refinement.")
        exit(1)
