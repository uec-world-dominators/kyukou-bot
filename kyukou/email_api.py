from email.mime.text import MIMEText
import smtplib
import requests
import time
from . import certificate
import hashlib

if __name__ != '__main__':
    from .settings import settings
    from .db import get_collection
    users_db = get_collection('users')


def register(o):
    if "email_addr" in o and not users_db.find_one({"connections.email.email_addr": o["email_addr"], "connections.email.validated": True}):
        password_hash = hashlib.sha256((o["password"]+settings["hash_salt"] or '').encode()).hexdigest()
        users_db.insert_one({
            "connections": {
                "email": {
                    "email_addr": o["email_addr"],
                    "name": o["name"],
                    "password_hash": password_hash,
                    "varidated": False,
                }
            },
            "length": 1
        })
        return True
    else:
        return False


def send_mails(msgs):
    server = smtplib.SMTP(settings["email"]["smtp_server"], settings["email"]["smtp_port"])
    server.login(settings["email"]["from_addr"], settings["email"]["password"])
    for msg in msgs:
        server.send_message(msg)
    server.quit()


def make_message(to_addr, subject, content):
    msg = MIMEText(content, "html")
    msg["Subject"] = subject
    msg["To"] = to_addr
    msg["From"] = settings["email"]["from_addr"]
    return msg
