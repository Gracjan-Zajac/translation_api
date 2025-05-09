import os
import email
import traceback
from email.header import decode_header
from email_handler import connect_to_inbox, send_email_with_attachment, send_error_email, send_error_notification
from api_handler import extract_pdf, translate_document

ALLOWED_SENDERS = os.getenv("ALLOWED_SENDERS", "").split(", ")
SUPPORT = os.getenv("SUPPORT")

# Download the attachment
def download_attachment(mail, email_data):
    attachment_folder = "attachments"
    email_id, part = email_data
    filename = part.get_filename()

    if filename:
        #Decode filename if needed
        decoded_parts = decode_header(filename)
        filename = "".join(
            part[0].decode(part[1] or "utf-8") if isinstance(part[0], bytes) else part[0]
            for part in decoded_parts
        )

        # Sanitize the filename to avoid issues with special characters
        filename = filename.replace("/", "_").replace("\\", "_")

        filepath = os.path.join(attachment_folder, filename)

        # Write the file to the directory
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        print(f"Downloaded: {filename}")
        return filepath, filename
    return None

def clear_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)

# Search and download attachment from unread emails. Extract and translate text. Send translated .docx file back. 
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
        try:
            status, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            message_id = msg["Message-ID"]

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

                # Check for attachments and look for a PDF or Word documents
                has_pdf_or_word = False
                for part in msg.walk():
                    content_type = part.get_content_type()

                    if content_type == "application/pdf":
                        print("PDF attachment found.")
                        pdf_path, pdf_name = download_attachment(mail, (num, part))
                        extracted_pdf_path, extracted_pdf_name = extract_pdf(pdf_path, pdf_name, extracted_folder)
                        translated_document_path = os.path.join(translated_folder, extracted_pdf_name)
                        translated_document = translate_document(extracted_pdf_path, translated_document_path)
                        send_email_with_attachment(sender, translated_document, original_message_id=message_id, original_subject=subject)
                        os.remove(translated_document)
                        os.remove(pdf_path)
                        pdf_emails.append((num, part))  # Store the email ID and part for each PDF
                        has_pdf_or_word = True

                    elif content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                        print("Word attachment found.")
                        word_path, word_name = download_attachment(mail, (num, part))
                        processed_word_name = "processed_" + word_name
                        translated_document_path = os.path.join(translated_folder, processed_word_name)
                        translated_document = translate_document(word_path, translated_document_path)
                        send_email_with_attachment(sender, translated_document, original_message_id=message_id, original_subject=subject)
                        os.remove(translated_document)
                        pdf_emails.append((num, part))  # Store the email ID and part for each PDF
                        has_pdf_or_word = True

                if not has_pdf_or_word:
                    print("No PDF/Word attachment found in this email.")
                    
            # mark as UNREAD if sender not in ALLOWED senders
            else:
                mail.store(num, '-FLAGS', '\\Seen')
                print(f"Email from {sender} ignored (not in allowed senders).")

        except Exception as e:
            attachment_folder = "attachments"
            error_message = traceback.format_exc()
            send_error_email(sender)
            send_error_notification(SUPPORT, error_message)
            clear_folder(attachment_folder)
            clear_folder(extracted_folder)
            clear_folder(translated_folder)


    print("All unread emails processed.")
    return pdf_emails

def process_attachments():
    mail = connect_to_inbox()
    pdf_emails = manage_attachment(mail)

    if pdf_emails:
        print("All PDF/Word files processed")

    mail.logout()

