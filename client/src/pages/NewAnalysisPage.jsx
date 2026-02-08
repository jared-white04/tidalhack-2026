import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import colors from '../styles/colors'
import axios from 'axios'

function NewAnalysisPage() {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const navigate = useNavigate()

  const handleFilesUploaded = (files) => {
    setUploadedFiles(prev => [...prev, ...files])
  }

  const handleRemoveFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true)
    try {
      const formData = new FormData()
      uploadedFiles.forEach(file => {
        formData.append('files', file)
      })

      const response = await axios.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      // Navigate to analysis page with results
      navigate('/analysis', { state: { results: response.data.results } })
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
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
