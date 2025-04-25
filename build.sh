#!/bin/bash
echo "Downloading BLIP model during build phase..."
python -c "
from transformers import BlipProcessor, BlipForConditionalGeneration;
BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-small');
BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-small');
print('Model downloaded successfully!')
"