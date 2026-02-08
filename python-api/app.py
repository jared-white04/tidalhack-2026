from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import subprocess
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'formatted_files')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'Aligned_Results')
ALLOWED_EXTENSIONS = {'csv'}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_filename(filename):
    """Check if filename matches ILI_YYYY_formatted.csv pattern"""
    import re
    pattern = r'^ILI_\d{4}_formatted\.csv$'
    return re.match(pattern, filename) is not None

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Python API is running'})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and save to formatted_files directory"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Validate filename format
                if not validate_filename(filename):
                    errors.append(f"{filename}: Must match pattern ILI_YYYY_formatted.csv")
                    continue
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                uploaded_files.append(filename)
            else:
                errors.append(f"{file.filename}: Invalid file type (must be CSV)")
        
        if not uploaded_files:
            return jsonify({
                'error': 'No valid files uploaded',
                'details': errors
            }), 400
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
            'files': uploaded_files,
            'errors': errors if errors else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run the mapping script and return results"""
    try:
        # Check if files exist in formatted_files directory
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        
        if not files:
            return jsonify({'error': 'No CSV files found in formatted_files directory'}), 400
        
        print(f"Found {len(files)} files to analyze: {files}")
        
        # Run the mapping script
        mapping_script = os.path.join(os.path.dirname(__file__), 'mapping.py')
        result = subprocess.run(
            ['python3', mapping_script],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"Mapping script error: {result.stderr}")
            return jsonify({
                'error': 'Analysis failed',
                'details': result.stderr
            }), 500
        
        print(f"Mapping script output: {result.stdout}")
        
        # Read the results CSV
        results_file = os.path.join(RESULTS_FOLDER, 'Master_Alignment_Final.csv')
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Results file not generated'}), 500
        
        # Load and format results for frontend
        df = pd.read_csv(results_file)
        
        # Convert to format expected by frontend
        results = []
        for _, row in df.iterrows():
            results.append({
                'anomalyNumber': int(row['anomaly_no']) if pd.notna(row['anomaly_no']) else None,
                'jointNumber': int(row['joint_no']) if pd.notna(row['joint_no']) else None,
                'startDistance': str(row['start_distance']) if pd.notna(row['start_distance']) else '',
                'anomalyType': str(row['anomaly_type']) if pd.notna(row['anomaly_type']) else '',
                'confidence': float(row['confidence']) if pd.notna(row['confidence']) else 0,
                'severity': float(row['severity']) if pd.notna(row['severity']) else 0,
                'persistence': int(row['persistence']) if pd.notna(row['persistence']) else 0,
                'growthRate': float(row['growth_rate']) if pd.notna(row['growth_rate']) else 0,
                'viewed': 'Y' if row['viewed'] == 'Yes' else 'N'
            })
        
        return jsonify({
            'message': 'Analysis complete',
            'totalAnomalies': len(results),
            'results': results
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Analysis timed out (exceeded 5 minutes)'}), 500
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-uploads', methods=['DELETE'])
def clear_uploads():
    """Clear all uploaded files from formatted_files directory"""
    try:
        files = os.listdir(UPLOAD_FOLDER)
        for file in files:
            if file.endswith('.csv'):
                os.remove(os.path.join(UPLOAD_FOLDER, file))
        
        return jsonify({
            'message': f'Cleared {len(files)} file(s)',
            'count': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomaly/<int:anomaly_id>/viewed', methods=['PATCH'])
def mark_viewed(anomaly_id):
    """Toggle viewed status for an anomaly"""
    try:
        results_file = os.path.join(RESULTS_FOLDER, 'Master_Alignment_Final.csv')
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Results file not found'}), 404
        
        df = pd.read_csv(results_file)
        
        # Find the anomaly
        mask = df['anomaly_no'] == anomaly_id
        if not mask.any():
            return jsonify({'error': 'Anomaly not found'}), 404
        
        # Toggle viewed status
        current_status = df.loc[mask, 'viewed'].iloc[0]
        new_status = 'No' if current_status == 'Yes' else 'Yes'
        df.loc[mask, 'viewed'] = new_status
        
        # Save back to CSV
        df.to_csv(results_file, index=False)
        
        return jsonify({
            'message': 'Viewed status updated',
            'anomalyId': anomaly_id,
            'viewed': 'Y' if new_status == 'Yes' else 'N'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask API server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Results folder: {RESULTS_FOLDER}")
    app.run(debug=True, port=8000, host='0.0.0.0')
