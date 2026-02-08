import { useState, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import PipelineVisualizer from '../components/PipelineVisualizer'
import ResultsTable from '../components/ResultsTable'
import colors from '../styles/colors'
import axios from 'axios'

function AnalysisPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const tableRef = useRef(null)
  
  const [analysisResults, setAnalysisResults] = useState(location.state?.results || null)
  const [filterJointNumber, setFilterJointNumber] = useState(null)
  const [testMode] = useState(location.state?.testMode || false)

  // Redirect if no results
  if (!analysisResults) {
    navigate('/new-analysis')
    return null
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

  const handleNewAnalysis = () => {
    navigate('/new-analysis')
  }

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: colors.background.page }}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: colors.text.primary }}>
              Analysis Results
            </h1>
            {testMode && (
              <p className="text-sm mt-1" style={{ color: colors.test.button }}>
                Test Mode - Using sample data
              </p>
            )}
          </div>
          <button
            onClick={handleNewAnalysis}
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
    </div>
  )
}

export default AnalysisPage
