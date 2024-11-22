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

def download_exctracted_docx(document_id, filename, folder):
    extracted_folder = folder
    filename = filename[:-4] + ".docx"
    extracted_docx = os.path.join(extracted_folder, filename)
    url = f"https://www.handwritingocr.com/api/v2/documents/{document_id}.docx"

    headers = {
        "Authorization": f"Bearer {HANDWRITINGOCR_API_KEY}",
    }
    
    output_file = extracted_docx

    response = requests.get(url,headers=headers)

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def extract_pdf(pdf_path, pdf_name, output_folder):
    extracted_path = os.path.join(output_folder, pdf_name)
    pdf_path = pdf_path
    document_id = upload_pdf(pdf_path)

    time.sleep(20)

    document_status = get_status(document_id)
    print(document_status)

    while True:
        if document_status == "processed":
            download_exctracted_docx(document_id, extracted_path)
            break
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

pdf_path = "/home/gracjan/dev/translation_api/attachments/02 Active Cars Form - C GR-1.pdf"
pdf_name = "02 Active Cars Form - C GR-1.pdf"
folder = "extracted"
path = os.path.join(folder, pdf_name)

# extract_pdf(pdf_path, pdf_name, folder)

download_exctracted_docx("WA9ArO38pE", pdf_name, folder)