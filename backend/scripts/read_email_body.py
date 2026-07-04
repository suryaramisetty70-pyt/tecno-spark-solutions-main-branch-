import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("EMAIL_SURYA")
password = os.getenv("EMAIL_PASS_SURYA")

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                try:
                    return part.get_payload(decode=True).decode()
                except:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode()
        except:
            return msg.get_payload()

def read_latest_email():
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        imap.select("INBOX")
        
        status, response = imap.search(None, 'UNSEEN')
        unread_msg_nums = response[0].split()
        
        if unread_msg_nums:
            # Get the LinkedIn "new message" email which was the 3rd from the end in the previous output (index -3)
            # Actually, let's just fetch the last 5 and find the one with "You have 1 new message"
            for num in reversed(unread_msg_nums[-5:]):
                res, msg_data = imap.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                            
                        if "You have 1 new message" in subject:
                            body = get_body(msg)
                            print("=== EMAIL BODY ===")
                            if body:
                                print(body[:1500]) # Print up to 1500 chars
                            else:
                                print("No plain text body found. Could be HTML only.")
                            print("==================")
                            imap.close()
                            imap.logout()
                            return
            print("Could not find the LinkedIn email.")
        imap.close()
        imap.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_latest_email()
