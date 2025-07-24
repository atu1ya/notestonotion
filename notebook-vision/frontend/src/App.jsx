import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import './App.css'

function App() {
  const [extractedText, setExtractedText] = useState('')
  const [flashcards, setFlashcards] = useState([])
  const [semanticFlashcards, setSemanticFlashcards] = useState([])
  const [isSemantic, setIsSemantic] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')
  const [noteText, setNoteText] = useState('')
  const [questions, setQuestions] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleUploadSuccess = (data, semanticMode) => {
    setExtractedText(data.extracted_text)
    setFileName(data.filename)
    setError('')
    setIsSemantic(!!semanticMode)
    if (semanticMode) {
      setSemanticFlashcards(Array.isArray(data.semantic_flashcards) ? data.semantic_flashcards : [])
      setFlashcards([])
    } else {
      setFlashcards(Array.isArray(data.flashcards) ? data.flashcards : [])
      setSemanticFlashcards([])
    }
  }

  const handleUploadError = (errorMessage) => {
    setError(errorMessage)
    setExtractedText('')
    setFlashcards([])
    setFileName('')
    setSemanticFlashcards([])
  }

  const handleLoadingChange = (loading) => {
    setIsLoading(loading)
  }

  const clearResults = () => {
    setExtractedText('')
    setFlashcards([])
    setSemanticFlashcards([])
    setError('')
    setFileName('')
    setIsSemantic(false)
  }

  const handleGenerateQuestions = async () => {
    if (!noteText.trim()) return
    setIsGenerating(true)
    setQuestions([])
    try {
      const response = await fetch('http://localhost:8000/api/generate-questions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: noteText })
      })
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to generate questions')
      }
      const data = await response.json()
      setQuestions(Array.isArray(data.questions) ? data.questions : [])
    } catch (err) {
      setQuestions([])
      setError(err.message)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>📖 Notebook Vision</h1>
        <p>Transform your handwritten notes into digital flashcards and AI-generated questions</p>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <UploadForm 
            onSuccess={handleUploadSuccess}
            onError={handleUploadError}
            onLoadingChange={handleLoadingChange}
            isLoading={isLoading}
          />
        </div>

        {/* Paste or upload plain text for question generation */}
        <div className="text-question-section">
          <h2>📝 Paste Notes or Text</h2>
          <textarea
            value={noteText}
            onChange={e => setNoteText(e.target.value)}
            placeholder="Paste your notes here (from Notion, etc.)"
            rows={8}
            style={{ width: '100%', maxWidth: 600, marginBottom: 8 }}
            disabled={isGenerating}
          />
          <button
            onClick={handleGenerateQuestions}
            disabled={isGenerating || !noteText.trim()}
            className="generate-btn"
          >
            {isGenerating ? 'Generating...' : 'Generate Questions with AI'}
          </button>
        </div>

        {/* Display generated questions grouped by type */}
        {questions.length > 0 && (
          <div className="questions-section">
            <h2>🤖 AI-Generated Questions</h2>
            {['basic', 'intermediate', 'advanced', 'math'].map(type => (
              <div key={type} className="question-group">
                <h3>{type.charAt(0).toUpperCase() + type.slice(1)} Questions</h3>
                <ul>
                  {questions.filter(q => q.type === type).map((q, idx) => (
                    <li key={idx}>{q.question}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

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

            {isSemantic && semanticFlashcards.length > 0 && (
              <div className="flashcards-section">
                <h2>🤖 Semantic Flashcards ({semanticFlashcards.length})</h2>
                <div className="flashcards-grid">
                  {semanticFlashcards.map((card, index) => (
                    <div key={index} className="flashcard">
                      <div className="flashcard-type-label">{card.type ? card.type : 'semantic'}</div>
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

            {!isSemantic && flashcards.length > 0 && (
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

            {((!isSemantic && flashcards.length === 0) || (isSemantic && semanticFlashcards.length === 0)) && (
              <div className="no-flashcards">
                <h3>💡 No flashcards detected</h3>
                <p>
                  To create flashcards, try formatting your notes with clear Q: and A: patterns, like:
                </p>
                <div className="example-format">
                  <pre>{`Q: What is the capital of France?\nA: Paris\n\nQuestion: What year did World War II end?\nAnswer: 1945`}</pre>
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
