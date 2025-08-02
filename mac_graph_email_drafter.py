import msal
import requests
import json
import time
import re
from ollama import chat

# === CONFIG ===
CLIENT_ID = "INSERT CLIENT_ID HERE"
AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = [
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send"
]
DATASET_PATH = "email_reply_dataset.json"
OLLAMA_MODEL = "llama3"

def acquire_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise ValueError("Device flow initiation failed")
        print(f"[INFO] Vai su {flow['verification_uri']} e inserisci il codice: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Token acquisition failed: {result}")

def load_style_dataset():
    with open(DATASET_PATH) as f:
        return json.load(f)

def prompt_llm(user_email_body, recipient, dataset):
    examples = [
        f"Email:\n{item['email_body']}\nReply:\n{item['my_reply']}"
        for item in dataset if item["recipient"] == recipient
    ]

    few_shot = "\n\n".join(examples[-3:])  # Usa ultimi 3 esempi
    prompt = f"""{few_shot}

Email:
{user_email_body}

Reply:"""

    response = chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def fetch_unread_emails(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/mailFolders('inbox')/messages?$filter=isRead eq false&$top=5"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Fetch failed: {r.status_code} - {r.text}")
    return r.json().get("value", [])

def create_draft_reply(token, to_address, subject, body):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    draft_payload = {
        "subject": f"RE: {subject}",
        "body": {
            "contentType": "Text",
            "content": body
        },
        "toRecipients": [
            {"emailAddress": {"address": to_address}}
        ],
        "isDraft": True
    }
    url = "https://graph.microsoft.com/v1.0/me/messages"
    r = requests.post(url, headers=headers, data=json.dumps(draft_payload))
    if r.status_code not in [201, 200]:
        raise Exception(f"Draft creation failed: {r.status_code} - {r.text}")
    print(f"[INFO] Bozza creata per: {to_address}")


def run_draft_pipeline():
    token = acquire_token()
    dataset = load_style_dataset()
    new_emails = fetch_unread_emails(token)

    print(f"[INFO] Trovate {len(new_emails)} nuove email non lette")

    for mail in new_emails:
        from_addr = mail["from"]["emailAddress"]["address"]
        subject = mail.get("subject", "(no subject)")
        body_html = mail.get("body", {}).get("content", "")
        body_text = re.sub(r'<[^>]+>', '', body_html)  # HTML → testo

        print(f"\n[INFO] Rispondendo a: {from_addr} | Oggetto: {subject}")

        reply = prompt_llm(body_text.strip(), from_addr, dataset)
        create_draft_reply(token, from_addr, subject, reply)
        time.sleep(2)  # Evita rate limiting

if __name__ == "__main__":
    run_draft_pipeline()
