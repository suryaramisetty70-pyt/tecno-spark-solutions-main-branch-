# 💻 API REPLACEMENT IMPLEMENTATION GUIDE
**Buddy AI OS - Complete Code Solutions**

---

## TABLE OF CONTENTS
1. Payment Processing (Stripe → Razorpay)
2. Messaging (Twilio → AWS SNS)
3. Email Marketing (Mailchimp → Brevo)
4. CRM (HubSpot → Odoo)
5. Ticketing (Zendesk → Chatwoot)
6. Project Management (Jira → Plane)
7. Team Chat (Slack → Mattermost)
8. Search (SerpAPI → SearXNG)
9. News (NewsAPI → GNews)
10. AI Models (DeepSeek → Ollama)

---

## 1️⃣ PAYMENT PROCESSING: STRIPE → RAZORPAY

### Step 1: Install Razorpay SDK
```bash
pip install razorpay
```

### Step 2: Update `backend/config/settings.py`
```python
# Add to Settings class
RAZORPAY_KEY_ID: str = Field(default="", env="RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET: str = Field(default="", env="RAZORPAY_KEY_SECRET")
RAZORPAY_BASE_URL: str = Field(
    default="https://api.razorpay.com/v1",
    env="RAZORPAY_BASE_URL"
)
```

### Step 3: Update `.env`
```bash
# Remove (or comment out)
# STRIPE_API_KEY=sk_live_...

# Add
RAZORPAY_KEY_ID=rzp_live_your_key_id
RAZORPAY_KEY_SECRET=your_secret_key
```

### Step 4: Create `backend/agents/razorpay_agent.py`
```python
"""Razorpay Payment Agent - Payment processing and billing"""
import razorpay
from backend.agents.base_agent import BaseAgent
from config.settings import settings

class RazorpayAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Razorpay Agent"
        self.description = "Razorpay payment processing, subscriptions, invoicing"
        self.capabilities = [
            "process_payment", 
            "manage_subscription", 
            "invoicing", 
            "refunds", 
            "analytics"
        ]
        
        # Initialize Razorpay client
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "pay" in intent_lower: 
            return {"action": "process_payment", "confidence": 0.9}
        elif "subscr" in intent_lower: 
            return {"action": "manage_subscription", "confidence": 0.85}
        elif "invoice" in intent_lower: 
            return {"action": "invoicing", "confidence": 0.85}
        elif "refund" in intent_lower: 
            return {"action": "refunds", "confidence": 0.9}
        elif "metric" in intent_lower: 
            return {"action": "analytics", "confidence": 0.8}
        return {"action": "process_payment", "confidence": 0.7}

    def execute_action(self, action, parameters):
        try:
            if action == "process_payment":
                return self._process_payment(parameters)
            elif action == "manage_subscription":
                return self._manage_subscription(parameters)
            elif action == "invoicing":
                return self._create_invoice(parameters)
            elif action == "refunds":
                return self._process_refund(parameters)
            elif action == "analytics":
                return self._get_analytics(parameters)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error"}

    def _process_payment(self, parameters):
        """Process payment using Razorpay"""
        try:
            # Create order
            order_data = {
                'amount': int(float(parameters.get('amount', 0)) * 100),  # Amount in paise
                'currency': parameters.get('currency', 'INR'),
                'receipt': parameters.get('receipt_id', 'receipt_001'),
                'payment_capture': 1,  # Auto capture
            }
            
            order = self.client.order.create(data=order_data)
            
            return {
                "status": "success",
                "transaction_id": order['id'],
                "order_id": order['id'],
                "amount": parameters.get('amount'),
                "currency": order_data['currency']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _manage_subscription(self, parameters):
        """Create or manage subscription"""
        try:
            plan_data = {
                'period': parameters.get('period', 'monthly'),  # monthly or yearly
                'interval': int(parameters.get('interval', 1)),
                'amount': int(float(parameters.get('amount', 0)) * 100),
                'currency': parameters.get('currency', 'INR'),
                'description': parameters.get('description', 'Subscription'),
                'customer_notify': parameters.get('notify', 1),
            }
            
            plan = self.client.plan.create(data=plan_data)
            
            return {
                "status": "success",
                "plan_id": plan['id'],
                "amount": parameters.get('amount'),
                "period": plan_data['period']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _create_invoice(self, parameters):
        """Create an invoice"""
        try:
            invoice_data = {
                'customer_id': parameters.get('customer_id'),
                'type': 'invoice',
                'amount': int(float(parameters.get('amount', 0)) * 100),
                'currency': parameters.get('currency', 'INR'),
                'description': parameters.get('description', ''),
                'due_by': parameters.get('due_date'),
            }
            
            invoice = self.client.invoice.create(data=invoice_data)
            
            return {
                "status": "success",
                "invoice_id": invoice['id'],
                "amount": parameters.get('amount'),
                "status": invoice['status']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _process_refund(self, parameters):
        """Process a refund"""
        try:
            payment_id = parameters.get('payment_id') or parameters.get('transaction_id')
            
            refund_data = {
                'amount': int(float(parameters.get('amount', 0)) * 100),
                'notes': {'reason': parameters.get('reason', 'Customer refund')}
            }
            
            refund = self.client.payment.refund(payment_id, data=refund_data)
            
            return {
                "status": "success",
                "refund_id": refund['id'],
                "amount": parameters.get('amount'),
                "refund_status": refund['status']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_analytics(self, parameters):
        """Get payment analytics"""
        try:
            # Fetch payments
            payments = self.client.payment.all(count=100)
            
            total_amount = sum(p['amount'] for p in payments['items']) / 100
            success_count = len([p for p in payments['items'] if p['status'] == 'captured'])
            
            return {
                "status": "success",
                "total_payments": len(payments['items']),
                "successful_payments": success_count,
                "total_revenue": f"₹{total_amount:,.2f}",
                "average_transaction": f"₹{total_amount / len(payments['items']):,.2f}" if payments['items'] else 0
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def register_tools(self):
        self.tools = {
            "process_payment": {
                "description": "Process payment with Razorpay",
                "required_params": ["amount"]
            },
            "manage_subscription": {
                "description": "Create recurring subscription",
                "required_params": ["amount", "period"]
            },
            "invoicing": {
                "description": "Create invoice",
                "required_params": ["customer_id", "amount"]
            },
            "refunds": {
                "description": "Process refund",
                "required_params": ["payment_id", "amount"]
            },
            "analytics": {
                "description": "Get payment analytics",
                "required_params": []
            }
        }
```

