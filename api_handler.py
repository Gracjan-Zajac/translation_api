import os
import requests
import time
import deepl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HANDWRITINGOCR_API_KEY = os.getenv("HANDWRITINGOCR_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

def upload_pdf(pdf_path):
    url = "https://www.handwritingocr.com/api/v2/documents"

    headers = {
        "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}",
        # "Accept": "application/pdf",
        # "Content-Type": "multipart/form-data"
    }

    files = {
        "file": open(pdf_path, "rb"),
    }

    data = {
        "action": "transcribe",
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    files["file"].close()

    document_id = response.json()["document_id"]

    return document_id

def get_status(document_id):
    url = f"https://www.handwritingocr.com/api/v2/documents/{document_id}"

    headers = {
        "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}",
    }

    response = requests.get(url,headers=headers)
    status = response.json()["status"]

    return status

def download_exctracted_docx(document_id, filename, output_folder):
    filename = filename[:-4] + "_processed.docx"
    output_file = os.path.join(output_folder, filename)
    url = f"https://www.handwritingocr.com/api/v2/documents/{document_id}.docx"

    headers = {
        "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}",
    }

    response = requests.get(url, headers=headers, stream=True)

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return output_file, filename

def extract_pdf(pdf_path, pdf_name, output_folder):
    document_id = upload_pdf(pdf_path)

    time.sleep(20)

    while True:
        document_status = get_status(document_id)
        print(f"OCR status: {document_status}")

        if document_status == "processed":
            extracted_pdf_path, extracted_pdf_name = download_exctracted_docx(document_id, pdf_name, output_folder)
            return extracted_pdf_path, extracted_pdf_name
        else:
            time.sleep(20)

def translate_document(input_path, output_path):
    translator = deepl.Translator(DEEPL_API_KEY)

    try:
        translator.translate_document_from_filepath(
            input_path,
            output_path,
            target_lang="EN-GB",
        )
        os.remove(input_path)
        print("Docu translated")
        return output_path


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
