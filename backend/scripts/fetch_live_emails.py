import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

username = os.getenv("EMAIL_SURYA", "suryaramisetty70@gmail.com")
password = os.getenv("EMAIL_PASS_SURYA")

def clean_text(text):
    if text:
        return text.replace('\n', ' ').replace('\r', '')
    return text

def fetch_live_emails():
    print(f"--- LIVE EMAIL MONITORING ---")
    print(f"Connecting to {username} via IMAP...")
    
    try:
        # Connect to Gmail IMAP
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        print("✅ Login successful! Switching to LIVE MODE.")
        
        # Select inbox
        status, messages = imap.select("INBOX")
        if status != "OK":
            print("Failed to select inbox.")
            return
            
        print("Scanning for unread emails...")
        # Search for unread emails
        status, response = imap.search(None, 'UNSEEN')
        if status != "OK":
            print("No new emails found.")
            return
            
        unread_msg_nums = response[0].split()
        print(f"Found {len(unread_msg_nums)} unread emails. Running through AI Importance Filter...\n")
        
        if not unread_msg_nums:
            print("Inbox is clear. No new unread messages.")
        else:
            # Fetch the top 3 most recent unread
            for num in unread_msg_nums[-3:]:
                res, msg_data = imap.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                            
                        # Decode sender
                        from_ = msg.get("From")
                        
                        print("=" * 50)
                        print(f"🚨 NEW LIVE EMAIL DETECTED 🚨")
                        print(f"From: {from_}")
                        print(f"Subject: {subject}")
                        print("=" * 50)
                        print("AI Action: Awaiting your permission to read full body and reply.\n")
                        
        imap.close()
        imap.logout()
        
    except Exception as e:
        print(f"❌ Error connecting to live inbox: {e}")
        print("Make sure IMAP is enabled in your Gmail settings and the App Password is correct.")

if __name__ == "__main__":
    fetch_live_emails()
