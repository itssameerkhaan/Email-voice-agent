# save as gmail_details.py (or paste into your test_gmail_api.py)
import base64
import json
from google.oauth2.credentials import Credentials
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from email import message_from_bytes
from email.header import decode_header

SCOPES = ["https://mail.google.com/"]

def build_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for next run
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_message_headers(msg):
    """Return a dict of relevant headers from a message resource."""
    headers = {}
    for h in msg.get("payload", {}).get("headers", []):
        name = h.get("name", "").lower()
        if name in ("from", "subject", "date", "to", "cc"):
            headers[name] = h.get("value")
    return headers


def decode_base64url(data_str):
    """Decode base64url to bytes."""
    if not data_str:
        return ""
    # pad and replace URL-safe chars
    missing_padding = len(data_str) % 4
    if missing_padding:
        data_str += "=" * (4 - missing_padding)
    return base64.urlsafe_b64decode(data_str)

def get_plain_text_from_payload(payload):
    """Walk multipart payload to find the text/plain part; fallback to snippet."""
    if not payload:
        return ""
    # If single part
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain" and payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        return decode_base64url(data).decode("utf-8", errors="ignore")

    # If multipart, search parts
    for part in payload.get("parts", []) or []:
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return decode_base64url(part["body"]["data"]).decode("utf-8", errors="ignore")
        # sometimes nested parts:
        if part.get("parts"):
            text = get_plain_text_from_payload(part)
            if text:
                return text
    return ""

def show_recent_emails(max_results=5):
    service = build_service()
    # list recent message IDs
    res = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = res.get("messages", [])
    if not messages:
        print("No messages found.")
        return

    for msg_meta in messages:
        msg_id = msg_meta["id"]
        # fetch full message (includes headers and payload)
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

        headers = get_message_headers(msg)
        subject = headers.get("subject", "(no subject)")
        sender = headers.get("from", "(unknown sender)")
        date = headers.get("date", "(unknown date)")
        snippet = msg.get("snippet", "")

        # try to extract plain text body (best-effort)
        body_text = get_plain_text_from_payload(msg.get("payload"))
        if not body_text:
            body_text = snippet

        print("------------------------------------------------------------")
        print(f"ID: {msg_id}")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print()
        print("Preview / Body (first 1000 chars):")
        print(body_text[:1000])
        print("------------------------------------------------------------\n")

def send_email(to_email, subject, body_text):
    """
    Send an email using Gmail API.
    :param to_email: recipient email address
    :param subject: subject of the email
    :param body_text: plain text body of the email
    """
    service = build_service()  # your existing function to build Gmail API service

    # Create MIME message
    message = MIMEText(body_text, "plain")
    message["to"] = to_email
    message["from"] = "me"  # 'me' tells Gmail API to send from authenticated account
    message["subject"] = subject

    # Encode message in base64 URL-safe format
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Create message object for Gmail API
    body = {"raw": raw_message}

    # Send the email
    sent_message = service.users().messages().send(userId="me", body=body).execute()
    print(f"Email sent! Message ID: {sent_message['id']}")

if __name__ == "__main__":
    send_email(
        to_email="sameerkhan1ssk1@gmail.com",
        subject="Test Email from Gmail API this is sameer",
        body_text="Hello! This is a test email sent via Gmail API using Python."
    )