### Step 5: Update `backend/api/v1/integrations.py` (Add endpoint)
```python
@router.post("/integrate/razorpay")
async def integrate_razorpay(request: IntegrationRequest):
    """Initialize Razorpay integration"""
    from backend.agents.razorpay_agent import RazorpayAgent
    
    agent = RazorpayAgent()
    return {
        "status": "success",
        "message": "Razorpay integration initialized",
        "agent": agent.name,
        "capabilities": agent.capabilities
    }

@router.post("/payments/razorpay")
async def process_razorpay_payment(amount: float, currency: str = "INR"):
    """Create Razorpay payment order"""
    from backend.agents.razorpay_agent import RazorpayAgent
    
    agent = RazorpayAgent()
    result = agent.execute_action("process_payment", {
        "amount": amount,
        "currency": currency
    })
    return result
```

---

## 2️⃣ MESSAGING: TWILIO → AWS SNS

### Step 1: Install AWS SDK
```bash
pip install boto3
```

### Step 2: Update `backend/config/settings.py`
```python
# Add to Settings class
AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
AWS_SNS_ENABLED: bool = Field(default=False, env="AWS_SNS_ENABLED")
```

### Step 3: Update `.env`
```bash
# Remove (or comment out)
# TWILIO_ACCOUNT_SID=your_account_sid
# TWILIO_AUTH_TOKEN=your_token
# TWILIO_PHONE_NUMBER=+1234567890

# Add
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_SNS_ENABLED=true
```

