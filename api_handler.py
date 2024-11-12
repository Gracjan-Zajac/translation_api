import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HANDWRITINGOCR_API_KEY = os.getenv("HANDWRITINGOCR_API_KEY")


def upload_pdf():
    attachments_folder = "attachments"
    url = "https://www.handwritingocr.com/api/v1/documents"

    headers = {
        "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}"
    }

    # Use the first PDF file in the attachments folder
    for filename in os.listdir(attachments_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(attachments_folder, filename)
            
            # Prepare file and payload for the request
            files = {
                "file": open(pdf_path, "rb")
            }
            data = {
                "action": "transcribe",
                "extractor_id": 16  # Adjust if required by the API
            }

            try:
                # Send the POST request to upload the PDF
                response = requests.post(url, headers=headers, files=files, data=data)
                
                # Print the response for each file
                print(f"File: {filename}")
                print("Response Status Code:", response.status_code)
                print("Response Text:", response.text)
                print("\n" + "-"*40 + "\n")  # Divider between responses

            finally:
                files["file"].close()  # Ensure the file is closed after the request

# Run the function
upload_pdf()