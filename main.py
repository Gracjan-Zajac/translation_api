import time
from file_manager import process_pdf_attachments


def main():
    while True:
        process_pdf_attachments()
        print("Waiting for new emails...")
        time.sleep(60)

if __name__ == "__main__":
    main()