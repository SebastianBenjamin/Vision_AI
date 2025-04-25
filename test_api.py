import requests
import base64
import os
import argparse
import time

def test_api(image_path, endpoint="caption_with_box", url="http://localhost:5000/"):
    """Test the image captioning API with a local image."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        image_content = f.read()

    files = {'image': (os.path.basename(image_path), image_content)}

    print(f"📡 Sending request to {url.rstrip('/')}/{endpoint}...")

    try:
        start_time = time.time()
        response = requests.post(f"{url.rstrip('/')}/{endpoint}", files=files)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📝 Caption: {data['caption']}")
            print(f"⏱️ Server Time: {data['processing_time']}")
            print(f"⚡ Total Time: {elapsed:.2f} seconds")

            if 'image' in data:
                image_data = base64.b64decode(data['image'])
                output_path = f"output_{endpoint}_{os.path.basename(image_path)}"
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"💾 Saved returned image to: {output_path}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"🔥 Exception occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the image captioning API")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--endpoint", default="caption", choices=["caption", "caption_with_box"], help="Endpoint to test")
    parser.add_argument("--url", default="http://localhost:5000/", help="API base URL (default: http://localhost:5000/)")

    args = parser.parse_args()
    test_api(args.image_path, args.endpoint, args.url)
