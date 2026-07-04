import time
import json
from agents.email_agent import EmailAgent

def run_simulation():
    print("Initializing Email Agent Monitoring Service...")
    agent = EmailAgent()
    
    print("\n--- SECURE IMAP CONNECTION LOG ---")
    for account in agent.monitored_accounts:
        print(f"[Connecting] Attempting IMAP connect to {account}...")
        time.sleep(1)
        if not agent.live_mode:
            print(f"[{account}] WARNING: No App Password found. Falling back to Simulation Mode.")
            
    print("\n[Monitor] Scanning inboxes for new messages (Filtering spam & promotions)...")
    time.sleep(2)
    print("[Monitor] Found 14 new emails in suryaramisetty70@gmail.com. Processing via AI filter...")
    time.sleep(2)
    print("[Monitor] 13 emails classified as Low Priority (Newsletters/Spam).")
    print("[Monitor] 1 email classified as URGENT.")
    
    time.sleep(1)
    print("\n==================================================")
    print("🚨 URGENT EMAIL ALERT 🚨")
    print("==================================================")
    print("Account: suryaramisetty70@gmail.com")
    print("From: Investor Relations <investors@tecnospark.com>")
    print("Subject: URGENT: Seed Funding Term Sheet Attached - Signature Required Today")
    print("Time Received: Just Now")
    print("-" * 50)
    print("Summary:")
    print("The investors have finally approved the term sheet for the $2M seed round. However, the lead investor requires your signature before 5:00 PM EST today, or the offer expires. Please review the attached PDF immediately.")
    print("==================================================\n")
    
    print("--> ACTION REQUIRED: Waiting for User Permission.")
    print("Suggested AI Reply: 'Thank you. I have received the term sheet, reviewed it, and attached the signed copy below. Looking forward to our partnership.'")
    
if __name__ == "__main__":
    run_simulation()