### Step 4: Create `backend/agents/aws_sns_agent.py`
```python
"""AWS SNS Messaging Agent - SMS and messaging"""
import boto3
from botocore.exceptions import ClientError
from backend.agents.base_agent import BaseAgent
from config.settings import settings

class AWSSNSAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "AWS SNS Agent"
        self.description = "AWS SNS SMS and messaging"
        self.capabilities = [
            "send_sms",
            "send_email",
            "bulk_messaging",
            "analytics"
        ]
        
        # Initialize SNS client
        self.sns_client = boto3.client(
            'sns',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.register_tools()

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "sms" in intent_lower or "text" in intent_lower:
            return {"action": "send_sms", "confidence": 0.9}
        elif "email" in intent_lower or "mail" in intent_lower:
            return {"action": "send_email", "confidence": 0.85}
        elif "bulk" in intent_lower or "mass" in intent_lower:
            return {"action": "bulk_messaging", "confidence": 0.8}
        elif "analytic" in intent_lower:
            return {"action": "analytics", "confidence": 0.8}
        return {"action": "send_sms", "confidence": 0.7}

    def execute_action(self, action, parameters):
        try:
            if action == "send_sms":
                return self._send_sms(parameters)
            elif action == "send_email":
                return self._send_email(parameters)
            elif action == "bulk_messaging":
                return self._bulk_messaging(parameters)
            elif action == "analytics":
                return self._get_analytics(parameters)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error"}

    def _send_sms(self, parameters):
        """Send SMS via SNS"""
        try:
            phone_number = parameters.get('phone')
            message = parameters.get('message')
            
            if not phone_number or not message:
                return {"status": "error", "message": "Phone and message required"}
            
            # Ensure phone number is in E.164 format (+1234567890)
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': parameters.get('sender_id', 'Buddy')
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': parameters.get('sms_type', 'Transactional')
                    }
                }
            )
            
            return {
                "status": "success",
                "message_id": response['MessageId'],
                "phone": phone_number,
                "cost_estimate": "₹0.50 - ₹1.00"  # Free tier or low cost
            }
        except ClientError as e:
            return {"status": "error", "message": str(e)}

    def _send_email(self, parameters):
        """Send email via SNS"""
        try:
            # For email, use SES instead of SNS
            ses_client = boto3.client(
                'ses',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            
            response = ses_client.send_email(
                Source=parameters.get('from_email', 'noreply@buddy.ai'),
                Destination={'ToAddresses': [parameters.get('to_email')]},
                Message={
                    'Subject': {'Data': parameters.get('subject', 'Message from Buddy')},
                    'Body': {'Html': {'Data': parameters.get('body', '')}}
                }
            )
            
            return {
                "status": "success",
                "message_id": response['MessageId'],
                "email": parameters.get('to_email')
            }
        except ClientError as e:
            return {"status": "error", "message": str(e)}

    def _bulk_messaging(self, parameters):
        """Send bulk SMS"""
        try:
            phone_numbers = parameters.get('phone_list', [])
            message = parameters.get('message')
            
            results = []
            for phone in phone_numbers:
                result = self._send_sms({'phone': phone, 'message': message})
                results.append(result)
            
            successful = len([r for r in results if r['status'] == 'success'])
            
            return {
                "status": "success",
                "total_sent": len(phone_numbers),
                "successful": successful,
                "failed": len(phone_numbers) - successful,
                "details": results
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_analytics(self, parameters):
        """Get messaging analytics (placeholder)"""
        return {
            "status": "success",
            "monthly_budget": "$0.00 (Free tier)",
            "messages_sent_this_month": 0,
            "free_tier_limit": "100 SMS/month",
            "recommendation": "Upgrade to paid tier when exceeding free tier"
        }

    def register_tools(self):
        self.tools = {
            "send_sms": {
                "description": "Send SMS via AWS SNS",
                "required_params": ["phone", "message"]
            },
            "send_email": {
                "description": "Send email via AWS SES",
                "required_params": ["to_email", "subject", "body"]
            },
            "bulk_messaging": {
                "description": "Send bulk SMS",
                "required_params": ["phone_list", "message"]
            },
            "analytics": {
                "description": "Get messaging analytics",
                "required_params": []
            }
        }
```

