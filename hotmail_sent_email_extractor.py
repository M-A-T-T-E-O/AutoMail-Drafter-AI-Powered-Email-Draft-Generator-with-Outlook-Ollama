
import msal
import requests
import json

# === CONFIG ===
CLIENT_ID = "INSERT CLIENT_ID HERE"
AUTHORITY = "https://login.microsoftonline.com/consumers"  # Per Hotmail/Outlook personale
SCOPES = [
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send"
]
REDIRECT_URI = "http://localhost:8000"
DATASET_PATH = "email_reply_dataset.json"
MAX_EMAILS = 100

def acquire_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise ValueError("Device flow initiation failed")

        print(f"[INFO] Please go to {flow['verification_uri']} and enter the code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        print("[INFO] Token acquired.")
        return result["access_token"]
    else:
        raise Exception(f"[ERROR] Token acquisition failed: {result}")

def fetch_sent_items(token):
    print("[INFO] Fetching sent emails...")
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/mailFolders('sentitems')/messages?$top=100"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise Exception(f"[ERROR] Failed to fetch messages: {r.status_code} - {r.text}")

    messages = r.json().get("value", [])
    dataset = []

    for msg in messages:
        body = msg.get("body", {}).get("content", "")
        to = msg.get("toRecipients", [])
        if not body or not to:
            continue
        recipient = to[0].get("emailAddress", {}).get("address", "")
        subject = msg.get("subject", "(no subject)")

        dataset.append({
            "email_body": f"Simulated original message based on subject: {subject}",
            "my_reply": body.strip(),
            "recipient": recipient
        })

    with open(DATASET_PATH, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"[INFO] Saved {len(dataset)} emails to {DATASET_PATH}")

if __name__ == "__main__":
    token = acquire_token()
    fetch_sent_items(token)
