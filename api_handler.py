import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HANDWRITINGOCR_API_KEY = os.getenv("HANDWRITINGOCR_API_KEY")

# HandwritingOCR API connetion
def extract_text_from_pdfs():
    attachments_folder = "attachments"
    extracted_folder = "extracted"

    os.makedirs(extracted_folder, exist_ok=True)

    url = "https://www.handwritingocr.com/api/v1/documents"      # HandwritingOCR API endpoint

    for filename in os.listdir(attachments_folder):
        pdf_path = os.path.join(attachments_folder, filename)
        output_path = os.path.join(extracted_folder, f"{os.path.splitext(filename)[0]}.docx")

        # Prepare headers and file for request
        headers = {
                "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}"
        }
        files = {
                "file": open(pdf_path, "rb")  # Open the PDF file in binary mode
        }

        try:
            # Send the POST request
            response = requests.post(url, headers=headers, files=files)

            # Handle the response
            if response.status_code == 200:
                # Save the extracted content to "extracted" folder
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Extracted text saved as: {output_path}")

                # Delete the original PDF
                os.remove(pdf_path)
                print(f"Deleted original PDF: {pdf_path}")

            else:
                print(f"Failed to extract text for {filename}. Status code: {response.status_code}")
                print(response.text)

        finally:
            # Ensure file is closed after the request
            files["file"].close()

extract_text_from_pdfs()