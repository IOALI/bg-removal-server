#!/usr/bin/env python3
"""
Background Removal Server for Railway.app - FIXED VERSION
Pre-loads the AI model on startup to avoid timeout on first request.
"""

from flask import Flask, request, jsonify
from PIL import Image
import io
import os
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Pre-load model on startup
logger.info("Loading rembg AI model on startup...")
try:
    from rembg import remove, new_session
    SESSION = new_session("u2net")
    logger.info("rembg model loaded OK!")
except Exception as e:
    logger.error(f"Failed to load rembg: {e}")
    SESSION = None


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'ok', 'message': 'BG Removal Server running!', 'model_loaded': SESSION is not None})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running', 'model_loaded': SESSION is not None})


@app.route('/remove-background', methods=['POST'])
def remove_background():
    if SESSION is None:
        return jsonify({'success': False, 'error': 'AI model not loaded'}), 500
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        file = request.files['image']
        image_data = file.read()
        if not image_data:
            return jsonify({'success': False, 'error': 'Empty image'}), 400
        if len(image_data) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large'}), 400
        logger.info(f"Processing: {file.filename} ({len(image_data)//1024}KB)")
        try:
            Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid image: {e}'}), 400
        output_data = remove(image_data, session=SESSION)
        output_image = Image.open(io.BytesIO(output_data))
        buf = io.BytesIO()
        output_image.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        logger.info("Background removed successfully!")
        return jsonify({'success': True, 'image_data': base64.b64encode(buf.getvalue()).decode(), 'format': 'png'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
