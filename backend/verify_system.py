#!/usr/bin/env python3
"""
BUDDY AI OS - System Verification Script
Verifies all fixes and checks system readiness
"""

import sys
import traceback
from pathlib import Path

print("\n" + "="*70)
print("BUDDY AI OS - SYSTEM VERIFICATION SCRIPT")
print("="*70 + "\n")

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

success_count = 0
fail_count = 0

def check(name, test_func):
    """Run a check and report result"""
    global success_count, fail_count
    try:
        print(f"Checking: {name}...", end=" ")
        result = test_func()
        if result:
            print(f"{GREEN}✅ PASS{RESET}")
            success_count += 1
            return True
        else:
            print(f"{RED}❌ FAIL{RESET}")
            fail_count += 1
            return False
    except Exception as e:
        print(f"{RED}❌ ERROR: {e}{RESET}")
        fail_count += 1
        return False

# ============== CHECKS ==============

print("[1/10] Core Module Imports\n")

# Check 1: Settings import
def test_settings():
    try:
        from config.settings import settings
        return hasattr(settings, 'DATABASE_URL')
    except:
        return False

check("Settings (Pydantic v1 compatible)", test_settings)

# Check 2: Database import
def test_database():
    try:
        from db.database import init_db, get_db_session
        return callable(init_db) and callable(get_db_session)
    except:
        return False

check("Database (import paths fixed)", test_database)

# Check 3: BuddyCore import
def test_buddy_core():
    try:
        from core.buddy_core import BuddyCore
        return BuddyCore is not None
    except:
        return False

check("Buddy Core (orchestration engine)", test_buddy_core)

# Check 4: API main import
def test_api_main():
    try:
        from api.main import create_app
        return callable(create_app)
    except:
        return False

check("API Main (FastAPI app)", test_api_main)

print("\n[2/10] API Routers\n")

# Check 5: All routers
def test_routers():
    try:
        from api.v1 import auth, users, agents, workflows, integrations, notifications, admin, files, analytics, search, marketplace
        routers = [auth.router, users.router, agents.router, workflows.router,
                   integrations.router, notifications.router, admin.router,
                   files.router, analytics.router, search.router, marketplace.router]
        return all(r is not None for r in routers)
    except Exception as e:
        print(f"Router error: {e}")
        return False

check("All 11 API routers (auth, users, agents, etc.)", test_routers)

print("\n[3/10] Configuration Files\n")

# Check 6: .env file
def test_env():
    return Path("../.env").exists() or Path(".env").exists()

check(".env configuration file", test_env)

# Check 7: requirements.txt
def test_requirements():
    with open("../requirements.txt" if not Path("requirements.txt").exists() else "requirements.txt") as f:
        content = f.read()
        has_pydantic = "pydantic==1.10.14" in content
        has_sqlalchemy = "sqlalchemy==1.4.54" in content
        no_pydantic_settings = "pydantic-settings" not in content or "pydantic-settings==0" in content
        return has_pydantic and has_sqlalchemy and no_pydantic_settings

check("requirements.txt (fixed dependencies)", test_requirements)

print("\n[4/10] Database Layer\n")

# Check 8: Models exist
def test_models():
    return Path("db/models.py").exists()

check("Database models file", test_models)

# Check 9: Database module clean
def test_db_clean():
    with open("db/database.py") as f:
        content = f.read()
        # Check for correct imports
        has_correct_import = "from db.models import Base" in content
        # Check for NO duplicates
        get_db_count = content.count("async def get_db")
        get_db_session_count = content.count("async def get_db_session")
        return has_correct_import and (get_db_count + get_db_session_count) <= 1

check("Database module (no duplicates)", test_db_clean)

print("\n[5/10] Settings Configuration\n")

# Check 10: Settings imports
def test_settings_import():
    with open("config/settings.py") as f:
        content = f.read()
        # Check for CORRECT import
        has_correct = "from pydantic import BaseSettings" in content
        # Check for NO incorrect import
        has_incorrect = "from pydantic_settings import BaseSettings" in content
        return has_correct and not has_incorrect

check("Settings.py (Pydantic v1 imports)", test_settings_import)

# ============== SUMMARY ==============

print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)
print(f"\n✅ Passed: {success_count}/10")
print(f"❌ Failed: {fail_count}/10")

if fail_count == 0:
    print(f"\n{GREEN}🎉 ALL CHECKS PASSED!{RESET}")
    print(f"\n{GREEN}✅ System is ready to run!{RESET}")
    print(f"\nNext steps:")
    print(f"  1. Install dependencies: pip install -r requirements.txt")
    print(f"  2. Start backend: python3 -m api.main")
    print(f"  3. Access docs: http://localhost:8000/docs")
    sys.exit(0)
else:
    print(f"\n{RED}⚠️  Some checks failed. See details above.{RESET}")
    sys.exit(1)
