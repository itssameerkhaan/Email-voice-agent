import os
import base64
import json
import re
from datetime import datetime,timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.header import decode_header
from email import message_from_bytes

# ---------------------- CONFIG ----------------------
SCOPES = ["https://mail.google.com/"]

# ---------------------- AUTH ----------------------
def build_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

# ---------------------- HELPERS ----------------------
def decode_base64url(data_str):
    if not data_str:
        return ""
    missing_padding = len(data_str) % 4
    if missing_padding:
        data_str += "=" * (4 - missing_padding)
    return base64.urlsafe_b64decode(data_str)

def get_plain_text_from_payload(payload):
    """Extract text/plain content from Gmail payload"""
    if not payload:
        return ""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain" and payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        return decode_base64url(data).decode("utf-8", errors="ignore")

    for part in payload.get("parts", []) or []:
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return decode_base64url(part["body"]["data"]).decode("utf-8", errors="ignore")
        if part.get("parts"):
            text = get_plain_text_from_payload(part)
            if text:
                return text
    return ""

def get_message_headers(msg):
    headers = {}
    for h in msg.get("payload", {}).get("headers", []):
        name = h.get("name", "").lower()
        if name in ("from", "subject", "date", "to"):
            headers[name] = h.get("value")
    return headers

# ---------------------- FILTER FUNCTION ----------------------
def filter_emails(filters):
    """
    filters = {
        "start_date": "2025-09-01",
        "end_date": "2025-09-30",
        "name": "Raj",
        "limit": None,
        "subject": None
    }
    """

    # clean_json = re.sub(r"^```json\s*|\s*```$", "", filters.strip())
    # filters = json.loads(clean_json)
    print(filters,type(filters))
    q=[]
    for key,val in filters.items():
        print(key,val)
        if val != None:
            q.append(f"{key}:{val} ")

    print(q)
    query = "".join(q)
    print("our query is :- ",query)


    service = build_service()

    # # ------------------- BUILD QUERY -------------------
    # query_parts = []

    # # Inclusive date filter
    # if filters.get("start_date") and filters.get("end_date"):
    #     start = datetime.strptime(filters["start_date"], "%Y-%m-%d") - timedelta(days=1)
    #     end = datetime.strptime(filters["end_date"], "%Y-%m-%d") + timedelta(days=1)
    #     query_parts.append(f"after:{start.strftime('%Y/%m/%d')} before:{end.strftime('%Y/%m/%d')}")
    # elif filters.get("start_date"):
    #     start = datetime.strptime(filters["start_date"], "%Y-%m-%d") - timedelta(days=1)
    #     query_parts.append(f"after:{start.strftime('%Y/%m/%d')}")
    # elif filters.get("end_date"):
    #     end = datetime.strptime(filters["end_date"], "%Y-%m-%d") + timedelta(days=1)
    #     query_parts.append(f"before:{end.strftime('%Y/%m/%d')}")

    # # Subject filter
    # if filters.get("subject"):
    #     query_parts.append(f'subject:"{filters["subject"]}"')

    # # Name filter (we’ll manually check this later)
    # name_filter = filters.get("name")

    # # Combine query parts
    # query = " ".join(query_parts).strip()
    # print(f"🔍 Gmail Search Query: {query or '(none, fetching all)'}")

    # ------------------- FETCH EMAILS -------------------
    limit = filters.get("limit")
    max_results = int(limit) if limit else 100  # default: 100
    res = service.users().messages().list(userId="me", maxResults=max_results, q=query).execute()

    messages = res.get("messages", [])
    if not messages:
        print("⚠️ No messages found for this filter.")
        return
    
    result = []
    result.append(f"Found {len(messages)} messages. Filtering results...")
    print(f"📨 Found {len(messages)} messages. Filtering results...")
    print("------------------------------------------------------------")

    for msg_meta in messages:
        msg_id = msg_meta["id"]
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = get_message_headers(msg)

        sender = headers.get("from", "(unknown)")
        subject = headers.get("subject", "(no subject)")
        date = headers.get("date", "(no date)")
        body_text = get_plain_text_from_payload(msg.get("payload"))

        # If name filter is provided, check if it matches sender
        # if name_filter and name_filter.lower() not in sender.lower():
        #     continue  # skip non-matching senders

        result.append(f"📧 ID: {msg_id}")
        print(f"📧 ID: {msg_id}")
        result.append(f"From: {sender}")
        print(f"From: {sender}")
        result.append(f"Subject: {subject}")
        print(f"Subject: {subject}")
        result.append(f"Date: {date}")
        print(f"Date: {date}")
        result.append(f"Body preview : {body_text[:300]}")
        print("Body preview:")
        print(body_text[:300])  # only first 300 chars
        print("------------------------------------------------------------")
    return result

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    # 1️⃣ Send a test email
    # send_email("sameerkhan1ssk1@gmail.com", "Test from Agent", "This is a test email!")

    # 2️⃣ Example filter usage
    filters = {
        "start_date": "2025-09-01",
        "end_date": "2025-09-30",
        "name": "Raj",
        "limit": None,
        "subject": None
    }

    filter_emails(filters)
