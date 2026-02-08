import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import NewAnalysisPage from './pages/NewAnalysisPage'
import AnalysisPage from './pages/AnalysisPage'
import LoadAnalysisPage from './pages/LoadAnalysisPage'

function App() {
  return (
    <Router>
      <div className="flex">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/new-analysis" element={<NewAnalysisPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/load-analysis" element={<LoadAnalysisPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
