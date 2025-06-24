# 🖼️ Vision AI

A Flask-based API that generates captions for images using a custom deep learning model (BLIP). The API provides endpoints for:

* Generating image captions
* Generating captions with bounding boxes

## 🚀 Features

✅ Generate descriptive captions for uploaded or base64-encoded images
✅ Optionally overlay a bounding box on the image
✅ Fast processing time
✅ CORS-enabled for cross-origin access

---

## 📂 Project Structure

```
blip/
├── app.py                # Flask server
├── model.py              # Image captioning model logic
├── index.html            # Simple frontend for testing
```

---

## 🔑 API Endpoints

| Endpoint            | Method | Description                                             |
| ------------------- | ------ | ------------------------------------------------------- |
| `/`                 | GET    | API status and list of endpoints                        |
| `/caption`          | POST   | Generate a caption for an image                         |
| `/caption_with_box` | POST   | Generate a caption and return image with a bounding box |

### POST request

* **Form field:** `image` (file upload or base64 string)

---

## 🛠 Installation

1️⃣ **Clone the repository**

```bash
git clone https://github.com/sebastianbenjamin/blip.git
cd blip
```

2️⃣ **Install the required packages**

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the app

```bash
python app.py
```

By default, it will run at:

```
http://0.0.0.0:5000/
```

---

## 🌐 Frontend

You can test the API using the provided frontend:

```
Open blip/index.html in your browser
```

This allows you to upload images and see the generated captions directly.

---

## 📝 Example cURL requests

### Generate caption

```bash
curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/caption
```

### Generate caption with bounding box

```bash
curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/caption_with_box
```

---

## 📌 Notes

* Input can be an uploaded image file or a base64-encoded string in the `image` field.
* Response includes processing time in seconds.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

👉 **Quick Start:**

```
python blip/app.py
```

Then open:

```
blip/index.html
```

in your browser!

---
