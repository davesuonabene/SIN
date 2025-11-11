import sys
from flask import Flask, jsonify, request
import logging
import os

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    print(f"[AudioCraft Server]: Received prompt: {prompt}", file=sys.stderr)
    
    return jsonify({
        "status": "success",
        "message": f"placeholder audio for prompt: {prompt}"
    })

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("[AudioCraft Server]: Shutdown command received.", file=sys.stderr)
    os._exit(0)

if __name__ == '__main__':
    print("[AudioCraft Server]: Starting on http://127.0.0.1:5001", file=sys.stderr)
    app.run(host='127.0.0.1', port=5001)