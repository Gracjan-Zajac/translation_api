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
                download_pdf_attachment(mail, (num, part))
                pdf_emails.append((num, part))  # Store the email ID and part for each PDF
                has_pdf = True
        
        if not has_pdf:
            print("No PDF attachment found in this email.")
    
    print("All unread emails processed.")
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

    if pdf_emails:
        print("Unread emails with PDF attachments were processed.")
    
    mail.logout()

receive_email_with_pdf()
