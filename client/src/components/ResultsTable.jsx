import { useState, useMemo, useEffect } from 'react'
import colors from '../styles/colors'

function ResultsTable({ data, onMarkViewed, filterJointNumber, onClearFilter }) {
  const [sortBy, setSortBy] = useState('confidence')
  const [sortOrder, setSortOrder] = useState('desc')
  const [filterUnviewed, setFilterUnviewed] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)
  const ITEMS_PER_PAGE = 30

  // Reset to first page when filter changes
  useEffect(() => {
    setCurrentPage(0)
  }, [filterJointNumber])

  const sortedAndFilteredData = useMemo(() => {
    let filtered = [...data]

    if (filterUnviewed) {
      filtered = filtered.filter(row => row.viewed === 'N')
    }

    // Apply segment filter BEFORE sorting
    if (filterJointNumber !== null) {
      filtered = filtered.filter(row => row.jointNumber >= filterJointNumber)
    }

    filtered.sort((a, b) => {
      let aVal = a[sortBy]
      let bVal = b[sortBy]

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    return filtered
  }, [data, sortBy, sortOrder, filterUnviewed, filterJointNumber])

  const totalPages = Math.ceil(sortedAndFilteredData.length / ITEMS_PER_PAGE)
  const paginatedData = sortedAndFilteredData.slice(
    currentPage * ITEMS_PER_PAGE,
    (currentPage + 1) * ITEMS_PER_PAGE
  )

  const handlePrevPage = () => {
    if (currentPage > 0) setCurrentPage(currentPage - 1)
  }

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) setCurrentPage(currentPage + 1)
  }

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
    // Clear segment filter when sorting
    if (onClearFilter) {
      onClearFilter()
    }
  }

  const getSeverityColor = (severity) => {
    const severityNum = parseFloat(severity)
    if (severityNum >= 8) return { color: colors.severity.severe, bg: `${colors.severity.severe}20` }
    if (severityNum >= 5) return { color: colors.severity.new, bg: `${colors.severity.new}20` }
    return { color: colors.severity.existing, bg: `${colors.severity.existing}20` }
  }

  const getConfidenceColor = (confidence) => {
    const confNum = parseFloat(confidence)
    if (confNum >= 90) return { color: colors.confidence.high, bg: `${colors.confidence.high}20` }
    if (confNum >= 70) return { color: colors.confidence.medium, bg: `${colors.confidence.medium}20` }
    return { color: colors.confidence.low, bg: `${colors.confidence.low}20` }
  }

  const SortButton = ({ field, label }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center gap-1 hover:text-blue-600 transition-colors"
    >
      {label}
      {sortBy === field && (
        <svg className={`h-4 w-4 ${sortOrder === 'asc' ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      )}
    </button>
  )

  return (
    <div className="rounded-lg shadow-md overflow-hidden" style={{ backgroundColor: colors.background.card }}>
      <div className="p-4 border-b" style={{ backgroundColor: colors.background.hover }}>
        <div className="flex justify-between items-center mb-3">
          <div className="text-sm" style={{ color: colors.text.secondary }}>
            Showing {currentPage * ITEMS_PER_PAGE + 1}-{Math.min((currentPage + 1) * ITEMS_PER_PAGE, sortedAndFilteredData.length)} of {sortedAndFilteredData.length} anomalies
            {filterJointNumber !== null && (
              <span className="ml-2">
                <span className="font-medium" style={{ color: colors.text.link }}>
                  (From Segment {filterJointNumber})
                </span>
                <button
                  onClick={onClearFilter}
                  className="ml-2 text-xs underline"
                  style={{ color: colors.status.error }}
                  onMouseEnter={(e) => e.target.style.color = colors.button.dangerHover}
                  onMouseLeave={(e) => e.target.style.color = colors.status.error}
                >
                  Clear Filter
                </button>
              </span>
            )}
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filterUnviewed}
              onChange={(e) => setFilterUnviewed(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm" style={{ color: colors.text.primary }}>Show unviewed only</span>
          </label>
        </div>
        
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={handlePrevPage}
              disabled={currentPage === 0}
              className="px-3 py-1 text-white rounded disabled:cursor-not-allowed transition-colors text-sm"
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
              className="px-3 py-1 text-white rounded disabled:cursor-not-allowed transition-colors text-sm"
              style={{ 
                backgroundColor: currentPage >= totalPages - 1 ? colors.button.disabled : colors.button.secondary
              }}
              onMouseEnter={(e) => currentPage < totalPages - 1 && (e.target.style.backgroundColor = colors.button.secondaryHover)}
              onMouseLeave={(e) => currentPage < totalPages - 1 && (e.target.style.backgroundColor = colors.button.secondary)}
            >
              Next →
            </button>
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b" style={{ backgroundColor: colors.background.hover }}>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                Anomaly #
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                <SortButton field="jointNumber" label="Joint #" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                Start Distance
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                Type
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                <SortButton field="confidence" label="Confidence" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                <SortButton field="severity" label="Severity" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                <SortButton field="persistence" label="Persistence" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                <SortButton field="growthRate" label="Growth Rate" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: colors.text.primary }}>
                Viewed
              </th>
            </tr>
          </thead>
          <tbody className="divide-y" style={{ borderColor: colors.border.light }}>
            {paginatedData.map((row) => (
              <tr 
                key={row.anomalyNumber} 
                className="transition-colors"
                style={{ backgroundColor: colors.background.card }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.background.hover}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.background.card}
              >
                <td className="px-4 py-3 text-sm font-medium" style={{ color: colors.text.primary }}>
                  {row.anomalyNumber}
                </td>
                <td className="px-4 py-3 text-sm" style={{ color: colors.text.primary }}>
                  {row.jointNumber}
                </td>
                <td className="px-4 py-3 text-sm" style={{ color: colors.text.primary }}>
                  {row.startDistance}
                </td>
                <td className="px-4 py-3 text-sm" style={{ color: colors.text.primary }}>
                  {row.anomalyType}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span 
                    className="px-2 py-1 rounded-full font-medium"
                    style={{ 
                      color: getConfidenceColor(row.confidence).color,
                      backgroundColor: getConfidenceColor(row.confidence).bg
                    }}
                  >
                    {row.confidence}%
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span 
                    className="px-2 py-1 rounded-full font-medium"
                    style={{ 
                      color: getSeverityColor(row.severity).color,
                      backgroundColor: getSeverityColor(row.severity).bg
                    }}
                  >
                    {row.severity}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm" style={{ color: colors.text.primary }}>
                  {row.persistence}
                </td>
                <td className="px-4 py-3 text-sm" style={{ color: colors.text.primary }}>
                  {row.growthRate}
                </td>
                <td className="px-4 py-3 text-sm">
                  <input
                    type="checkbox"
                    checked={row.viewed === 'Y'}
                    onChange={() => onMarkViewed(row.anomalyNumber)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ResultsTable
