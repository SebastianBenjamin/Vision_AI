import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import io
import cv2
import numpy as np
import base64
import os

# Disable CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = ""

class ImageCaptioningModel:
    def __init__(self):
        self.processor = None
        self.model = None
        self.tokenizer = None
        self.device = "cpu"

    def _ensure_loaded(self):
        if self.processor is None or self.model is None:
            print("Loading lightweight ViT-GPT2 model...")
            self.model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
            self.processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
            self.tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
            self.model.to(self.device)
            print("Model loaded successfully.")

    def generate_caption(self, image):
        self._ensure_loaded()
        
        if isinstance(image, str):  # base64
            image = self.base64_to_pil(image)
        elif isinstance(image, bytes):
            image = Image.open(io.BytesIO(image)).convert("RGB")

        if not isinstance(image, Image.Image):
            raise ValueError("Expected PIL Image, base64 string, or bytes")

        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.to(self.device)
        
        with torch.no_grad():
            output_ids = self.model.generate(pixel_values, max_length=16, num_beams=4)
        
        caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return caption.strip()

    def base64_to_pil(self, base64_str):
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        image_bytes = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def image_to_base64(self, image):
        if isinstance(image, Image.Image):
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
            
        _, buffer = cv2.imencode('.jpg', image_bgr)
        return base64.b64encode(buffer).decode('utf-8')

    def add_bounding_box(self, image):
        if isinstance(image, str):
            image = self.base64_to_pil(image)
        
        image_np = np.array(image)
        height, width = image_np.shape[:2]
        border_size = 5
        color = (255, 0, 0)  # Red
        image_with_box = cv2.rectangle(
            image_np, 
            (border_size, border_size), 
            (width - border_size, height - border_size), 
            color, 
            border_size
        )
        return image_with_box
