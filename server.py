#!/usr/bin/env python3
from flask import Flask, request, jsonify
from PIL import Image
import io, os, base64, logging, traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Pre-load model on startup
logger.info("Loading rembg model...")
from rembg import remove, new_session
SESSION = new_session("u2net")
logger.info("Model ready!")

def hex_to_rgba(hex_color):
    """Convert #rrggbb to (r, g, b, 255)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, 255)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Running', 'model_loaded': True})

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'ok'})

@app.route('/remove-background', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        file     = request.files['image']
        data     = file.read()
        bg_color = request.form.get('bg_color', '').strip()  # e.g. "#ffffff" or empty

        if not data:
            return jsonify({'success': False, 'error': 'Empty image'}), 400

        logger.info(f"Processing {file.filename} ({len(data)//1024}KB) bg_color={bg_color or 'transparent'}")

        # Validate image
        try:
            Image.open(io.BytesIO(data))
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid image: {e}'}), 400

        # Remove background
        output = remove(data, session=SESSION)
        result_img = Image.open(io.BytesIO(output)).convert('RGBA')

        # Apply background color if specified
        if bg_color and bg_color.startswith('#') and len(bg_color) >= 7:
            try:
                rgba = hex_to_rgba(bg_color)
                background = Image.new('RGBA', result_img.size, rgba)
                background.paste(result_img, mask=result_img.split()[3])  # use alpha as mask
                result_img = background.convert('RGB')  # flatten to RGB
                logger.info(f"Applied background color {bg_color}")
            except Exception as e:
                logger.warning(f"Could not apply bg color: {e}, using transparent")
                result_img = Image.open(io.BytesIO(output)).convert('RGBA')

        buf = io.BytesIO()
        fmt = 'JPEG' if bg_color and not bg_color == '' else 'PNG'
        if result_img.mode == 'RGBA':
            fmt = 'PNG'  # can't save RGBA as JPEG
        result_img.save(buf, format=fmt, quality=95 if fmt == 'JPEG' else None, optimize=True)
        buf.seek(0)

        logger.info(f"Done! {fmt} output: {len(buf.getvalue())//1024}KB")
        return jsonify({
            'success': True,
            'image_data': base64.b64encode(buf.getvalue()).decode(),
            'format': fmt.lower()
        })

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)
