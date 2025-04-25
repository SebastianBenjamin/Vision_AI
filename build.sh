#!/bin/bash
python -c "
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer;
VisionEncoderDecoderModel.from_pretrained('nlpconnect/vit-gpt2-image-captioning');
ViTImageProcessor.from_pretrained('nlpconnect/vit-gpt2-image-captioning');
AutoTokenizer.from_pretrained('nlpconnect/vit-gpt2-image-captioning');
print('Model downloaded!')
"
