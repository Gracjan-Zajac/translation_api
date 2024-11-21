import os
import requests
import time
import deepl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HANDWRITINGOCR_API_KEY = os.getenv("HANDWRITINGOCR_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# def upload_pdf():
#     attachments_folder = "attachments"
#     url = "https://www.handwritingocr.com/api/v1/documents"

#     headers = {
#         "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}"
#     }

#     # Use the first PDF file in the attachments folder
#     for filename in os.listdir(attachments_folder):
#         if filename.endswith(".pdf"):
#             pdf_path = os.path.join(attachments_folder, filename)
            
#             # Prepare file and payload for the request
#             files = {
#                 "file": open(pdf_path, "rb")
#             }
#             data = {
#                 "action": "transcribe",
#                 "extractor_id": 1
#             }

#             try:
#                 # Send the POST request to upload the PDF
#                 response = requests.post(url, headers=headers, files=files, data=data)
                
#                 # Print the response for each file
#                 print(f"File: {filename}")
#                 print("Response Status Code:", response.status_code)
#                 print("Response Text:", response.text)
#                 print("\n" + "-"*40 + "\n")  # Divider between responses

#             finally:
#                 files["file"].close()

#     return response.json()["document_id"]


# def get_detail():
#     url = "https://www.handwritingocr.com/api/v1/documents/vZ9NBDv9rX/download/wxv148tU4R9v6h3X4tDYinqbVmPVMqoP0vxLlcfR/transcribe.docx"
#     extracted_folder = "extracted"
#     output_path = os.path.join(extracted_folder, "test.docx")
#     headers = {
#       'Authorization': f'Bearer {HANDWRITINGOCR_API_KEY}',
#     }

#     response = requests.request('GET', url, headers=headers)
#     with open(output_path, "wb") as f:
#         f.write(response.content)


# # Run the function
# upload_pdf()

# get_detail()

def translate_document():
    input_folder = "extracted"
    output_folder = "translated"
    translator = deepl.Translator(DEEPL_API_KEY)

    for filename in os.listdir(input_folder):
        if filename.endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                translator.translate_document_from_filepath(
                    input_path,
                    output_path,
                    target_lang="EN-GB",
                )
                os.remove(input_path)
                print("docu translated")
                return(output_path)


            except deepl.DocumentTranslationException as error:
                # If an error occurs during document translation after the document was
                # already uploaded, a DocumentTranslationException is raised. The
                # document_handle property contains the document handle that may be used to
                # later retrieve the document from the server, or contact DeepL support.
                doc_id = error.document_handle.id
                doc_key = error.document_handle.key
                print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")


            except deepl.DeepLException as error:
                # Errors during upload raise a DeepLException
                print(error)
                