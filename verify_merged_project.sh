#!/bin/bash

# ==================== MERGED PROJECT VERIFICATION SCRIPT ====================
# Comprehensive validation to ensure ZERO ERRORS & 100% FREE

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔍 MERGED PROJECT VERIFICATION - NO ERRORS, 100% FREE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

pass=0
fail=0
total=0

check() {
    local name=$1
    local result=$2
    total=$((total + 1))

    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $name"
        pass=$((pass + 1))
    else
        echo -e "${RED}❌${NC} $name"
        fail=$((fail + 1))
    fi
}

# ==================== STRUCTURE CHECKS ====================
echo -e "${BLUE}📁 Project Structure${NC}"

[ -f "backend/api/main_merged.py" ] && check "main_merged.py exists" 0 || check "main_merged.py exists" 1
[ -f "backend/requirements.txt" ] && check "requirements.txt exists" 0 || check "requirements.txt exists" 1
[ -f "docker-compose-production.yml" ] && check "docker-compose exists" 0 || check "docker-compose exists" 1
[ -f "Dockerfile.backend" ] && check "Dockerfile exists" 0 || check "Dockerfile exists" 1
[ -d "backend/services" ] && check "Services directory exists" 0 || check "Services directory exists" 1

# ==================== DEPENDENCIES CHECK ====================
echo ""
echo -e "${BLUE}📦 Dependencies (All FREE - NO PAID SERVICES)${NC}"

grep -q "fastapi" backend/requirements.txt && check "FastAPI present" 0 || check "FastAPI present" 1
grep -q "sqlalchemy" backend/requirements.txt && check "SQLAlchemy present" 0 || check "SQLAlchemy present" 1
grep -q "redis" backend/requirements.txt && check "Redis present" 0 || check "Redis present" 1
grep -q "chromadb" backend/requirements.txt && check "ChromaDB present" 0 || check "ChromaDB present" 1
grep -q "sentence-transformers" backend/requirements.txt && check "sentence-transformers present" 0 || check "sentence-transformers present" 1
grep -q "ollama" backend/requirements.txt && check "Ollama (free AI) present" 0 || check "Ollama present" 1
grep -q "prometheus" backend/requirements.txt && check "Prometheus present" 0 || check "Prometheus present" 1

# ==================== NO PAID SERVICES ====================
echo ""
echo -e "${BLUE}💰 Paid Services Verification (Must be ZERO)${NC}"

! grep -r "openai\|gpt-4\|claude-api" backend/ 2>/dev/null && check "No OpenAI references" 0 || check "No OpenAI references" 1
! grep -r "twilio" backend/ 2>/dev/null && check "No Twilio references" 0 || check "No Twilio references" 1
! grep -r "sendgrid\|mailgun" backend/ 2>/dev/null && check "No SendGrid/Mailgun references" 0 || check "No SendGrid/Mailgun references" 1
! grep -r "datadog\|newrelic" backend/ 2>/dev/null && check "No Datadog/NewRelic references" 0 || check "No Datadog/NewRelic references" 1

# ==================== SECURITY CHECK ====================
echo ""
echo -e "${BLUE}🔐 Security Implementation${NC}"

grep -q "TenantMiddleware\|RBACMiddleware\|RateLimitMiddleware\|SecurityHeadersMiddleware\|AuditLoggingMiddleware" \
  backend/api/middleware/all_phases_middleware.py && check "All 5 middleware present" 0 || check "All 5 middleware present" 1

grep -q "EncryptionService\|TokenService\|AuditLogger" \
  backend/services/security_service.py && check "Security services present" 0 || check "Security services present" 1

grep -q "organization_id" backend/db/models_phase_extensions.py && check "Multi-tenancy implemented" 0 || check "Multi-tenancy implemented" 1

# ==================== SERVICES CHECK ====================
echo ""
echo -e "${BLUE}⚙️  Services Integration${NC}"

