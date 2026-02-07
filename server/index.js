import express from 'express'
import cors from 'cors'

const app = express()
const PORT = 5000

app.use(cors())
app.use(express.json())

app.get('/api/hello', (req, res) => {
  res.json({
    message: 'Hello from Node/Express!',
    timestamp: new Date().toISOString(),
    server: 'Express.js'
  })
})

app.get('/api/status', (req, res) => {
  res.json({ status: 'running', uptime: process.uptime() })
})

app.listen(PORT, () => {
  console.log(`Express server running on http://localhost:${PORT}`)
})
