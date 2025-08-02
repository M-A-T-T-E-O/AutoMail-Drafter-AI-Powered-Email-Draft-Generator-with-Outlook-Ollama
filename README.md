# 🧠 AutoMail-Drafter

A local AI assistant for macOS that automatically generates personalized Outlook email drafts using your own historical replies.  
Built with [Ollama](https://ollama.com) and [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview).

---

## 🚀 Features

- 📨 **Extracts sent emails** to build a personal reply dataset  
- ✍️ **Generates reply drafts** for new emails using a local LLM (e.g., LLaMA3)
- 🔐 **Runs entirely locally** – no data sent to third-party servers
- 🛠️ **Configurable** dataset size and model
- 📥 Drafts are saved in your **Outlook Drafts** folder, never auto-sent

---

## 🧰 Requirements

- macOS
- Python 3.10+
- [Ollama](https://ollama.com) with a local model (e.g., `llama3`)
- A registered app on [Azure Portal](https://portal.azure.com/)  
  (to get your `CLIENT_ID` for Microsoft Graph API access)

---

## 🗂 Included Scripts

### `hotmail_sent_email_extractor.py`

Extracts up to 100 sent emails via Microsoft Graph and generates a dataset file:  
📄 `email_reply_dataset.json`

> ⚠️ Be sure to insert your `CLIENT_ID` before running.

---

### `mac_graph_email_drafter.py`

Fetches unread emails and uses a local LLM (via Ollama) to generate personalized drafts, saved in Outlook.

> ⚠️ Requires the dataset file from the extractor and your `CLIENT_ID`.

---

## ⚙️ Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Register an app on [Azure](https://portal.azure.com):
   - Redirect URI: `http://localhost`
   - Permissions:  
     `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`, `offline_access`

3. Add your `CLIENT_ID` in both scripts.

4. Run the extractor first:
   ```bash
   python hotmail_sent_email_extractor.py
   ```

5. Then run the drafter:
   ```bash
   python mac_graph_email_drafter.py
   ```

---

## 🧪 Status

This is a **work in progress** – functional but under active development.  
Contributions, feedback, and testing across different environments are welcome!

---

## 📜 License

MIT License

---

## 🤖 Credits

Built using:
- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/)
- [Ollama](https://ollama.com/)
- Inspired by inbox fatigue 😅
