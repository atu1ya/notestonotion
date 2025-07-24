# 🧪 Test Samples for Notebook Vision

## Sample Handwritten Note Formats

To test the OCR and flashcard generation, create handwritten notes with these patterns:

### Format 1: Q: and A: 
```
Q: What is the capital of France?
A: Paris

Q: When did World War II end?
A: 1945

Q: What is the largest ocean?
A: Pacific Ocean
```

### Format 2: Question: and Answer:
```
Question: What is photosynthesis?
Answer: The process by which plants convert sunlight into energy

Question: Who invented the telephone?
Answer: Alexander Graham Bell

Question: What is the speed of light?
Answer: 299,792,458 meters per second
```

### Format 3: Numbered Questions
```
1. What is machine learning?
   A subset of AI that enables computers to learn without explicit programming

2. Name three programming languages
   Python, JavaScript, Java

3. What year was the internet invented?
   1969 (ARPANET)
```

### Format 4: Mixed Patterns
```
Q1: What is artificial intelligence?
A1: Technology that enables machines to simulate human intelligence

Question: How many continents are there?
Answer: Seven continents

Q: What is the chemical symbol for gold?
A: Au

3. What is the smallest unit of matter?
   Atom
```

## Testing Tips

1. **Image Quality**:
   - Use good lighting
   - Keep text horizontal 
   - Ensure clear, legible handwriting
   - Use dark ink on white/light paper

2. **File Formats**:
   - Test with JPEG, PNG, BMP, TIFF formats
   - Keep file size under 10MB

3. **Expected Results**:
   - Text should be extracted accurately
   - Question/answer pairs should be detected
   - Flashcards should be generated for Q/A patterns

4. **Error Testing**:
   - Try uploading non-image files (should fail)
   - Try very large files (should fail)
   - Try images without Q/A patterns (should extract text but no flashcards)

## Sample Test Cases

### Test Case 1: Perfect Q/A Format
Create a note with clear Q: and A: patterns. Expected: Multiple flashcards generated.

### Test Case 2: Mixed Formats  
Create a note mixing different question formats. Expected: All patterns detected.

### Test Case 3: Poor Handwriting
Create a note with unclear handwriting. Expected: Some text extracted, possible OCR errors.

### Test Case 4: No Q/A Patterns
Create a note with just regular text. Expected: Text extracted, no flashcards.

### Test Case 5: Complex Layout
Create a note with diagrams, equations, and Q/A. Expected: Text and Q/A extracted, diagrams ignored.

## Manual Testing Checklist

- [ ] Upload functionality works
- [ ] Drag and drop works  
- [ ] File validation works (rejects non-images)
- [ ] Size validation works (rejects >10MB)
- [ ] OCR extracts text correctly
- [ ] Flashcard detection works
- [ ] Error handling works
- [ ] UI is responsive on mobile
- [ ] Both backend and frontend start correctly
- [ ] API endpoints respond correctly
