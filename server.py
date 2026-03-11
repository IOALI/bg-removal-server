#!/usr/bin/env python3
"""
Lightweight Background Removal Server
Uses transparent-background instead of rembg - much lighter on RAM
"""
from flask import Flask, request, jsonify
from PIL import Image
import io, os, base64, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

SESSION = None

def load_model():
    global SESSION
    try:
        from transparent_background import Remover
        SESSION = Remover(mode='base')
        logger.info("Model loaded OK!")
    except Exception as e:
        logger.error(f"transparent_background failed: {e}")
        # Fallback: try rembg
        try:
            from rembg import new_session
            SESSION = new_session("u2net_human_seg")
            logger.info("Fallback rembg loaded OK!")
        except Exception as e2:
            logger.error(f"rembg fallback also failed: {e2}")
            SESSION = "rembg_u2net"  # will try basic rembg on request

load_model()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Running', 'model': str(type(SESSION).__name__)})

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'ok'})

@app.route('/remove-background', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        data = file.read()
        if not data:
            return jsonify({'success': False, 'error': 'Empty image'}), 400

        logger.info(f"Processing {file.filename} ({len(data)//1024}KB)")
        img = Image.open(io.BytesIO(data)).convert('RGBA')

        # Try rembg (works on Railway with enough RAM)
        from rembg import remove as rembg_remove
        output_data = rembg_remove(data)
        result_img = Image.open(io.BytesIO(output_data)).convert('RGBA')

        buf = io.BytesIO()
        result_img.save(buf, format='PNG')
        buf.seek(0)
        logger.info("Done!")
        return jsonify({'success': True, 'image_data': base64.b64encode(buf.getvalue()).decode(), 'format': 'png'})

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)
