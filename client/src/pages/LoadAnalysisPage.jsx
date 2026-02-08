import colors from '../styles/colors'

function LoadAnalysisPage() {
  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: colors.background.page }}>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: colors.text.primary }}>
            Load Analysis
          </h1>
          <p style={{ color: colors.text.secondary }}>
            Load a previously saved analysis
          </p>
        </div>

        <div 
          className="rounded-lg shadow-md p-12 text-center"
          style={{ backgroundColor: colors.background.card }}
        >
          <svg 
            className="mx-auto h-24 w-24 mb-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            style={{ color: colors.text.light }}
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
            />
          </svg>
          <h2 className="text-2xl font-semibold mb-2" style={{ color: colors.text.primary }}>
            Coming Soon
          </h2>
          <p style={{ color: colors.text.secondary }}>
            This feature will be available once the backend is complete.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoadAnalysisPage
