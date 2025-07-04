import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import io
import cv2
import numpy as np
import base64

class ImageCaptioningModel:
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = "cpu"  # Force CPU for stability

    def _ensure_loaded(self):
        """Lazy-load the model only when needed."""
        if self.processor is None or self.model is None:
            print("Loading BLIP-small model...")
            # Change this line in model.py
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            print("Model loaded successfully!")

    def generate_caption(self, image):
        """Generate a caption for the given image."""
        self._ensure_loaded()
        
        if isinstance(image, str):  # Base64 string
            image = self.base64_to_pil(image)
        elif isinstance(image, bytes):  # Binary data
            image = Image.open(io.BytesIO(image)).convert("RGB")
        
        if not isinstance(image, Image.Image):
            raise ValueError("Expected PIL Image, base64 string, or bytes")

        inputs = self.processor(image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(**inputs)

        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

    def base64_to_pil(self, base64_str):
        """Convert base64 string to PIL Image."""
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        image_bytes = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def image_to_base64(self, image):
        """Convert PIL Image to base64 string."""
        if isinstance(image, Image.Image):
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
            
        _, buffer = cv2.imencode('.jpg', image_bgr)
        return base64.b64encode(buffer).decode('utf-8')

    def add_bounding_box(self, image):
        """Add a bounding box to the image (placeholder)."""
        if isinstance(image, str):
            image = self.base64_to_pil(image)
        
        image_np = np.array(image)
        height, width = image_np.shape[:2]
        
        border_size = 5
        color = (0, 255, 0)  # Green
        image_with_box = cv2.rectangle(
            image_np, 
            (border_size, border_size), 
            (width - border_size, height - border_size), 
            color, 
            border_size
        )
        return image_with_box