#!/usr/bin/env python3
"""
Buddy AI OS - Comprehensive System Verification & Error Checking
Performs cross-validation of all components
"""

import os
import json
import sys
from pathlib import Path

class BuddySystemVerifier:
    def __init__(self):
        self.root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed = []

    def verify_python_files(self):
        """Verify all Python files compile correctly"""
        python_files = list(self.root.glob("backend/**/*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                compile(code, str(py_file), 'exec')
                self.passed.append(f"Python: {py_file.relative_to(self.root)}")
            except SyntaxError as e:
                self.errors.append(f"Syntax Error in {py_file}: {e}")
            except Exception as e:
                self.warnings.append(f"Warning in {py_file}: {e}")

    def verify_imports(self):
        """Verify critical imports work"""
        try:
            sys.path.insert(0, str(self.root / "backend"))

            # Test Buddy Core
            from core.buddy_core import BuddyCore
            from core.intent_router import IntentRouter
            from core.event_bus import EventBus
            from core.memory_engine import MemoryEngine
            from core.workflow_engine import WorkflowEngine
            from core.model_router import ModelRouter
            self.passed.append("Buddy Core: All 5 engines import successfully")

            # Test Agents
            from agents.personal_assistant import PersonalAssistantAgent
            from agents.memory_agent import MemoryAgent
            from agents.productivity_agent import ProductivityAgent
            self.passed.append("Agents: Core agents import successfully")

            # Test API
            from api.main import create_app
            self.passed.append("API: FastAPI app creates successfully")

        except ImportError as e:
            self.errors.append(f"Import Error: {e}")
        except Exception as e:
            self.errors.append(f"Runtime Error: {e}")

    def verify_database_models(self):
        """Verify database is configured correctly"""
        try:
            sys.path.insert(0, str(self.root / "backend"))
            from db.database import DATABASE_URL, sync_engine, async_session_maker

            if "sqlite" in DATABASE_URL:
                self.passed.append("Database: SQLite configured for Windows dev")
            elif "postgresql" in DATABASE_URL:
                self.passed.append("Database: PostgreSQL configured for production")
            else:
                self.warnings.append("Database: Unknown database type")

        except Exception as e:
            self.errors.append(f"Database Config Error: {e}")

    def verify_json_files(self):
        """Verify JSON configuration files"""
        json_files = [
            self.root / "frontend-desktop" / "src-tauri" / "tauri.conf.json",
            self.root / "frontend-mobile" / "pubspec.yaml",  # Actually YAML, skip JSON check
        ]

        for json_file in json_files:
            if json_file.name.endswith('.json'):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                    self.passed.append(f"JSON: {json_file.relative_to(self.root)} is valid")
                except json.JSONDecodeError as e:
                    self.errors.append(f"JSON Error in {json_file}: {e}")

    def verify_file_structure(self):
        """Verify required directory structure exists"""
        required_dirs = [
            "backend/api",
            "backend/core",
            "backend/agents",
            "backend/services",
            "backend/db",
            "backend/config",
            "frontend/app/dashboard",
            "frontend-mobile/lib",
            "frontend-desktop/src-tauri",
        ]

        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                self.passed.append(f"Structure: {dir_path} exists")
            else:
                self.errors.append(f"Structure: {dir_path} missing or not a directory")

    def verify_agent_pattern(self):
        """Verify all agents follow the same pattern"""
        agent_files = list((self.root / "backend" / "agents").glob("*.py"))

        required_methods = ["process_intent", "execute_action", "register_tools"]

        for agent_file in agent_files:
            if agent_file.name == "__init__.py" or agent_file.name == "base_agent.py":
                continue

            try:
                with open(agent_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check for async and non-async versions
                missing = [m for m in required_methods if f"def {m}" not in content]

                if not missing:
                    self.passed.append(f"Agent Pattern: {agent_file.name} follows standard interface")
                else:
                    self.errors.append(f"Agent Pattern: {agent_file.name} missing methods: {missing}")

            except Exception as e:
                self.errors.append(f"Agent Verification Error: {agent_file.name}: {e}")

    def verify_api_endpoints(self):
        """Verify API endpoint files exist"""
        api_modules = [
            "auth", "users", "agents", "workflows", "integrations",
            "notifications", "admin", "files", "analytics", "search"
        ]

        for module in api_modules:
            api_file = self.root / "backend" / "api" / "v1" / f"{module}.py"
            if api_file.exists():
                self.passed.append(f"API: {module}.py exists")
            else:
                self.errors.append(f"API: {module}.py missing")

    def verify_requirements(self):
        """Verify requirements.txt is valid"""
        req_file = self.root / "backend" / "requirements.txt"

        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()

            valid_lines = [l for l in lines if l.strip() and not l.startswith('#')]
            self.passed.append(f"Requirements: {len(valid_lines)} dependencies specified")

            # Check for critical dependencies
            content = open(req_file).read()
            required = ["fastapi", "sqlalchemy", "pydantic"]
            missing = [r for r in required if r not in content]

            if not missing:
                self.passed.append("Requirements: All critical dependencies present")
            else:
                self.errors.append(f"Requirements: Missing critical deps: {missing}")

        except Exception as e:
            self.errors.append(f"Requirements Error: {e}")

    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("BUDDY AI OS - COMPREHENSIVE SYSTEM VERIFICATION")
        print("="*70 + "\n")

        checks = [
            ("Python Files", self.verify_python_files),
            ("Core Imports", self.verify_imports),
            ("Database Config", self.verify_database_models),
            ("File Structure", self.verify_file_structure),
            ("Agent Patterns", self.verify_agent_pattern),
            ("API Endpoints", self.verify_api_endpoints),
            ("Requirements", self.verify_requirements),
            ("JSON Files", self.verify_json_files),
        ]

        for check_name, check_func in checks:
            print(f"\n[*] Verifying {check_name}...")
            check_func()

        self.print_results()

    def print_results(self):
        """Print verification results"""
        print("\n" + "="*70)
        print("VERIFICATION RESULTS")
        print("="*70 + "\n")

        # Passed
        if self.passed:
            print(f"\n[OK] PASSED ({len(self.passed)} checks):")
            for p in self.passed[:10]:
                print(f"  [+] {p}")
            if len(self.passed) > 10:
                print(f"  ... and {len(self.passed) - 10} more")

        # Warnings
        if self.warnings:
            print(f"\n[!] WARNINGS ({len(self.warnings)} issues):")
            for w in self.warnings:
                print(f"  [W] {w}")

        # Errors
        if self.errors:
            print(f"\n[ERROR] ERRORS ({len(self.errors)} critical issues):")
            for e in self.errors:
                print(f"  [!] {e}")
        else:
            print("\n[SUCCESS] No critical errors found!")

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Passed: {len(self.passed)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")
        print(f"\nSystem Status: {'READY' if not self.errors else 'NEEDS FIXES'}")
        print("="*70 + "\n")

        return len(self.errors) == 0

if __name__ == "__main__":
    verifier = BuddySystemVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)
