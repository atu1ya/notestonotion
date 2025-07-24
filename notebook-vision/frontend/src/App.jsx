import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import './App.css'

function App() {
  const [extractedText, setExtractedText] = useState('')
  const [flashcards, setFlashcards] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')

  const handleUploadSuccess = (data) => {
    setExtractedText(data.extracted_text)
    setFlashcards(data.flashcards)
    setFileName(data.filename)
    setError('')
  }

  const handleUploadError = (errorMessage) => {
    setError(errorMessage)
    setExtractedText('')
    setFlashcards([])
    setFileName('')
  }

  const handleLoadingChange = (loading) => {
    setIsLoading(loading)
  }

  const clearResults = () => {
    setExtractedText('')
    setFlashcards([])
    setError('')
    setFileName('')
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>📖 Notebook Vision</h1>
        <p>Transform your handwritten notes into digital flashcards with AI-powered OCR</p>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <UploadForm 
            onSuccess={handleUploadSuccess}
            onError={handleUploadError}
            onLoadingChange={handleLoadingChange}
            isLoading={isLoading}
          />
          
          {fileName && (
            <div className="file-info">
              <p>📁 Processing: <strong>{fileName}</strong></p>
            </div>
          )}
        </div>

        {error && (
          <div className="error-section">
            <div className="error-message">
              <h3>❌ Error</h3>
              <p>{error}</p>
              <button onClick={clearResults} className="clear-button">
                Clear and Try Again
              </button>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading-section">
            <div className="loading-spinner"></div>
            <p>Processing your image... This may take a few moments.</p>
          </div>
        )}

        {extractedText && !isLoading && (
          <div className="results-section">
            <div className="extracted-text">
              <h2>📝 Extracted Text</h2>
              <div className="text-content">
                <pre>{extractedText}</pre>
              </div>
            </div>

            {flashcards.length > 0 && (
              <div className="flashcards-section">
                <h2>🎯 Generated Flashcards ({flashcards.length})</h2>
                <div className="flashcards-grid">
                  {flashcards.map((card, index) => (
                    <div key={index} className="flashcard">
                      <div className="flashcard-question">
                        <h4>❓ Question</h4>
                        <p>{card.question}</p>
                      </div>
                      <div className="flashcard-answer">
                        <h4>✅ Answer</h4>
                        <p>{card.answer}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {flashcards.length === 0 && (
              <div className="no-flashcards">
                <h3>💡 No flashcards detected</h3>
                <p>
                  To create flashcards, try formatting your notes with clear Q: and A: patterns, like:
                </p>
                <div className="example-format">
                  <pre>{`Q: What is the capital of France?
A: Paris

Question: What year did World War II end?
Answer: 1945`}</pre>
                </div>
              </div>
            )}

            <div className="actions">
              <button onClick={clearResults} className="clear-button">
                🗑️ Clear Results
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built with React + FastAPI + EasyOCR | 
          <a href="https://github.com" target="_blank" rel="noopener noreferrer"> View Source</a>
        </p>
      </footer>
    </div>
  )
}

export default App
