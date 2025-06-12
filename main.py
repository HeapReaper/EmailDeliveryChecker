import smtplib
import imaplib
import email
import datetime
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

code = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def send_test_email(to_address, code):
    msg = f"Subject: SMTP Test {code}\n\nDit is een testmail met code: {code}"
    with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        server.sendmail(os.getenv('SMTP_USER'), os.getenv('TO_ADDRESS'), msg)

def check_mail(to_address, code):
    with imaplib.IMAP4_SSL(os.getenv('IMAP_SERVER')) as mail:
        mail.login(os.getenv('IMAP_USER'), os.getenv('IMAP_PASS'))
        mail.select('inbox')

        result, data = mail.search(None, 'ALL')
        for num in data[0].split()[::-1]:  # Recente mails eerst
            result, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = msg['Subject']

            if code in subject:
                return True

    return False

def send_webhook_alert(to_address, code):
    data = {"content": f"SMTP-monitor: Mail van '{to_address}' met code '{code}' is NIET aangekomen!"}
    requests.post(os.getenv('WEBHOOK_URL'), json=data)

send_test_email(os.getenv('TO_ADDRESS'), code)
print(f"Testmail verzonden met code: {code}")

time.sleep(10)

if not check_mail(os.getenv('TO_ADDRESS'), code):
    send_webhook_alert(os.getenv('TO_ADDRESS'), code)
    print("Webhook verzonden")
else:
    print("Mail is aangekomen")
