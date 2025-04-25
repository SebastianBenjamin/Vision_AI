#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "Base64.h"

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Your captioning API URL
const char* apiUrl = "http://your-render-api-url/caption_with_box";

// Web server
WebServer server(80);

// Camera configuration for ESP32-CAM
#define CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Global variables
String lastCaption = "No caption yet";
String lastImage = "";
unsigned long captionTimestamp = 0;
bool processingImage = false;

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector
  
  Serial.begin(115200);
  Serial.println("\n\nESP32 Image Captioning System");
  
  // Initialize camera
  initCamera();
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup web server
  setupWebServer();
}

void loop() {
  server.handleClient();
  
  // Capture and process an image every 5 seconds if not currently processing
  unsigned long currentTime = millis();
  if (!processingImage && (currentTime - captionTimestamp > 5000)) {
    processingImage = true;
    captionTimestamp = currentTime;
    
    captureAndProcess();
    
    processingImage = false;
  }
}

void initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Initialize with medium quality and resolution
  config.frame_size = FRAMESIZE_VGA; // 640x480
  config.jpeg_quality = 12; // 0-63, lower is higher quality
  config.fb_count = 1;

  // Initialize the camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
  }
  
  Serial.println("Camera initialized successfully");
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi. Please check your credentials.");
  }
}

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/stream", HTTP_GET, handleStream);
  server.onNotFound(handleNotFound);
  
  server.begin();
  Serial.println("HTTP server started");
}

void handleRoot() {
  // Serve the HTML page
  String html = R"(
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>ESP32 Image Captioning</title>
      <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .image-container { margin: 20px 0; position: relative; display: inline-block; }
        img { max-width: 100%; border: 1px solid #ddd; }
        .caption { background: rgba(0,0,0,0.7); color: white; padding: 10px; position: absolute; bottom: 0; left: 0; right: 0; text-align: center; }
        button { padding: 10px 20px; margin: 10px; font-size: 16px; }
        .status { margin: 10px 0; font-style: italic; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>ESP32 Image Captioning</h1>
        <div class="status">Status: <span id="status">Ready</span></div>
        <div class="image-container">
          <img id="captionedImage" src="/stream" alt="Captioned Image">
          <div class="caption" id="imageCaption">)" + lastCaption + R"(</div>
        </div>
        <div>
          <button onclick="captureImage()">Capture & Generate Caption</button>
        </div>
      </div>
      
      <script>
        function captureImage() {
          document.getElementById('status').textContent = 'Processing...';
          
          fetch('/capture')
            .then(response => response.json())
            .then(data => {
              document.getElementById('imageCaption').textContent = data.caption;
              document.getElementById('captionedImage').src = 'data:image/jpeg;base64,' + data.image;
              document.getElementById('status').textContent = 'Ready';
            })
            .catch(error => {
              console.error('Error:', error);
              document.getElementById('status').textContent = 'Error: ' + error;
            });
        }
        
        // Auto-refresh the stream every 5 seconds
        setInterval(() => {
          document.getElementById('captionedImage').src = '/stream?' + new Date().getTime();
        }, 5000);
      </script>
    </body>
    </html>
  )";
  
  server.send(200, "text/html", html);
}

void handleCapture() {
  captureAndProcess();
  
  // Return the caption and image as JSON
  String jsonResponse = "{\"caption\":\"" + lastCaption + "\",\"image\":\"" + lastImage + "\"}";
  server.send(200, "application/json", jsonResponse);
}

void handleStream() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  
  server.sendHeader("Content-Type", "image/jpeg");
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.sendHeader("Content-Length", String(fb->len));
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  
  WiFiClient client = server.client();
  client.write(fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
}

void handleNotFound() {
  server.send(404, "text/plain", "Not found");
}

void captureAndProcess() {
  Serial.println("Capturing image...");
  
  // Get image from camera
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  Serial.printf("Image captured! Size: %zu bytes\n", fb->len);
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    // Encode image to base64
    size_t base64_len = Base64.encodedLength(fb->len);
    char* base64_buf = (char*)malloc(base64_len + 1);
    
    if (base64_buf) {
      Base64.encode(base64_buf, (char*)fb->buf, fb->len);
      base64_buf[base64_len] = 0; // Null terminate
      
      // Send to API
      Serial.println("Sending image to API...");
      sendToAPI(base64_buf);
      
      free(base64_buf);
    } else {
      Serial.println("Failed to allocate memory for base64 encoding");
    }
  }
  
  // Return the frame buffer back to be reused
  esp_camera_fb_return(fb);
}

void sendToAPI(const char* base64Image) {
  HTTPClient http;
  
  // Your endpoint
  http.begin(apiUrl);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  
  // Prepare form data
  String postData = "image=" + String(base64Image);
  
  // Send POST request
  int httpResponseCode = http.POST(postData);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response code: " + String(httpResponseCode));
    
    // Parse JSON response
    DynamicJsonDocument doc(16384); // Allocate large buffer for JSON
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
    } else {
      // Extract caption and image
      lastCaption = doc["caption"].as<String>();
      lastImage = doc["image"].as<String>();
      
      Serial.print("Caption: ");
      Serial.println(lastCaption);
    }
  } else {
    Serial.print("Error on sending POST: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}