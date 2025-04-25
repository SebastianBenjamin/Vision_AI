import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import io
import cv2
import numpy as np
import base64

class ImageCaptioningModel:
    def __init__(self):
        print("Loading image captioning model...")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("Model loaded successfully!")
        
    def generate_caption(self, image):
        """Generate a caption for the given image."""
        if isinstance(image, str):  # If image is a base64 string
            image = self.base64_to_pil(image)
        elif isinstance(image, bytes):  # If image is binary data
            image = Image.open(io.BytesIO(image)).convert("RGB")
        
        # Ensure we have a PIL image
        if not isinstance(image, Image.Image):
            raise ValueError("Expected PIL Image, base64 string, or bytes")
            
        # Generate caption
        inputs = self.processor(image, return_tensors="pt")
        out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        
        return caption
    
    def base64_to_pil(self, base64_str):
        """Convert base64 string to PIL Image."""
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        image_bytes = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image
    
    def image_to_base64(self, image):
        """Convert PIL Image to base64 string."""
        if isinstance(image, Image.Image):
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
            
        _, buffer = cv2.imencode('.jpg', image_bgr)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    def add_bounding_box(self, image):
        """Simple placeholder function to add a bounding box around the image."""
        # For a real implementation, you would use object detection models
        # This is a simplified version that just adds a border
        if isinstance(image, str):  # If image is a base64 string
            image = self.base64_to_pil(image)
        
        image_np = np.array(image)
        height, width = image_np.shape[:2]
        
        # Draw a border around the whole image
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