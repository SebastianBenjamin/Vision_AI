import requests
import base64
import json
import argparse
import os
from PIL import Image
import io
import time

def test_api(image_path, endpoint="caption", url="https://api-caption-generator-blip.onrender.com/"):
    """Test the image captioning API with a local image."""
    print(f"Testing API endpoint: {url}/{endpoint}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
    
    # Read image file
    with open(image_path, "rb") as f:
        image_content = f.read()
    
    # Create multipart form data
    files = {'image': (os.path.basename(image_path), image_content)}
    
    try:
        start_time = time.time()
        print(f"Sending request to {url}/{endpoint}...")
        
        # Send request
        response = requests.post(f"{url}/{endpoint}", files=files)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Status: {data['status']}")
            print(f"Caption: {data['caption']}")
            print(f"Server processing time: {data['processing_time']}")
            print(f"Total request time: {time.time() - start_time:.2f} seconds")
            
            # Save the returned image
            if 'image' in data:
                image_data = base64.b64decode(data['image'])
                output_path = f"output_{endpoint}_{os.path.basename(image_path)}"
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"Saved returned image to {output_path}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the image captioning API')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('--endpoint', default='caption', choices=['caption', 'caption_with_box'],
                        help='API endpoint to test (caption or caption_with_box)')
    parser.add_argument('--url', default='https://api-caption-generator-blip.onrender.com/',
                        help='API URL (default: https://api-caption-generator-blip.onrender.com/)')
    
    args = parser.parse_args()
    test_api(args.image_path, args.endpoint, args.url)