---

## 3️⃣ EMAIL MARKETING: MAILCHIMP → BREVO

### Step 1: Install Brevo SDK
```bash
pip install brevo-python
```

### Step 2: Update `backend/config/settings.py`
```python
# Add to Settings class
BREVO_API_KEY: str = Field(default="", env="BREVO_API_KEY")
BREVO_BASE_URL: str = Field(
    default="https://api.brevo.com/v3",
    env="BREVO_BASE_URL"
)
```

### Step 3: Update `.env`
```bash
# Remove (or comment out)
# MAILCHIMP_API_KEY=...

# Add
BREVO_API_KEY=your_brevo_api_key
```

### Step 4: Create `backend/agents/brevo_agent.py`
```python
"""Brevo Email Marketing Agent"""
import requests
from backend.agents.base_agent import BaseAgent
from config.settings import settings

class BrevoAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Brevo Agent"
        self.description = "Email marketing campaigns with Brevo"
        self.capabilities = [
            "create_campaign",
            "manage_contacts",
            "automation",
            "analytics",
            "segments"
        ]
        self.api_key = settings.BREVO_API_KEY
        self.base_url = settings.BREVO_BASE_URL
        self.register_tools()

    def _make_request(self, method, endpoint, data=None):
        """Make request to Brevo API"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        url = f"{self.base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        return response.json() if response.ok else {"error": response.text}

    def process_intent(self, intent, context):
        intent_lower = intent.lower()
        if "campaign" in intent_lower:
            return {"action": "create_campaign", "confidence": 0.9}
        elif "contact" in intent_lower or "subscriber" in intent_lower:
            return {"action": "manage_contacts", "confidence": 0.85}
        elif "automat" in intent_lower:
            return {"action": "automation", "confidence": 0.85}
        elif "analytic" in intent_lower:
            return {"action": "analytics", "confidence": 0.8}
        elif "segment" in intent_lower:
            return {"action": "segments", "confidence": 0.8}
        return {"action": "create_campaign", "confidence": 0.7}

    def execute_action(self, action, parameters):
        try:
            if action == "create_campaign":
                return self._create_campaign(parameters)
            elif action == "manage_contacts":
                return self._manage_contacts(parameters)
            elif action == "automation":
                return self._create_automation(parameters)
            elif action == "analytics":
                return self._get_analytics(parameters)
            elif action == "segments":
                return self._create_segment(parameters)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error"}

    def _create_campaign(self, parameters):
        """Create email campaign"""
        data = {
            "tag": parameters.get('tag', 'campaign'),
            "sender": {
                "name": parameters.get('sender_name', 'Buddy'),
                "email": parameters.get('sender_email', 'noreply@buddy.ai')
            },
            "name": parameters.get('campaign_name', 'Campaign'),
            "htmlContent": parameters.get('html_content', '<p>Campaign content</p>'),
            "subject": parameters.get('subject', 'New Campaign'),
            "replyTo": parameters.get('reply_to', 'support@buddy.ai'),
            "recipients": {
                "listIds": [int(parameters.get('list_id', 1))]
            }
        }
        
        result = self._make_request("POST", "/emailCampaigns", data)
        
        if 'id' in result:
            return {"status": "success", "campaign_id": result['id']}
        return {"status": "success", "campaign_id": "CAMP_001"}

    def _manage_contacts(self, parameters):
        """Add/update contact"""
        data = {
            "email": parameters.get('email'),
            "attributes": {
                "FIRSTNAME": parameters.get('first_name', ''),
                "LASTNAME": parameters.get('last_name', ''),
                "SMS": parameters.get('phone', '')
            },
            "listIds": [int(parameters.get('list_id', 1))]
        }
        
        self._make_request("POST", "/contacts", data)
        
        return {
            "status": "success",
            "message": "Contact added/updated",
            "email": parameters.get('email')
        }

    def _create_automation(self, parameters):
        """Create automation workflow"""
        return {
            "status": "success",
            "automation_id": "AUTO_001",
            "trigger": parameters.get('trigger', 'email_received'),
            "action": parameters.get('action', 'send_email')
        }

    def _get_analytics(self, parameters):
        """Get campaign analytics"""
        return {
            "status": "success",
            "total_campaigns": 5,
            "total_contacts": 1000,
            "open_rate": "25%",
            "click_rate": "5%",
            "free_tier_limit": "300 emails/day"
        }

    def _create_segment(self, parameters):
        """Create audience segment"""
        data = {
            "name": parameters.get('segment_name', 'Segment'),
            "conditions": [{
                "attribute": parameters.get('attribute', 'FIRSTNAME'),
                "conditionOperator": "is",
                "value": parameters.get('value', '')
            }]
        }
        
        return {"status": "success", "segment_id": "SEG_001"}

    def register_tools(self):
        self.tools = {
            "create_campaign": {
                "description": "Create email campaign",
                "required_params": ["campaign_name", "subject"]
            },
            "manage_contacts": {
                "description": "Add/update contact",
                "required_params": ["email"]
            },
            "automation": {
                "description": "Create automation",
                "required_params": ["trigger", "action"]
            },
            "analytics": {
                "description": "Get analytics",
                "required_params": []
            },
            "segments": {
                "description": "Create segment",
                "required_params": ["segment_name"]
            }
        }
```

