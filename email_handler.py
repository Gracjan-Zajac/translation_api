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

def send_email_with_attachment(to_email, attachment_paths, original_message_id=None, original_subject=None):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = f"Re: {original_subject}" if original_subject else "Your translated document"

    if original_message_id:
        msg["In-Reply-To"] = original_message_id
        msg["References"] = original_message_id

    #msg.attach(MIMEText(body, "plain"))

    for attachment_path in attachment_paths:
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

#Send an email to the user and inform that document cannot be processed due to an error
def send_error_email(to_email):
    body = f"""
    Hi,

    We encountered an error while processing your email. Our team has been notified, and we will resolve this issue as soon as possible.

    Best regards,
    Your Support Team
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = "Error Processing Your Email"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"Error email sent to {to_email}")

#Send en email to the Support Team and inform anout an error
def send_error_notification(to_email, error_message):
    body = f"""
    Hi,

    An error occured in Translation API:

    {error_message}

    Please take care of it. People needs you!
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = "Translation API error"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"Error notificaton sent to {to_email}")


