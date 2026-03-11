#!/usr/bin/env python3
"""
Background Removal Server for Railway.app
Uses rembg (free, local AI) - no API key needed!
"""

from flask import Flask, request, jsonify
from rembg import remove
from PIL import Image
import io
import os
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Background Removal Server is running on Railway!',
        'version': '1.0.0'
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Background Removal Server is running',
        'version': '1.0.0'
    })


@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        file = request.files['image']
        image_data = file.read()

        if len(image_data) == 0:
            return jsonify({'success': False, 'error': 'Empty image file'}), 400

        if len(image_data) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large (max 50MB)'}), 400

        logger.info(f"Processing: {file.filename} ({len(image_data)} bytes)")

        # Validate image
        try:
            img = Image.open(io.BytesIO(image_data))
            logger.info(f"Format: {img.format}, Size: {img.size}")
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid image: {str(e)}'}), 400

        # Remove background
        output_data = remove(image_data)

        # Convert to PNG
        output_image = Image.open(io.BytesIO(output_data))
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format='PNG', optimize=True)
        output_buffer.seek(0)

        output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        logger.info("Background removed successfully!")
        return jsonify({
            'success': True,
            'image_data': output_base64,
            'format': 'png'
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
