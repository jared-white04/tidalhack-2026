import { useNavigate } from 'react-router-dom'
import colors from '../styles/colors'
import myLocalImage from '../assets/pipeline.jpg';

function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Hero Background with Gradient */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${myLocalImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Dark overlay for text contrast */}
        <div 
          className="absolute inset-0"
          style={{
            backgroundColor: colors.hero.darkOverlay
          }}
        />
        {/* Gradient fade to page background */}
        <div 
          className="absolute inset-0"
          style={{
            background: `linear-gradient(to bottom, transparent 0%, transparent ${colors.hero.gradientStart}, ${colors.background.page} ${colors.hero.gradientEnd})`
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-4 max-w-4xl">
        <h1 
          className="text-6xl font-bold mb-6"
          style={{ color: colors.text.white }}
        >
          Pipeline Data Analysis
        </h1>
        <p 
          className="text-xl mb-12"
          style={{ color: colors.text.white, opacity: 0.9 }}
        >
          Advanced anomaly detection and visualization for pipeline inspection data
        </p>

        <div className="flex gap-6 justify-center">
          <button
            onClick={() => navigate('/new-analysis')}
            className="px-8 py-4 rounded-lg font-semibold text-lg shadow-lg transition-all transform hover:scale-105"
            style={{ 
              backgroundColor: 'transparent',
              border: `2px solid ${colors.button.primary}`,
              color: colors.button.primary
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = colors.button.primary
              e.target.style.color = colors.text.white
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent'
              e.target.style.color = colors.button.primary
            }}
          >
            Get Started
          </button>

          <button
            onClick={() => navigate('/load-analysis')}
            className="px-8 py-4 rounded-lg font-semibold text-lg shadow-lg transition-all transform hover:scale-105"
            style={{ 
              backgroundColor: 'transparent',
              border: `2px solid ${colors.button.secondary}`,
              color: colors.button.secondary
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = colors.button.secondary
              e.target.style.color = colors.text.white
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent'
              e.target.style.color = colors.button.secondary
            }}
          >
            Load Analysis
          </button>
        </div>
      </div>
    </div>
  )
}

export default HomePage
