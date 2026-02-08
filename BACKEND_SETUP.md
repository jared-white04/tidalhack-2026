# Backend Setup Guide

## Overview
The backend is a Flask API that handles file uploads, runs the mapping analysis, and returns results.

## Installation

1. **Install Python dependencies:**
```bash
cd python-api
pip install -r requirements.txt
```

2. **Start the Flask server:**
```bash
python app.py
```

The server will run on `http://localhost:8000`

## API Endpoints

### 1. Health Check
```
GET /api/health
```
Returns server status.

### 2. Upload Files
```
POST /api/upload
Content-Type: multipart/form-data
Body: files (multiple CSV files)
```
- Uploads CSV files to `data/formatted_files/`
- Validates filename format: `ILI_YYYY_formatted.csv`
- Returns list of uploaded files and any errors

### 3. Run Analysis
```
POST /api/analyze
```
- Runs the `mapping.py` script
- Processes all files in `data/formatted_files/`
- Returns analysis results as JSON
- Results also saved to `data/Aligned_Results/Master_Alignment_Final.csv`

### 4. Mark Anomaly as Viewed
```
PATCH /api/anomaly/<anomaly_id>/viewed
```
- Toggles the viewed status for a specific anomaly
- Updates the CSV file

### 5. Clear Uploads
```
DELETE /api/clear-uploads
```
- Removes all CSV files from `data/formatted_files/`
- Useful for starting fresh

## File Upload Requirements

Files must be named: `ILI_YYYY_formatted.csv`

Examples:
- ✅ `ILI_2007_formatted.csv`
- ✅ `ILI_2015_formatted.csv`
- ✅ `ILI_2022_formatted.csv`
- ❌ `ILI_07_formatted.csv` (year must be 4 digits)
- ❌ `ILI_2022.csv` (missing "_formatted")

## Workflow

1. User uploads files via frontend
2. Frontend sends files to `/api/upload`
3. Files saved to `data/formatted_files/`
4. Frontend calls `/api/analyze`
5. Backend runs `mapping.py` script
6. Script processes files and generates results
7. Backend reads results CSV
8. Backend returns JSON to frontend
9. Frontend displays results in analysis page

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid files, missing data)
- `404`: Resource not found
- `500`: Server error

Error responses include:
```json
{
  "error": "Error message",
  "details": "Additional details (optional)"
}
```

## Development

### Running in Development Mode
```bash
python app.py
```

### Testing the API

Test health endpoint:
```bash
curl http://localhost:8000/api/health
```

Test file upload:
```bash
curl -X POST -F "files=@ILI_2007_formatted.csv" http://localhost:8000/api/upload
```

Test analysis:
```bash
curl -X POST http://localhost:8000/api/analyze
```

## Production Considerations

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (gunicorn, uwsgi)
3. Set up proper CORS configuration
4. Add authentication/authorization
5. Implement rate limiting
6. Add request validation
7. Set up logging
8. Configure file size limits

Example with gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
