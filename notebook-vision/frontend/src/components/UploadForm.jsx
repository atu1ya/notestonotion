import React, { useState, useRef } from 'react'
import './UploadForm.css'

const UploadForm = ({ onSuccess, onError, onLoadingChange, isLoading }) => {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [semanticMode, setSemanticMode] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [showCamera, setShowCamera] = useState(false)
  const [cameraStream, setCameraStream] = useState(null)
  const videoRef = useRef(null)
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
    setPreviewUrl(URL.createObjectURL(file))
  }

  // Camera capture logic
  const handleTakePhotoClick = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        setCameraStream(stream)
        setShowCamera(true)
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      } catch (err) {
        onError('Unable to access camera: ' + err.message)
      }
    } else {
      onError('Camera not supported on this device/browser.')
    }
  }

  const handleCapturePhoto = () => {
    if (!videoRef.current) return
    const video = videoRef.current
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(blob => {
      if (blob) {
        const file = new File([blob], 'captured_photo.jpg', { type: 'image/jpeg' })
        setSelectedFile(file)
        setPreviewUrl(URL.createObjectURL(blob))
        stopCamera()
      }
    }, 'image/jpeg', 0.95)
  }

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop())
      setCameraStream(null)
    }
    setShowCamera(false)
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

      const endpoint = semanticMode ? '/api/upload/semantic/' : '/api/upload/'
      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      if (data.success) {
        onSuccess(data, semanticMode)
        setSelectedFile(null) // Clear selected file after successful upload
        setPreviewUrl(null)
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
    setPreviewUrl(null)
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
        onClick={!selectedFile && !showCamera ? handleBrowseClick : undefined}
      >
        {/* File input for both upload and mobile camera */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileInputChange}
          className="file-input"
          disabled={isLoading}
        />

        {/* Camera interface (desktop) */}
        {showCamera && (
          <div className="camera-modal">
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', maxHeight: 320 }} />
            <div className="camera-actions">
              <button onClick={handleCapturePhoto} disabled={isLoading}>📸 Capture</button>
              <button onClick={stopCamera} disabled={isLoading}>Cancel</button>
            </div>
          </div>
        )}

        {/* Preview selected or captured image */}
        {previewUrl && selectedFile && !showCamera ? (
          <div className="image-preview">
            <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: 240, borderRadius: 8 }} />
            <button onClick={clearSelection} className="remove-file-btn" disabled={isLoading}>✕</button>
          </div>
        ) : !selectedFile && !showCamera ? (
          <div className="upload-prompt">
            <div className="upload-icon">📁</div>
            <h3>Upload or Capture a Photo of Your Notes</h3>
            <p>Drag and drop, browse, or use your camera</p>
            <p className="file-info">
              Supported: JPEG, PNG, BMP, TIFF (max 10MB)
            </p>
            <button type="button" className="camera-btn" onClick={handleTakePhotoClick} disabled={isLoading}>
              📷 Take Photo
            </button>
          </div>
        ) : null}
      </div>

      {selectedFile && !showCamera && (
        <div className="upload-actions">
          <label className="semantic-toggle">
            <input
              type="checkbox"
              checked={semanticMode}
              onChange={e => setSemanticMode(e.target.checked)}
              disabled={isLoading}
            />
            <span>AI Semantic Extraction (beta)</span>
          </label>
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
                {semanticMode ? '🤖 Semantic Extract' : '🚀 Extract Text & Flashcards'}
              </>
            )}
          </button>
          <button 
            onClick={clearSelection}
            disabled={isLoading}
            className="cancel-btn"
          >
            Retake / Cancel
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
