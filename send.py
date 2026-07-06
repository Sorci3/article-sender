import json, os, smtplib, ssl, urllib.request
from email.message import EmailMessage
from pathlib import Path

# Secrets injectes par GitHub Actions (Settings > Secrets > Actions)
cfg = json.loads(Path("prompt.json").read_text(encoding="utf-8"))
API_KEY = os.environ["API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
MAIL_TO = os.environ.get("MAIL_TO", GMAIL_USER)

url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg['model']}:generateContent?key={API_KEY}"
body = {
    "contents": [{"parts": [{"text": cfg["prompt"]}]}],
    "tools": [{"google_search": {}}],  
}
req = urllib.request.Request(
    url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=120) as r:
    data = json.load(r)

parts = data["candidates"][0]["content"]["parts"]
article = "".join(p.get("text", "") for p in parts).strip()
assert article, f"Reponse vide: {json.dumps(data)[:500]}"

msg = EmailMessage()
msg["Subject"] = "Ton article allemand du jour"
msg["From"] = GMAIL_USER
msg["To"] = MAIL_TO
msg.set_content(article)

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
    s.login(GMAIL_USER, GMAIL_PASS)
    s.send_message(msg)

print("Envoye a", MAIL_TO)
