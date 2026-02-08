import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import colors from '../styles/colors'
import axios from 'axios'

// API base URL - change this if backend is on different port
const API_BASE_URL = 'http://localhost:8000'

function NewAnalysisPage() {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const navigate = useNavigate()

  const handleFilesUploaded = (files) => {
    setUploadedFiles(prev => [...prev, ...files])
    setUploadStatus(null)
  }

  const handleRemoveFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`, { timeout: 3000 })
      return response.data.status === 'healthy'
    } catch (error) {
      return false
    }
  }

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true)
    setUploadStatus(null)
    
    try {
      // Check if backend is running
      const isHealthy = await checkBackendHealth()
      if (!isHealthy) {
        throw new Error('Backend server is not running. Please start the Python API server on port 8000.')
      }

      // First, upload the files
      setUploadStatus('Uploading files...')
      const formData = new FormData()
      uploadedFiles.forEach(file => {
        formData.append('files', file)
      })

      const uploadResponse = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000 // 30 second timeout
      })
      
      console.log('Upload response:', uploadResponse.data)
      
      if (uploadResponse.data.errors && uploadResponse.data.errors.length > 0) {
        alert(`Warning: Some files had issues:\n${uploadResponse.data.errors.join('\n')}`)
      }
      
      // Then run the analysis
      setUploadStatus('Running analysis... This may take a few minutes.')
      const analysisResponse = await axios.post(`${API_BASE_URL}/api/analyze`, {}, {
        timeout: 300000 // 5 minute timeout
      })
      
      console.log('Analysis response:', analysisResponse.data)
      
      // Navigate to analysis page with results
      navigate('/analysis', { 
        state: { 
          results: analysisResponse.data.results,
          testMode: false 
        } 
      })
    } catch (error) {
      console.error('Analysis failed:', error)
      
      let errorMessage = 'Analysis failed. '
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        errorMessage += 'Cannot connect to backend server. Please ensure the Python API is running on port 8000.\n\nTo start the backend:\n1. Open a terminal\n2. cd python-api\n3. python app.py'
      } else if (error.response?.data?.error) {
        errorMessage += error.response.data.error
        if (error.response.data.details) {
          errorMessage += '\n\nDetails: ' + error.response.data.details
        }
      } else {
        errorMessage += error.message || 'Unknown error occurred.'
      }
      
      alert(errorMessage)
      setUploadStatus(null)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const loadTestData = async () => {
    try {
      const response = await fetch('/test-data.json')
      const testData = await response.json()
      navigate('/analysis', { state: { results: testData, testMode: true } })
    } catch (error) {
      console.error('Failed to load test data:', error)
      alert('Failed to load test data')
    }
  }

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: colors.background.page }}>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: colors.text.primary }}>
            Create New Analysis
          </h1>
          <p style={{ color: colors.text.secondary }}>
            Upload your pipeline CSV files to begin analysis
          </p>
        </div>

        <FileUpload 
          onFilesUploaded={handleFilesUploaded}
          uploadedFiles={uploadedFiles}
          onRemoveFile={handleRemoveFile}
        />

        {uploadStatus && (
          <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: colors.status.info + '20', borderLeft: `4px solid ${colors.status.info}` }}>
            <p style={{ color: colors.text.primary }}>{uploadStatus}</p>
          </div>
        )}

        {uploadedFiles.length > 0 && (
          <div className="mt-8 flex gap-4 justify-center">
            <button
              onClick={handleRunAnalysis}
              disabled={isAnalyzing}
              className="font-semibold py-3 px-8 rounded-lg shadow-lg transition-colors text-lg disabled:cursor-not-allowed"
              style={{ 
                backgroundColor: isAnalyzing ? colors.button.disabled : colors.button.primary,
                color: colors.text.white
              }}
              onMouseEnter={(e) => !isAnalyzing && (e.target.style.backgroundColor = colors.button.primaryHover)}
              onMouseLeave={(e) => !isAnalyzing && (e.target.style.backgroundColor = colors.button.primary)}
            >
              {isAnalyzing ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                'Run Analysis'
              )}
            </button>

            <button
              onClick={loadTestData}
              className="font-semibold py-3 px-8 rounded-lg shadow-lg transition-colors text-lg"
              style={{ 
                backgroundColor: colors.test.button,
                color: colors.test.text
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = colors.test.buttonHover}
              onMouseLeave={(e) => e.target.style.backgroundColor = colors.test.button}
            >
              Load Test Data
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default NewAnalysisPage
