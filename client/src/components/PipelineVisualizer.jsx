import { useState, useMemo } from 'react'
import colors from '../styles/colors'

function PipelineVisualizer({ data, onSegmentClick }) {
  const [currentPage, setCurrentPage] = useState(0)
  const [hoveredSegment, setHoveredSegment] = useState(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const SEGMENTS_PER_PAGE = 100
  const ROWS = 10
  const COLS = 10
  const SEVERE_THRESHOLD = 7

  const segmentData = useMemo(() => {
    // Create segments for every multiple of 10
    const maxJoint = Math.max(...data.map(a => a.jointNumber))
    const numSegments = Math.ceil(maxJoint / 10)
    const segments = {}
    
    // Initialize all segments (multiples of 10)
    for (let i = 0; i <= numSegments; i++) {
      const segmentNumber = i * 10
      segments[segmentNumber] = {
        segmentNumber,
        severe: 0,
        new: 0,
        existing: 0,
        total: 0
      }
    }
    
    // Add anomalies to their corresponding segments
    data.forEach(anomaly => {
      const joint = anomaly.jointNumber
      // Find which segment this joint belongs to (floor to nearest 10)
      const segmentNumber = Math.floor(joint / 10) * 10
      
      if (segments[segmentNumber]) {
        const severity = parseFloat(anomaly.severity)
        const persistence = parseFloat(anomaly.persistence)
        
        if (severity >= SEVERE_THRESHOLD) {
          segments[segmentNumber].severe++
        } else if (persistence === 0) {
          segments[segmentNumber].new++
        } else {
          segments[segmentNumber].existing++
        }
        
        segments[segmentNumber].total++
      }
    })
    
    return Object.values(segments).sort((a, b) => a.segmentNumber - b.segmentNumber)
  }, [data])

  const totalPages = Math.ceil(segmentData.length / SEGMENTS_PER_PAGE)
  const currentSegments = segmentData.slice(
    currentPage * SEGMENTS_PER_PAGE,
    (currentPage + 1) * SEGMENTS_PER_PAGE
  )

  const getSegmentColors = (segment) => {
    if (segment.total === 0) {
      return { severe: 0, new: 0, existing: 0 }
    }
    
    return {
      severe: (segment.severe / segment.total) * 100,
      new: (segment.new / segment.total) * 100,
      existing: (segment.existing / segment.total) * 100
    }
  }

  const handlePrevPage = () => {
    if (currentPage > 0) setCurrentPage(currentPage - 1)
  }

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) setCurrentPage(currentPage + 1)
  }

  return (
    <div className="rounded-lg shadow-md p-6" style={{ backgroundColor: colors.background.card }}>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold" style={{ color: colors.text.primary }}>Pipeline Visualization</h2>
          <p className="text-sm mt-1" style={{ color: colors.text.secondary }}>
            Showing segments {currentPage * SEGMENTS_PER_PAGE} - {Math.min((currentPage + 1) * SEGMENTS_PER_PAGE - 10, segmentData[segmentData.length - 1]?.segmentNumber || 0)} of {segmentData.length} segments
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 0}
            className="px-4 py-2 text-white rounded-lg disabled:cursor-not-allowed transition-colors"
            style={{ 
              backgroundColor: currentPage === 0 ? colors.button.disabled : colors.button.secondary
            }}
            onMouseEnter={(e) => currentPage !== 0 && (e.target.style.backgroundColor = colors.button.secondaryHover)}
            onMouseLeave={(e) => currentPage !== 0 && (e.target.style.backgroundColor = colors.button.secondary)}
          >
            ← Previous
          </button>
          <span className="text-sm font-medium" style={{ color: colors.text.primary }}>
            Page {currentPage + 1} of {totalPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage >= totalPages - 1}
            className="px-4 py-2 text-white rounded-lg disabled:cursor-not-allowed transition-colors"
            style={{ 
              backgroundColor: currentPage >= totalPages - 1 ? colors.button.disabled : colors.button.secondary
            }}
            onMouseEnter={(e) => currentPage < totalPages - 1 && (e.target.style.backgroundColor = colors.button.secondaryHover)}
            onMouseLeave={(e) => currentPage < totalPages - 1 && (e.target.style.backgroundColor = colors.button.secondary)}
          >
            Next →
          </button>
        </div>
      </div>

      <div className="mb-6 flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: colors.severity.severe }}></div>
          <span style={{ color: colors.text.primary }}>Severe (≥{SEVERE_THRESHOLD})</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: colors.severity.new }}></div>
          <span style={{ color: colors.text.primary }}>New (Persistence = 0)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: colors.severity.existing }}></div>
          <span style={{ color: colors.text.primary }}>Existing</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: colors.severity.none }}></div>
          <span style={{ color: colors.text.primary }}>No Anomalies</span>
        </div>
      </div>

      <div className="grid grid-cols-10 gap-2 relative">
        {Array.from({ length: SEGMENTS_PER_PAGE }).map((_, index) => {
          const segment = currentSegments[index]
          
          if (!segment) {
            return (
              <div
                key={index}
                className="h-6 bg-gray-200 rounded opacity-30"
              />
            )
          }

          const segmentColors = getSegmentColors(segment)
          const hasAnomalies = segment.total > 0

          return (
            <div
              key={segment.segmentNumber}
              className="relative h-6 rounded overflow-hidden cursor-pointer hover:ring-2 transition-all"
              style={{ 
                backgroundColor: colors.severity.none,
                borderColor: colors.border.focus
              }}
              onMouseEnter={() => setHoveredSegment(segment)}
              onMouseLeave={() => setHoveredSegment(null)}
              onMouseMove={(e) => setMousePosition({ x: e.clientX, y: e.clientY })}
              onClick={() => onSegmentClick(segment.segmentNumber)}
            >
              {hasAnomalies ? (
                <div className="flex h-full">
                  {segmentColors.severe > 0 && (
                    <div
                      style={{ 
                        width: `${segmentColors.severe}%`,
                        backgroundColor: colors.severity.severe
                      }}
                    />
                  )}
                  {segmentColors.new > 0 && (
                    <div
                      style={{ 
                        width: `${segmentColors.new}%`,
                        backgroundColor: colors.severity.new
                      }}
                    />
                  )}
                  {segmentColors.existing > 0 && (
                    <div
                      style={{ 
                        width: `${segmentColors.existing}%`,
                        backgroundColor: colors.severity.existing
                      }}
                    />
                  )}
                </div>
              ) : null}
            </div>
          )
        })}
      </div>

      {hoveredSegment && (
        <div 
          className="fixed z-50 rounded-lg shadow-xl p-3 pointer-events-none"
          style={{
            left: `${mousePosition.x + 10}px`,
            top: `${mousePosition.y - 120}px`,
            backgroundColor: colors.background.card,
            border: `2px solid ${colors.border.focus}`
          }}
        >
          <h3 className="font-semibold mb-1 text-sm" style={{ color: colors.text.primary }}>
            Segment {hoveredSegment.segmentNumber}-{hoveredSegment.segmentNumber + 9}
          </h3>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between gap-3">
              <span style={{ color: colors.text.secondary }}>Total:</span>
              <span style={{ color: colors.text.primary }} className="font-medium">{hoveredSegment.total}</span>
            </div>
            <div className="flex justify-between gap-3">
              <span style={{ color: colors.severity.severe }}>Severe:</span>
              <span style={{ color: colors.text.primary }} className="font-medium">{hoveredSegment.severe}</span>
            </div>
            <div className="flex justify-between gap-3">
              <span style={{ color: colors.severity.new }}>New:</span>
              <span style={{ color: colors.text.primary }} className="font-medium">{hoveredSegment.new}</span>
            </div>
            <div className="flex justify-between gap-3">
              <span style={{ color: colors.severity.existing }}>Existing:</span>
              <span style={{ color: colors.text.primary }} className="font-medium">{hoveredSegment.existing}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PipelineVisualizer