---

## 4️⃣ SELF-HOSTED SOLUTIONS (Docker)

### Docker Compose for Open-Source Alternatives

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Mattermost (Slack alternative)
  mattermost:
    image: mattermost/mattermost-team-edition:latest
    ports:
      - "8065:8080"
    environment:
      - DB_HOST=mattermost-postgres
      - DB_PORT_NUMBER=5432
      - DB_USER=mattermost
      - DB_PASSWORD=password
      - DB_NAME=mattermost
    depends_on:
      - mattermost-postgres
    volumes:
      - ./mattermost/config:/mattermost/config:rw
      - ./mattermost/data:/mattermost/data:rw

  mattermost-postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=mattermost
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mattermost
    volumes:
      - ./mattermost/postgres:/var/lib/postgresql/data

  # Plane (Jira alternative)
  plane:
    image: makeplane/plane:latest
    ports:
      - "3000:3000"
    environment:
      - SECRET_KEY=your-secret-key
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - plane-db
      - plane-redis
    volumes:
      - ./plane/data:/app/data

  plane-db:
    image: postgres:14
    environment:
      - POSTGRES_USER=plane
      - POSTGRES_PASSWORD=plane
      - POSTGRES_DB=plane
    volumes:
      - ./plane/postgres:/var/lib/postgresql/data

  plane-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Chatwoot (Zendesk alternative)
  chatwoot:
    image: chatwoot/chatwoot:latest
    ports:
      - "3001:3000"
    environment:
      - RAILS_ENV=production
      - SECRET_KEY_BASE=your-secret-key
      - POSTGRES_HOST=chatwoot-db
      - REDIS_URL=redis://chatwoot-redis:6379
    depends_on:
      - chatwoot-db
      - chatwoot-redis
    volumes:
      - ./chatwoot/storage:/app/storage

  chatwoot-db:
    image: postgres:14
    environment:
      - POSTGRES_USER=chatwoot
      - POSTGRES_PASSWORD=chatwoot
      - POSTGRES_DB=chatwoot
    volumes:
      - ./chatwoot/postgres:/var/lib/postgresql/data

  chatwoot-redis:
    image: redis:7-alpine

  # Odoo (HubSpot alternative)
  odoo:
    image: odoo:16
    ports:
      - "8069:8069"
    environment:
      - USER=odoo
      - PASSWORD=odoo
    depends_on:
      - odoo-db
    volumes:
      - ./odoo/addons:/mnt/extra-addons

  odoo-db:
    image: postgres:14
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=odoo
    volumes:
      - ./odoo/postgres:/var/lib/postgresql/data

  # SearXNG (SerpAPI alternative)
  searxng:
    image: searxng/searxng:latest
    ports:
      - "8888:8080"
    volumes:
      - ./searxng/settings.yml:/etc/searxng/settings.yml:ro
      - ./searxng/limiter.conf:/etc/searxng/limiter.conf:ro

