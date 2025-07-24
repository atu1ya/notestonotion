import React, { useState, useRef } from 'react'
import './UploadForm.css'

const UploadForm = ({ onSuccess, onError, onLoadingChange, isLoading }) => {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const BACKEND_URL = 'http://localhost:8000'

  const handleFileSelect = (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
    if (!allowedTypes.includes(file.type)) {
      onError('Please select a valid image file (JPEG, PNG, BMP, TIFF)')
      return
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      onError('File size too large. Maximum size is 10MB.')
      return
    }

    setSelectedFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInputChange = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      onError('Please select a file first')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      onLoadingChange(true)
      onError('') // Clear any previous errors

      const response = await fetch(`${BACKEND_URL}/api/upload/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        onSuccess(data)
        setSelectedFile(null) // Clear selected file after successful upload
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } else {
        throw new Error(data.error || 'Upload failed')
      }

    } catch (error) {
      console.error('Upload error:', error)
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        onError('Cannot connect to server. Please make sure the backend is running on http://localhost:8000')
      } else {
        onError(error.message || 'An error occurred during upload')
      }
    } finally {
      onLoadingChange(false)
    }
  }

  const clearSelection = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="upload-form">
      <div 
        className={`upload-area ${dragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!selectedFile ? handleBrowseClick : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="file-input"
          disabled={isLoading}
        />

        {!selectedFile ? (
          <div className="upload-prompt">
            <div className="upload-icon">📁</div>
            <h3>Upload Your Handwritten Notes</h3>
            <p>Drag and drop an image here, or click to browse</p>
            <p className="file-info">
              Supported formats: JPEG, PNG, BMP, TIFF (max 10MB)
            </p>
          </div>
        ) : (
          <div className="file-selected">
            <div className="file-icon">📄</div>
            <div className="file-details">
              <h4>{selectedFile.name}</h4>
              <p>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation()
                clearSelection()
              }}
              className="remove-file-btn"
              disabled={isLoading}
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="upload-actions">
          <button 
            onClick={handleUpload}
            disabled={isLoading}
            className="upload-btn"
          >
            {isLoading ? (
              <>
                <span className="btn-spinner"></span>
                Processing...
              </>
            ) : (
              <>
                🚀 Extract Text & Flashcards
              </>
            )}
          </button>
          
          <button 
            onClick={clearSelection}
            disabled={isLoading}
            className="cancel-btn"
          >
            Cancel
          </button>
        </div>
      )}

      <div className="upload-tips">
        <h4>💡 Tips for better results:</h4>
        <ul>
          <li>Ensure good lighting and clear handwriting</li>
          <li>Format questions as "Q:" and answers as "A:"</li>
          <li>Keep text horizontal and avoid skewed images</li>
          <li>Use high-resolution images for better OCR accuracy</li>
        </ul>
      </div>
    </div>
  )
}

export default UploadForm
