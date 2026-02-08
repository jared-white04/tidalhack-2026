# How to Start the Backend Server

## Quick Start

1. **Open a new terminal** (separate from the frontend)

2. **Navigate to the python-api directory:**
```bash
cd python-api
```

3. **Install dependencies** (first time only):
```bash
pip install -r requirements.txt
```

4. **Start the Flask server:**
```bash
python app.py
```

You should see:
```
Starting Flask API server...
Upload folder: /path/to/data/formatted_files
Results folder: /path/to/data/Aligned_Results
 * Running on http://0.0.0.0:8000
```

## Troubleshooting

### "python: command not found"
Try using `python3` instead:
```bash
python3 app.py
```

### Port 8000 already in use
Kill the process using port 8000:
```bash
# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Module not found errors
Make sure you installed dependencies:
```bash
pip install Flask flask-cors pandas numpy
```

### Cannot connect from frontend
1. Check that the server is running (you should see Flask output)
2. Verify it's running on port 8000
3. Check for firewall blocking localhost:8000
4. Try accessing http://localhost:8000/api/health in your browser

## Running Both Frontend and Backend

You need **TWO terminals**:

**Terminal 1 - Backend:**
```bash
cd python-api
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run client
```

## Testing the Backend

Once running, test the health endpoint:
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{"status": "healthy", "message": "Python API is running"}
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.
