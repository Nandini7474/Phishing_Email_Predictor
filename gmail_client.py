# gmail_client.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import base64
from bs4 import BeautifulSoup   # NEW

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def gmail_authenticate():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service


# def fetch_message_ids(service, max_results=20):
#     results = service.users().messages().list(
#         userId="me",
#         q="in:inbox",
#         maxResults=max_results
#     ).execute()

#     return results.get("messages", [])
def fetch_all_message_ids(service, max_pages=10):
    all_messages = []
    page_token = None
    page_count = 0

    while True:
        response = service.users().messages().list(
            userId="me",
            q="in:inbox",
            maxResults=500,        # maximum allowed
            pageToken=page_token
        ).execute()

        messages = response.get("messages", [])
        all_messages.extend(messages)

        page_token = response.get("nextPageToken")
        page_count += 1

        if not page_token:
            break

        if page_count >= max_pages:
            break  # safety guard

    return all_messages


# NEW helper function
def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ")


def read_email(service, msg_id):
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg["payload"]["headers"]
    subject = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]

    body = ""
    payload = msg["payload"]

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            data = part.get("body", {}).get("data")

            #  Prefer plain text
            if mime_type == "text/plain" and data:
                body = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
                break

            #  Fallback to HTML
            elif mime_type == "text/html" and not body and data:
                html = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
                body = html_to_text(html)

    return msg_id, subject, body

