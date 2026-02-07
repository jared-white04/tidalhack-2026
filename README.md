# Full Stack Application

React + Tailwind + Express.js + Python Flask

## Project Structure

```
├── client/          # React + Tailwind frontend (Vite)
├── server/          # Node.js Express API
├── python-api/      # Python Flask API
└── package.json     # Root package with scripts
```

## Setup

1. Install Node dependencies:
```bash
npm run install-all
```

2. Install Python dependencies:
```bash
cd python-api
pip install -r requirements.txt
```

## Running the App

Run all services concurrently:
```bash
npm run dev
```

Or run individually:
- Frontend: `npm run client` (http://localhost:3000)
- Express API: `npm run server` (http://localhost:5000)
- Python API: `npm run python` (http://localhost:8000)

## API Endpoints

### Express (Node.js)
- GET `/api/hello` - Test endpoint
- GET `/api/status` - Server status

### Flask (Python)
- GET `/python-api/data` - Test endpoint
- GET `/python-api/health` - Health check
