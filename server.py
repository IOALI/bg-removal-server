#!/usr/bin/env python3
from flask import Flask, request, jsonify
from PIL import Image
import io, os, base64, logging, traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Running'})

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

        # Step 1: validate image
        try:
            img = Image.open(io.BytesIO(data))
            logger.info(f"Image OK: {img.size} {img.format}")
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid image: {e}'}), 400

        # Step 2: remove background
        try:
            from rembg import remove
            logger.info("Calling rembg.remove()...")
            output = remove(data)
            logger.info("rembg done!")
        except Exception as e:
            err = traceback.format_exc()
            logger.error(f"rembg failed: {err}")
            return jsonify({'success': False, 'error': f'rembg error: {str(e)}', 'detail': err}), 500

        # Step 3: encode result
        result = Image.open(io.BytesIO(output)).convert('RGBA')
        buf = io.BytesIO()
        result.save(buf, format='PNG')
        buf.seek(0)

        logger.info(f"Success! Output: {len(buf.getvalue())//1024}KB")
        return jsonify({
            'success': True,
            'image_data': base64.b64encode(buf.getvalue()).decode(),
            'format': 'png'
        })

    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"Unexpected error: {err}")
        return jsonify({'success': False, 'error': str(e), 'detail': err}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)
