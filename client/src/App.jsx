import { useState } from 'react'
import React from 'react'
import FileUpload from './components/FileUpload'
import ResultsTable from './components/ResultsTable'
import PipelineVisualizer from './components/PipelineVisualizer'
import axios from 'axios'
import colors from './styles/colors'

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [analysisResults, setAnalysisResults] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [filterJointNumber, setFilterJointNumber] = useState(null)
  const [testMode, setTestMode] = useState(false)
  const tableRef = React.useRef(null)

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
      
      setAnalysisResults(response.data.results)
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleMarkViewed = async (anomalyNumber) => {
    if (testMode) {
      setAnalysisResults(prev => 
        prev.map(row => 
          row.anomalyNumber === anomalyNumber 
            ? { ...row, viewed: row.viewed === 'Y' ? 'N' : 'Y' }
            : row
        )
      )
      return
    }

    try {
      await axios.patch(`/api/anomaly/${anomalyNumber}/viewed`)
      setAnalysisResults(prev => 
        prev.map(row => 
          row.anomalyNumber === anomalyNumber 
            ? { ...row, viewed: row.viewed === 'Y' ? 'N' : 'Y' }
            : row
        )
      )
    } catch (error) {
      console.error('Failed to mark as viewed:', error)
    }
  }

  const handleSegmentClick = (segmentNumber) => {
    setFilterJointNumber(segmentNumber)
    setTimeout(() => {
      tableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }

  const handleClearFilter = () => {
    setFilterJointNumber(null)
  }

  const loadTestData = async () => {
    try {
      const response = await fetch('/test-data.json')
      const testData = await response.json()
      setAnalysisResults(testData)
      setTestMode(true)
    } catch (error) {
      console.error('Failed to load test data:', error)
      alert('Failed to load test data')
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.background.page }}>
      <header className="text-white py-6 shadow-lg" style={{ backgroundColor: colors.background.header }}>
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Pipeline Data Analysis</h1>
            <p className="mt-1" style={{ color: colors.text.white, opacity: 0.9 }}>
              Upload CSV files and analyze pipeline anomalies
            </p>
          </div>
          {!analysisResults && (
            <button
              onClick={loadTestData}
              className="font-semibold py-2 px-4 rounded-lg transition-colors"
              style={{ 
                backgroundColor: colors.test.button,
                color: colors.test.text
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = colors.test.buttonHover}
              onMouseLeave={(e) => e.target.style.backgroundColor = colors.test.button}
            >
              Load Test Data
            </button>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!analysisResults ? (
          <div className="max-w-4xl mx-auto">
            <FileUpload 
              onFilesUploaded={handleFilesUploaded}
              uploadedFiles={uploadedFiles}
              onRemoveFile={handleRemoveFile}
            />

            {uploadedFiles.length > 0 && (
              <div className="mt-8 text-center">
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
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold" style={{ color: colors.text.primary }}>Analysis Results</h2>
              <button
                onClick={() => {
                  setAnalysisResults(null)
                  setUploadedFiles([])
                }}
                className="font-semibold py-2 px-4 rounded-lg transition-colors"
                style={{ 
                  backgroundColor: colors.button.secondary,
                  color: colors.text.white
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = colors.button.secondaryHover}
                onMouseLeave={(e) => e.target.style.backgroundColor = colors.button.secondary}
              >
                New Analysis
              </button>
            </div>
            
            <div className="mb-8">
              <PipelineVisualizer 
                data={analysisResults}
                onSegmentClick={handleSegmentClick}
              />
            </div>

            <div ref={tableRef}>
              <ResultsTable 
                data={analysisResults}
                onMarkViewed={handleMarkViewed}
                filterJointNumber={filterJointNumber}
                onClearFilter={handleClearFilter}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
