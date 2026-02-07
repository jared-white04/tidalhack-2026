from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/python-api/data', methods=['GET'])
def get_data():
    return jsonify({
        'message': 'Hello from Python!',
        'timestamp': datetime.now().isoformat(),
        'server': 'Flask'
    })

@app.route('/python-api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