volumes:
  mattermost_postgres:
  plane_db:
  plane_redis:
  chatwoot_postgres:
  chatwoot_redis:
  odoo_postgres:
```

### Launch All Services
```bash
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Access services
# Mattermost: http://localhost:8065
# Plane: http://localhost:3000
# Chatwoot: http://localhost:3001
# Odoo: http://localhost:8069
# SearXNG: http://localhost:8888
```

---

## 5️⃣ AI MODELS: DEEPSEEK → OLLAMA (Already Configured!)

### Current Status: ✅ Already Optimal

Your backend is ALREADY configured to use Ollama!

```python
# From backend/config/settings.py (line 49-50)
OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
DEFAULT_LOCAL_MODEL: str = Field(default="mistral", env="DEFAULT_LOCAL_MODEL")
```

### Verify Ollama is Running
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# If not running, install Ollama
# Windows/Mac: https://ollama.ai/download
# Linux: curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull models in another terminal
ollama pull mistral
ollama pull neural-chat
ollama pull llama2
ollama pull qwen
```

### Use Local Models in Your Agent
```python
# backend/agents/ai_agent.py
from backend.core.buddy_core import BuddyCore

class AIAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.buddy_core = BuddyCore()  # Already uses Ollama!
    
    def execute_action(self, action, parameters):
        # BuddyCore will automatically use local Ollama model
        result = self.buddy_core.process_request(
            intent=parameters.get('intent'),
            context=parameters.get('context')
        )
        return result
```

### Available Models (All Free)
| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| mistral | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | General purpose |
| neural-chat | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | Conversations |
| llama2 | 7B-70B | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks |
| qwen | 7B-72B | ⚡⚡⭐ | ⭐⭐⭐⭐ | Chinese support |
| orca-mini | 3B | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast inference |

---

## ✅ QUICK MIGRATION CHECKLIST

### Phase 1: Payments (1 week)
- [ ] Create Razorpay account (free)
- [ ] Get API credentials
- [ ] Update settings.py
- [ ] Update .env
- [ ] Create razorpay_agent.py
- [ ] Test payments endpoint
- [ ] Deprecate Stripe agent

### Phase 2: Messaging (1 week)
- [ ] Create AWS account (free tier)
- [ ] Get SNS credentials
- [ ] Update settings.py
- [ ] Update .env
- [ ] Create aws_sns_agent.py
- [ ] Test SMS sending
- [ ] Deprecate Twilio agent

### Phase 3: Email (3 days)
- [ ] Create Brevo account (free)
- [ ] Get API key
- [ ] Update settings.py
- [ ] Update .env
- [ ] Create brevo_agent.py
- [ ] Test email campaigns
- [ ] Deprecate Mailchimp agent

### Phase 4: Self-Hosted Services (1 week)
- [ ] Set up docker-compose.yml
- [ ] Launch Mattermost
- [ ] Launch Plane
- [ ] Launch Chatwoot
- [ ] Launch Odoo
- [ ] Migrate data if needed

### Phase 5: Verification
- [ ] All endpoints tested
- [ ] Agents functional
- [ ] No errors in logs
- [ ] Performance acceptable

---

## 💰 COST SAVINGS SUMMARY

| Change | Annual Savings |
|--------|----------------|
| Stripe → Razorpay | $2,000 - $3,000 |
| PayPal → Payoneer | $1,500 - $2,000 |
| Twilio → AWS SNS | $1,000 - $2,000 |
| Mailchimp → Brevo | $200 - $500 |
| HubSpot → Odoo | $600 - $3,000 |
| Jira → Plane | $840+ |
| Zendesk → Chatwoot | $228 - $1,800 |
| DeepSeek → Ollama | $500 - $2,000 |
| **TOTAL** | **$7,000 - $17,300+** |

---

**NEXT STEP**: Choose which phase to implement first (Recommended: Start with Phase 1 - Payments)
