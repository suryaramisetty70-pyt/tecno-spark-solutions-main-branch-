"""
Email Agent - Manages email sending, receiving, and thread management
Integrates with Gmail, Outlook, and other email providers
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from agents.base_agent import BaseAgent, AgentStatus, Tool

logger = logging.getLogger(__name__)


class EmailAgent(BaseAgent):
    """Manages all email-related operations"""

    def __init__(self):
        super().__init__(
            agent_id="email_agent",
            name="Email Agent",
            description="Manages your emails and email integrations",
            version="0.1.0"
        )

        self.capabilities = [
            {
                "category": "communication",
                "skills": ["email_send", "email_receive", "thread_management"],
                "priority": 8
            }
        ]

        # Registered Monitored Accounts
        self.monitored_accounts = [
            "suryaramisetty70@gmail.com",
            "vtu27657@veltech.edu.in"
        ]
        self.live_mode = False # Requires App Passwords to switch to True

        self.tools = self._initialize_tools()
        self._initialize_permissions()
        self.logger.info("✅ Email Agent initialized with 2 monitored accounts (Simulation Mode)")

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="send_email",
                description="Send an email",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "cc": {"type": "array"},
                        "bcc": {"type": "array"}
                    },
                    "required": ["to", "subject", "body"]
                },
                execute_fn=self._send_email
            ),
            Tool(
                name="receive_emails",
                description="Fetch received emails",
                input_schema={
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string"},
                        "limit": {"type": "integer"}
                    }
                },
                execute_fn=self._receive_emails
            ),
            Tool(
                name="search_emails",
                description="Search for emails",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "from": {"type": "string"}
                    },
                    "required": ["query"]
                },
                execute_fn=self._search_emails
            )
        ]

    def _initialize_permissions(self) -> None:
        for perm in ["send_email", "read_email", "delete_email", "connect_email_account"]:
            self.grant_permission(perm)

    def register_tools(self) -> List[Tool]:
        return self.tools

    async def process_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(AgentStatus.PROCESSING)
        try:
            intent_lower = intent.lower()
            if "send" in intent_lower and "email" in intent_lower:
                return {"status": "success", "action": "send_email", "response": "I'll help you send an email."}
            elif "email" in intent_lower and any(w in intent_lower for w in ["check", "get", "receive", "read"]):
                return {"status": "success", "action": "receive_emails", "response": "Let me check your emails."}
            return {"status": "success", "response": f"Email: {intent}"}
        except Exception as e:
            return await self.handle_error(e)
        finally:
            await self.set_state(AgentStatus.SUCCESS)

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "send_email":
            return await self._send_email(parameters)
        elif action == "receive_emails":
            return await self._receive_emails(parameters)
        return {"status": "error", "error": f"Unknown action: {action}"}

    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import smtplib
        from email.mime.text import MIMEText
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        email_user = os.getenv("GMAIL_USER")
        email_pass = os.getenv("GMAIL_APP_PASSWORD")
        
        if not email_user or not email_pass:
            return {"status": "error", "message": "GMAIL_USER or GMAIL_APP_PASSWORD not set in .env"}
            
        try:
            msg = MIMEText(params.get("body", ""))
            msg['Subject'] = params.get("subject", "")
            msg['From'] = email_user
            msg['To'] = params.get("to", "")
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(email_user, email_pass)
                server.send_message(msg)
                
            return {
                "status": "success",
                "to": params.get("to"),
                "subject": params.get("subject"),
                "sent_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _receive_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import imaplib
        import email
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        email_user = os.getenv("GMAIL_USER")
        email_pass = os.getenv("GMAIL_APP_PASSWORD")
        
        if not email_user or not email_pass:
            return {"status": "error", "message": "GMAIL_USER or GMAIL_APP_PASSWORD not set in .env"}
            
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email_user, email_pass)
            mail.select(params.get("folder", "inbox"))
            
            # Search for all unread emails
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            limit = params.get("limit", 5)
            fetched_emails = []
            
            for eid in email_ids[-limit:]:
                _, msg_data = mail.fetch(eid, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg['subject']
                        sender = msg['from']
                        fetched_emails.append({"from": sender, "subject": subject})
                        
            mail.close()
            mail.logout()
            
            return {
                "status": "success",
                "folder": params.get("folder", "inbox"),
                "emails": fetched_emails,
                "count": len(fetched_emails)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": "Search feature requires IMAP Search logic. Use receive_emails for now."
        }
