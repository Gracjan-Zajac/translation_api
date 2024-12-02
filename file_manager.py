import os
import email
from email.header import decode_header
from email_handler import connect_to_inbox, send_email_with_attachment
from api_handler import extract_pdf, translate_document

ALLOWED_SENDERS = os.getenv("ALLOWED_SENDERS", "").split(", ")

# Download the PDF attachment
def download_pdf_attachment(mail, email_data):
    attachment_folder = "attachments"
    email_id, part = email_data
    filename = part.get_filename()
    if filename:
        #Decode filename if needed
        filename = decode_header(filename)[0][0].decode("utf-8") if isinstance(filename, bytes) else filename
        filepath = os.path.join(attachment_folder, filename)    # Save in an "attachments" folder

        # Write the PDF file to the directory
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        print(f"Downloaded: {filename}")
        return filepath, filename
    return None

# Search and download PDFs from unread emails. Extract and translate text. Send translated .docx file back. 
def manage_attachment(mail):
    extracted_folder = "extracted"
    translated_folder = "translated"
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()
    pdf_emails = []

    if not email_ids:
        print("No unread emails found.")
        return pdf_emails  # Return empty list if no unread emails

    print(f"Total emails found: {len(email_ids)}") 

    for num in email_ids:
        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        #Decode sender's email address
        sender = msg["From"]
        if sender:
            sender = email.utils.parseaddr(sender)[1]

        if sender in ALLOWED_SENDERS:
            print(f"Processing email from allowed sender: {sender}")

            # Print subject for each email to verify if it's fetching correctly
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            print(f"Processing email with subject: {subject}")

            # Check for attachments and look for a PDF
            has_pdf = False
            for part in msg.walk():
                if part.get_content_type() == "application/pdf":
                    print("PDF attachment found.")
                    pdf_path, pdf_name = download_pdf_attachment(mail, (num, part))
                    extracted_pdf_path, extracted_pdf_name = extract_pdf(pdf_path, pdf_name, extracted_folder)
                    translated_document_path = os.path.join(translated_folder, extracted_pdf_name)
                    translated_document = translate_document(extracted_pdf_path, translated_document_path)
                    send_email_with_attachment(sender, translated_document)
                    os.remove(translated_document)
                    os.remove(pdf_path)
                    pdf_emails.append((num, part))  # Store the email ID and part for each PDF
                    has_pdf = True
            
            if not has_pdf:
                print("No PDF attachment found in this email.")
                
        # mark as UNREAD if sender not in ALLOWED senders
        else:
            mail.store(num, '-FLAGS', '\\Seen')
            print(f"Email from {sender} ignored (not in allowed senders).")
    
    print("All unread emails processed.")
    return pdf_emails

def process_pdf_attachments():
    mail = connect_to_inbox()
    pdf_emails = manage_attachment(mail)

    if pdf_emails:
        print("All PDF files processed")

    mail.logout()

