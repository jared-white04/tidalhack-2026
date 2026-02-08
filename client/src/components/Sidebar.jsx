import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import colors from '../styles/colors'

function Sidebar() {
  const [isOpen, setIsOpen] = useState(true)
  const location = useLocation()

  const menuItems = [
    { path: '/', label: 'Home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { path: '/new-analysis', label: 'Create New Analysis', icon: 'M12 4v16m8-8H4' },
    { path: '/load-analysis', label: 'Load Analysis', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <>
      <div 
        className={`fixed top-0 left-0 h-full shadow-lg transition-all duration-300 z-40 ${isOpen ? 'w-64' : 'w-16'}`}
        style={{ backgroundColor: colors.background.card }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b" style={{ borderColor: colors.border.light }}>
            <div className="flex items-center justify-between">
              {isOpen && (
                <h1 className="text-lg font-bold" style={{ color: colors.text.primary }}>
                  Pipeline Analysis
                </h1>
              )}
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 rounded-lg transition-colors"
                style={{ color: colors.text.secondary }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.background.hover}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Menu Items */}
          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {menuItems.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors"
                    style={{
                      backgroundColor: isActive(item.path) ? colors.background.selected : 'transparent',
                      color: colors.text.primary
                    }}
                    onMouseEnter={(e) => !isActive(item.path) && (e.currentTarget.style.backgroundColor = colors.background.hover)}
                    onMouseLeave={(e) => !isActive(item.path) && (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                    {isOpen && <span className="font-medium">{item.label}</span>}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>

      {/* Spacer to prevent content from going under sidebar */}
      <div className={`transition-all duration-300 ${isOpen ? 'w-64' : 'w-16'}`} />
    </>
  )
}

export default Sidebar
