from flask import Flask, request, send_file, jsonify
from google.cloud import vision
from google.oauth2 import service_account
from openpyxl import Workbook
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load credentials from the JSON key file
credentials = service_account.Credentials.from_service_account_file(
    'vivid-router-425405-d2-a599618b747a.json'
)
client = vision.ImageAnnotatorClient(credentials=credentials)

@app.route("C:\Users\laxma\OneDrive\Documents\excel.jpg", methods=['POST'])
def process_image():
    try:
        # Check if request contains image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        # Read image from request
        image = request.files['image'].read()

        # Perform OCR on the image using Google Cloud Vision
        image = vision.Image(content=image)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        # Extract text from the response
        if len(texts) > 0:
            ocr_text = texts[0].description
        else:
            ocr_text = ""

        # Convert OCR text to Excel
        wb = Workbook()
        ws = wb.active
        for line in ocr_text.split('\n'):
            ws.append([line])

        # Save Excel file
        excel_filename = 'output.xlsx'
        wb.save(excel_filename)

        # Send Excel file as response
        response = send_file(excel_filename, as_attachment=True)
        
        # Clean up the file after sending it
        response.call_on_close(lambda: os.remove(excel_filename))
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
