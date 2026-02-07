import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [nodeData, setNodeData] = useState(null)
  const [pythonData, setPythonData] = useState(null)

  useEffect(() => {
    fetchNodeAPI()
    fetchPythonAPI()
  }, [])

  const fetchNodeAPI = async () => {
    try {
      const response = await axios.get('/api/hello')
      setNodeData(response.data)
    } catch (error) {
      console.error('Error fetching Node API:', error)
    }
  }

  const fetchPythonAPI = async () => {
    try {
      const response = await axios.get('/python-api/data')
      setPythonData(response.data)
    } catch (error) {
      console.error('Error fetching Python API:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-12">
          Full Stack Application
        </h1>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-blue-600 mb-4">
              Node/Express API
            </h2>
            <div className="bg-gray-50 rounded p-4">
              {nodeData ? (
                <pre className="text-sm">{JSON.stringify(nodeData, null, 2)}</pre>
              ) : (
                <p className="text-gray-500">Loading...</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-purple-600 mb-4">
              Python API
            </h2>
            <div className="bg-gray-50 rounded p-4">
              {pythonData ? (
                <pre className="text-sm">{JSON.stringify(pythonData, null, 2)}</pre>
              ) : (
                <p className="text-gray-500">Loading...</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
