# 🚀 Quick Start Guide

## For Windows Users

1. **Double-click `start.bat`** - This will automatically:
   - Check for Python and Node.js
   - Create virtual environment if needed
   - Install dependencies if needed
   - Start both backend and frontend

2. **Open http://localhost:3000** in your browser

## For Mac/Linux Users

1. **Run the start script**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **Open http://localhost:3000** in your browser

## Manual Setup (if scripts don't work)

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Frontend Setup (in new terminal)
```bash
cd frontend
npm install
npm run dev
```

## Test the Application

1. Upload a handwritten note image (JPEG, PNG, BMP, TIFF)
2. Wait for OCR processing
3. View extracted text and generated flashcards

## Common Issues

- **"Python not found"**: Install Python 3.9+ from python.org
- **"Node not found"**: Install Node.js 16+ from nodejs.org  
- **Backend fails**: Check if port 8000 is available
- **Frontend fails**: Check if port 3000 is available
- **Poor OCR results**: Use clear, well-lit images with good handwriting

## File Format Tips

For best flashcard results, format your notes like this:

```
Q: What is machine learning?
A: A subset of AI that enables computers to learn

Question: Who invented the telephone?
Answer: Alexander Graham Bell

Q1: What is photosynthesis?
A1: Process by which plants convert sunlight to energy
```
