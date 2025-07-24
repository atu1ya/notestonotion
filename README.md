# � Notebook Vision - AI-Powered OCR Flashcard Generator

Transform your handwritten notes into digital flashcards with AI-powered OCR technology. Notebook Vision uses EasyOCR to extract text from images of handwritten notes and automatically generates flashcards from Q/A patterns.

![Notebook Vision Demo](https://via.placeholder.com/800x400/667eea/white?text=Notebook+Vision+Demo)

## ✨ Features

- 📱 Drag & Drop Upload: Easy image upload interface
- **🤖 AI-Powered OCR**: Uses EasyOCR for accurate handwriting recognition
- **🎯 Smart Flashcard Generation**: Automatically detects Q/A patterns and creates flashcards
- **📝 Text Extraction**: Extract all text from handwritten notes
- **💻 Modern UI**: Clean, responsive React interface
- **⚡ Fast Processing**: Optimized for quick OCR processing
- **🔧 Multiple Formats**: Supports JPEG, PNG, BMP, TIFF image formats

## 🏗️ Architecture

```
notebook-vision/
├── backend/                 # FastAPI Python backend
│   ├── main.py             # FastAPI application
│   ├── ocr_utils.py        # OCR processing utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── App.css         # Global styles
│   │   ├── main.jsx        # React entry point
│   │   └── components/
│   │       ├── UploadForm.jsx    # File upload component
│   │       └── UploadForm.css    # Upload form styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (backend)
- **Node.js 16+** (for frontend)
- **Git** (for cloning)

### 🔧 Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd notebook-vision
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 🏃‍♂️ Running the Application

#### Start the Backend (Terminal 1)

```bash
cd backend
# Make sure virtual environment is activated
python main.py
```

The backend will start on: **http://localhost:8000**

You can verify it's running by visiting: http://localhost:8000 (should show API status)

#### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend will start on: **http://localhost:3000**

### 🎯 Usage

1. **Open the Application**: Navigate to http://localhost:3000 in your browser
2. **Upload an Image**: 
   - Drag and drop an image of handwritten notes, or
   - Click the upload area to browse and select a file
3. **Wait for Processing**: The OCR will extract text from your image
4. **View Results**: 
   - See the extracted text in the "Extracted Text" section
   - View auto-generated flashcards in the "Generated Flashcards" section

### 📝 Flashcard Format Tips

For best flashcard generation results, format your handwritten notes with clear Q/A patterns:

```
Q: What is the capital of France?
A: Paris

Question: When did World War II end?
Answer: 1945

Q1: What is photosynthesis?
A1: The process by which plants convert sunlight into energy
```

Supported question/answer patterns:

## 🔧 Configuration

### Backend Configuration

The backend can be configured by modifying `backend/main.py`:


### Frontend Configuration

The frontend configuration is in `frontend/vite.config.js`:


## 🛠️ Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python main.py

# Run tests (if implemented)
pytest

# Type checking
mypy main.py ocr_utils.py
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 📋 API Endpoints

### Backend API


### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Upload image
curl -X POST \
  -F "file=@your-image.jpg" \
  http://localhost:8000/api/upload/
```

## 🧪 Testing

### Manual Testing

1. **Test Different Image Formats**: Try uploading JPEG, PNG, BMP, and TIFF files
2. **Test Handwriting Styles**: Upload images with different handwriting styles
3. **Test Q/A Patterns**: Try different question/answer formats
4. **Test Error Handling**: Upload invalid files or very large files
5. **Test Mobile Responsiveness**: Use the application on mobile devices

### Sample Test Images

Create handwritten notes with these patterns to test:

```
Q: What is machine learning?
A: A subset of AI that enables computers to learn without explicit programming

Question: Name three programming languages
Answer: Python, JavaScript, Java

1. What year was the internet invented?
   1969 (ARPANET)

2. Who invented the World Wide Web?
   Tim Berners-Lee
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.9+

# Check if virtual environment is activated
which python  # Should point to venv

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 16+

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### OCR Not Working

1. **GPU Issues**: If you have GPU problems, the app will automatically fall back to CPU
2. **Memory Issues**: Large images may cause memory issues. Try resizing images to < 2MB
3. **Dependencies**: Ensure all Python packages are installed correctly

#### CORS Errors

If you see CORS errors in the browser console:

1. Check that the backend is running on port 8000
2. Ensure the frontend is connecting to the correct backend URL
3. Verify CORS settings in `main.py`

#### Poor OCR Results

1. **Image Quality**: Use high-resolution, well-lit images
2. **Handwriting**: Ensure clear, legible handwriting
3. **Format**: Keep text horizontal and avoid skewed images
4. **Language**: Ensure correct language settings in OCRProcessor

### Getting Help

1. **Check Logs**: Look at console output for both backend and frontend
2. **Browser Console**: Check browser developer tools for frontend errors
3. **API Testing**: Test API endpoints directly with curl or Postman
4. **Dependencies**: Verify all dependencies are correctly installed

## 🔒 Security Considerations


## 🚀 Deployment

### Production Deployment

#### Backend Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Deployment

```bash
# Build for production
npm run build

# Serve static files
npx serve -s dist
```

#### Docker Deployment (Optional)

Create Dockerfile for backend:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments


## 📈 Roadmap



**Made with ❤️ using React, FastAPI, and EasyOCR**
