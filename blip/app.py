from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from PIL import Image  # Add this line at the top with other imports
from model import ImageCaptioningModel
import time

app = Flask(__name__)
CORS(app)

# Initialize model (lazy-loaded)
model = ImageCaptioningModel()

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Image Captioning API is running",
        "endpoints": {
            "/caption": "POST - Generate caption for an image",
            "/caption_with_box": "POST - Generate caption and add bounding box"
        }
    })

@app.route('/caption', methods=['POST'])
def caption():
    start_time = time.time()
    
    if 'image' not in request.files and 'image' not in request.form:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    try:
        if 'image' in request.files:
            image_file = request.files['image']
            image = Image.open(image_file).convert("RGB")
        else:
            image_data = request.form['image']
            image = model.base64_to_pil(image_data)
        
        caption = model.generate_caption(image)
        image_base64 = model.image_to_base64(image)
        
        return jsonify({
            "status": "success",
            "caption": caption,
            "image": image_base64,
            "processing_time": f"{time.time() - start_time:.2f} seconds"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing image: {str(e)}"
        }), 500

@app.route('/caption_with_box', methods=['POST'])
def caption_with_box():
    start_time = time.time()
    
    if 'image' not in request.files and 'image' not in request.form:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    try:
        if 'image' in request.files:
            image_file = request.files['image']
            image = Image.open(image_file).convert("RGB")
        else:
            image_data = request.form['image']
            image = model.base64_to_pil(image_data)
        
        caption = model.generate_caption(image)
        image_with_box = model.add_bounding_box(image)
        image_base64 = model.image_to_base64(image_with_box)
        
        return jsonify({
            "status": "success",
            "caption": caption,
            "image": image_base64,
            "processing_time": f"{time.time() - start_time:.2f} seconds"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing image: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)