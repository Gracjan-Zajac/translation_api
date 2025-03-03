import smtplib
from email.utils import encode_rfc2231
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import os

IMAP_HOST = os.getenv("IMAP_HOST")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Connect to the Gmail IMAP server
def connect_to_inbox():
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.select("inbox")
    return mail

def send_email_with_attachment(to_email, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = "Your translated document"

    #msg.attach(MIMEText(body, "plain"))

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)

        filename = os.path.basename(attachment_path)
        encoded_filename = encode_rfc2231(filename, 'utf-8')

        part.add_header("Content-Disposition", f'attachment; filename*={encoded_filename}')
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"Email with attachment sent to {to_email}")