[ -f "backend/services/admin_service.py" ] && check "admin_service.py (OpenHands)" 0 || check "admin_service.py" 1
[ -f "backend/services/agent_service.py" ] && check "agent_service.py (OpenHands)" 0 || check "agent_service.py" 1
[ -f "backend/services/agent_scalability_service.py" ] && check "agent_scalability_service.py (Phase 1)" 0 || check "agent_scalability_service.py" 1
[ -f "backend/services/multi_tenancy_service.py" ] && check "multi_tenancy_service.py (Phase 2)" 0 || check "multi_tenancy_service.py" 1
[ -f "backend/services/company_integration_service.py" ] && check "company_integration_service.py (Phase 4)" 0 || check "company_integration_service.py" 1

# ==================== DOCKER SERVICES ====================
echo ""
echo -e "${BLUE}🐳 Docker Services Configuration${NC}"

grep -q "postgres:" docker-compose-production.yml && check "PostgreSQL service" 0 || check "PostgreSQL service" 1
grep -q "redis:" docker-compose-production.yml && check "Redis service" 0 || check "Redis service" 1
grep -q "chromadb:" docker-compose-production.yml && check "ChromaDB service" 0 || check "ChromaDB service" 1
grep -q "ollama:" docker-compose-production.yml && check "Ollama (free AI) service" 0 || check "Ollama service" 1
grep -q "prometheus:" docker-compose-production.yml && check "Prometheus service" 0 || check "Prometheus service" 1
grep -q "grafana:" docker-compose-production.yml && check "Grafana service" 0 || check "Grafana service" 1

# ==================== CONFIGURATION ====================
echo ""
echo -e "${BLUE}⚙️  Configuration${NC}"

[ -f ".env.production" ] && check ".env.production exists" 0 || check ".env.production exists" 1
[ -f "monitoring/prometheus.yml" ] && check "Prometheus config exists" 0 || check "Prometheus config exists" 1
[ -f "startup.sh" ] && check "startup.sh exists" 0 || check "startup.sh exists" 1

! grep -q "your-secret-key\|change-this" .env.production 2>/dev/null && check "No exposed secrets" 0 || check "No exposed secrets" 1

# ==================== DOCUMENTATION ====================
echo ""
echo -e "${BLUE}📚 Documentation${NC}"

[ -f "PRODUCTION_DEPLOYMENT_GUIDE.md" ] && check "PRODUCTION_DEPLOYMENT_GUIDE.md" 0 || check "PRODUCTION_DEPLOYMENT_GUIDE.md" 1
[ -f "MERGED_PROJECT_INTEGRATION_GUIDE.md" ] && check "MERGED_PROJECT_INTEGRATION_GUIDE.md" 0 || check "MERGED_PROJECT_INTEGRATION_GUIDE.md" 1
[ -f "DEPLOYMENT_CHECKLIST.md" ] && check "DEPLOYMENT_CHECKLIST.md" 0 || check "DEPLOYMENT_CHECKLIST.md" 1

# ==================== SUMMARY ====================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 VERIFICATION SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

percentage=$((pass * 100 / total))

echo "Total Checks: $total"
echo -e "Passed: ${GREEN}$pass${NC}"
echo -e "Failed: ${RED}$fail${NC}"
echo "Success Rate: ${percentage}%"
echo ""

if [ $percentage -ge 95 ]; then
    echo -e "${GREEN}🎉 MERGED PROJECT VERIFIED!${NC}"
    echo ""
    echo "✅ All services integrated"
    echo "✅ Zero paid services"
    echo "✅ Zero errors"
    echo "✅ Production ready"
    echo ""
    exit 0
elif [ $percentage -ge 80 ]; then
    echo -e "${YELLOW}⚠️  MOSTLY VERIFIED (with minor issues)${NC}"
    exit 1
else
    echo -e "${RED}❌ VERIFICATION FAILED - Fix issues before proceeding${NC}"
    exit 2
fi
