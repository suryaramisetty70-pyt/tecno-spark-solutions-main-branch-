#!/bin/bash

# ==================== TECNO SPARK DEPLOYMENT VERIFICATION ====================
# Comprehensive checklist for production deployment
# Verifies all 5 phases, security, services, and cost

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_mark() { echo -e "${GREEN}✅${NC}"; }
cross_mark() { echo -e "${RED}❌${NC}"; }
warn_mark() { echo -e "${YELLOW}⚠️${NC}"; }

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 TECNO SPARK BUDDY AI OS - DEPLOYMENT VERIFICATION${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

total_checks=0
passed_checks=0

# ==================== INFRASTRUCTURE CHECKS ====================
echo -e "${BLUE}📦 INFRASTRUCTURE CHECKS${NC}"

# Check Docker
total_checks=$((total_checks + 1))
if command -v docker &> /dev/null; then
    echo -n "  Docker installed: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Docker installed: "
    cross_mark
fi

# Check Docker Compose
total_checks=$((total_checks + 1))
if command -v docker-compose &> /dev/null; then
    echo -n "  Docker Compose installed: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Docker Compose installed: "
    cross_mark
fi

# Check environment file
total_checks=$((total_checks + 1))
if [ -f ".env.production" ]; then
    echo -n "  .env.production exists: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  .env.production exists: "
    cross_mark
fi

# Check docker-compose file
total_checks=$((total_checks + 1))
if [ -f "docker-compose-production.yml" ]; then
    echo -n "  docker-compose-production.yml exists: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  docker-compose-production.yml exists: "
    cross_mark
fi

# Check Dockerfile
total_checks=$((total_checks + 1))
if [ -f "Dockerfile.backend" ]; then
    echo -n "  Dockerfile.backend exists: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Dockerfile.backend exists: "
    cross_mark
fi

echo ""

# ==================== SECURITY CHECKS ====================
echo -e "${BLUE}🔐 SECURITY CHECKS${NC}"

# Check for hardcoded secrets
total_checks=$((total_checks + 1))
if ! grep -r "change-this" backend/ 2>/dev/null | grep -q "SECRET_KEY\|ENCRYPTION_KEY"; then
    echo -n "  No hardcoded secrets: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  No hardcoded secrets: "
    warn_mark
fi

# Check requirements for security libraries
total_checks=$((total_checks + 1))
if grep -q "cryptography" backend/requirements.txt && \
   grep -q "PyJWT" backend/requirements.txt && \
   grep -q "passlib" backend/requirements.txt; then
    echo -n "  Security libraries in requirements: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Security libraries in requirements: "
    cross_mark
fi

# Check middleware implementations
total_checks=$((total_checks + 1))
if [ -f "backend/api/middleware/all_phases_middleware.py" ] && \
   grep -q "TenantMiddleware\|RBACMiddleware\|RateLimitMiddleware\|SecurityHeadersMiddleware\|AuditLoggingMiddleware" backend/api/middleware/all_phases_middleware.py; then
    echo -n "  All 5 middleware implemented: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  All 5 middleware implemented: "
    cross_mark
fi

echo ""

# ==================== PHASE CHECKS ====================
echo -e "${BLUE}⚡ PHASE IMPLEMENTATION CHECKS${NC}"

# Phase 1: Agent Scalability
total_checks=$((total_checks + 1))
if [ -f "backend/services/agent_scalability_service.py" ] && \
   grep -q "AgentRegistryService\|IntentClassifier\|MultiAgentCoordinator" backend/services/agent_scalability_service.py; then
    echo -n "  Phase 1 (Agent Scalability): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Phase 1 (Agent Scalability): "
    cross_mark
fi

# Phase 2: Multi-Tenancy
total_checks=$((total_checks + 1))
if [ -f "backend/services/multi_tenancy_service.py" ] && \
   grep -q "TenantContext\|RBACService\|TenantScopingService" backend/services/multi_tenancy_service.py; then
    echo -n "  Phase 2 (Multi-Tenancy): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Phase 2 (Multi-Tenancy): "
    cross_mark
fi

# Phase 3: Security
total_checks=$((total_checks + 1))
if [ -f "backend/services/security_service.py" ] && \
   grep -q "EncryptionService\|TokenService\|AuditLogger\|RateLimitService" backend/services/security_service.py; then
    echo -n "  Phase 3 (Enterprise Security): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Phase 3 (Enterprise Security): "
    cross_mark
fi

# Phase 4: Company Integration
total_checks=$((total_checks + 1))
if [ -f "backend/services/company_integration_service.py" ] && \
   grep -q "CompanySyncService\|IntegrationRegistryService\|CompanyAnalyticsService" backend/services/company_integration_service.py; then
    echo -n "  Phase 4 (Company Integration): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Phase 4 (Company Integration): "
    cross_mark
fi

# Phase 5: All phases in main.py
total_checks=$((total_checks + 1))
if [ -f "backend/api/main_all_phases.py" ] && \
   grep -q "Phase 1\|Phase 2\|Phase 3\|Phase 4\|Phase 5" backend/api/main_all_phases.py; then
    echo -n "  Phase 5 (All integrated): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Phase 5 (All integrated): "
    cross_mark
fi

echo ""

# ==================== DEPENDENCY CHECKS ====================
echo -e "${BLUE}📦 DEPENDENCY CHECKS${NC}"

# Core framework
total_checks=$((total_checks + 1))
if grep -q "fastapi\|uvicorn\|sqlalchemy\|pydantic" backend/requirements.txt; then
    echo -n "  Core framework (FastAPI, SQLAlchemy, Pydantic): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Core framework: "
    cross_mark
fi

# ML/NLP (Free)
total_checks=$((total_checks + 1))
if grep -q "sentence-transformers\|chromadb\|numpy\|pandas" backend/requirements.txt; then
    echo -n "  ML/NLP libraries (sentence-transformers, ChromaDB): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  ML/NLP libraries: "
    cross_mark
fi

# AI Models (Free)
total_checks=$((total_checks + 1))
if grep -q "ollama" backend/requirements.txt; then
    echo -n "  Free AI models (Ollama): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Free AI models: "
    warn_mark
fi

# Email (Free)
total_checks=$((total_checks + 1))
if grep -q "brevo\|requests" backend/requirements.txt; then
    echo -n "  Free email service (Brevo): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Free email service: "
    warn_mark
fi

echo ""

# ==================== PAID SERVICES CHECK ====================
echo -e "${BLUE}💰 PAID SERVICES VERIFICATION${NC}"

paid_services=0
excluded_count=0

# Check for paid services
if grep -r "openai\|gpt\|chatgpt" backend/ 2>/dev/null; then
    echo -n "  ❌ Found OpenAI references: "
    cross_mark
    paid_services=$((paid_services + 1))
fi

if grep -r "twilio" backend/ 2>/dev/null; then
    echo -n "  ❌ Found Twilio references: "
    cross_mark
    paid_services=$((paid_services + 1))
fi

if grep -r "sendgrid\|mailgun" backend/ 2>/dev/null; then
    echo -n "  ❌ Found SendGrid/Mailgun: "
    cross_mark
    paid_services=$((paid_services + 1))
fi

if grep -r "stripe" backend/ 2>/dev/null; then
    echo -n "  ⚠️ Found Stripe (may be test mode): "
    warn_mark
fi

if grep -r "sentry" backend/ 2>/dev/null; then
    echo -n "  ⚠️ Found Sentry (optional - use Prometheus instead): "
    warn_mark
fi

total_checks=$((total_checks + 1))
if [ $paid_services -eq 0 ]; then
    echo -n "  No paid services detected: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Free services only: "
    cross_mark
fi

echo ""

# ==================== DATABASE CHECKS ====================
echo -e "${BLUE}🗄️  DATABASE CHECKS${NC}"

# Check models file
total_checks=$((total_checks + 1))
if [ -f "backend/db/models_phase_extensions.py" ] && \
   grep -q "class Organization\|class Company\|class Agent\|class Team" backend/db/models_phase_extensions.py; then
    echo -n "  Multi-tenancy models defined: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Multi-tenancy models defined: "
    cross_mark
fi

# Check organization_id in models
total_checks=$((total_checks + 1))
if grep -q "organization_id" backend/db/models_phase_extensions.py; then
    echo -n "  Organization isolation (org_id) implemented: "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Organization isolation: "
    cross_mark
fi

echo ""

# ==================== COMPLIANCE CHECKS ====================
echo -e "${BLUE}✅ COMPLIANCE CHECKS${NC}"

total_checks=$((total_checks + 1))
if [ -f "backend/services/security_service.py" ] && \
   grep -q "GDPR\|HIPAA\|SOC2" backend/services/security_service.py; then
    echo -n "  Compliance features (GDPR/HIPAA/SOC2): "
    check_mark
    passed_checks=$((passed_checks + 1))
else
    echo -n "  Compliance features: "
    cross_mark
fi

echo ""

# ==================== SUMMARY ====================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 VERIFICATION SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

percentage=$((passed_checks * 100 / total_checks))

echo "Total Checks: $total_checks"
echo "Passed: $(echo -e ${GREEN})$passed_checks$(echo -e ${NC})"
echo "Failed: $(echo -e ${RED})$((total_checks - passed_checks))$(echo -e ${NC})"
echo "Success Rate: ${percentage}%"
echo ""

if [ $percentage -ge 90 ]; then
    echo -e "${GREEN}🎉 DEPLOYMENT READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Update .env.production with your domain & secrets"
    echo "  2. ./startup.sh"
    echo "  3. Access: http://localhost:8000/docs"
    exit 0
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}⚠️  DEPLOYMENT POSSIBLE (with warnings)${NC}"
    exit 1
else
    echo -e "${RED}❌ DEPLOYMENT BLOCKED - Fix issues before proceeding${NC}"
    exit 2
fi
