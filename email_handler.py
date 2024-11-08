import os
from dotenv import find_dotenv, load_dotenv
import imaplib
import email
from email.header import decode_header

# Load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Connect to the Gmail IMAP server
def connect_to_inbox():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.select("inbox")
    return mail

# Search for unread emails with PDF attachment
def search_for_pdf_emails(mail):
    status, messages = mail.search(None, "UNSEEN")      # Search for unread emails
    email_ids = messages[0].split()
    pdf_emails = []

    print(f"Total emails found: {len(email_ids)}")  # Check if emails are being found

    for num in email_ids:
        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Print subject for each email to verify if it's fetching correctly
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        print(f"Processing email with subject: {subject}")

        # Check for attachments and look for a PDF
        for part in msg.walk():
            if part.get_content_type() == "application/pdf":
                print("PDF attachment found.")
                pdf_emails.append((num, part))
                break       # Stop after finding the first PDF attachment in the email
        return pdf_emails
    
# Download the PDF attachment
def download_pdf_attachment(mail, email_data):
    email_id, part = email_data
    filename = part.get_filename()
    if filename:
        #Decode filename if needed
        filename = decode_header(filename)[0][0].decode("utf-8") if isinstance(filename, bytes) else filename
        filepath = os.path.join("attachments", filename)    # Save in an "attachments" folder

        # Write the PDF file to the directory
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        print(f"Downloaded: {filename}")
        return filepath
    return None

# Main function to run email receiving process
def receive_email_with_pdf():
    mail = connect_to_inbox()
    pdf_emails = search_for_pdf_emails(mail)

    # Download attachments from each email with a PDF
    pdf_paths = []
    for email_data in pdf_emails:
        pdf_path = download_pdf_attachment(mail, email_data)
        if pdf_path:
            pdf_paths.append(pdf_path)
    
    mail.logout()
    return pdf_paths  # Return list of downloaded PDF paths for further processing

receive_email_with_pdf()