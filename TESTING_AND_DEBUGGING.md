# Testing and Debugging Guide for Notebook Vision

This guide will help you test and debug the Notebook Vision app (FastAPI backend + React frontend) so you can pick up development or troubleshooting at any time.

---

## 1. Prerequisites
- Python 3.9+
- Node.js 18+
- All dependencies installed:
  - Backend: `pip install -r backend/requirements.txt`
  - Frontend: `npm install` in the frontend directory
- Ensure OCR and NLP models are downloaded (EasyOCR, spaCy)

---

## 2. Running the App

### Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```
- The API will be available at: http://localhost:8000
- Check logs for OCR/NLP errors or missing models.

### Frontend (React)
```bash
cd frontend
npm run dev
```
- The app will be available at: http://localhost:5173 (or as shown in terminal)

---

## 3. Manual Testing

### Uploading Notes
- Use the upload form to select or drag-and-drop an image (JPEG, PNG, BMP, TIFF, max 10MB).
- Try the camera capture feature (desktop/mobile).
- Toggle "AI Semantic Extraction" for advanced flashcard extraction.
- Check for errors: invalid file type, size, or server connection.

### Reviewing Results
- Confirm extracted text and flashcards are displayed.
- Try uploading handwritten and printed notes.
- Use the question generator and review AI-generated questions.

### Flashcard Management
- Create, rename, and delete decks.
- Add, tag, and untag flashcards.
- Use search/filter features.
- Test self-assessment and progress tracking.

---

## 4. Debugging

### Backend
- Check terminal logs for errors (OCR, spaCy, FastAPI exceptions).
- Use `/health` and `/` endpoints to verify server status.
- Test API endpoints directly with curl or Postman (see OpenAPI docs at http://localhost:8000/docs).
- If OCR or NLP fails, ensure models are installed and GPU is available (if configured).

### Frontend
- Use browser dev tools (Console, Network tab) to debug API calls and UI errors.
- Check for CORS issues or failed requests.
- Review error messages shown in the UI.

---

## 5. Automated Testing (Optional)
- Add unit tests for backend utilities (pytest recommended).
- Add integration tests for API endpoints (FastAPI's TestClient).
- For frontend, use React Testing Library or Cypress for UI tests.

---

## 6. Common Issues
- **Cannot connect to backend:** Ensure FastAPI is running on port 8000.
- **OCR errors:** Check EasyOCR and Pillow installation, and that language models are present.
- **NLP errors:** Run `python -m spacy download en_core_web_sm` if spaCy model is missing.
- **CORS errors:** Ensure CORS middleware is enabled in FastAPI.
- **File upload fails:** Check file type/size and backend logs.

---

## 7. Useful Commands

### Install spaCy English Model
```bash
python -m spacy download en_core_web_sm
```

### Run Backend Tests
```bash
pytest backend/
```

### Run Frontend Tests
```bash
npm test
```

---

## 8. Further Debugging
- Add print/log statements in backend endpoints for deeper inspection.
- Use `console.log` in React components to trace UI state.
- If using Docker, check container logs and port mappings.

---

## 9. Getting Help
- Check FastAPI, React, EasyOCR, and spaCy documentation for troubleshooting tips.
- Search error messages on Stack Overflow or GitHub Issues.

---

**Happy hacking!**
