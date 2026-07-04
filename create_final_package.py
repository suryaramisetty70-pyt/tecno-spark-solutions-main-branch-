#!/usr/bin/env python3
"""
Create production-ready zip package with all deliverables
"""
import zipfile
import os
from pathlib import Path

def create_deployment_package():
    """Create comprehensive deployment zip package"""

    project_dir = Path("c:/Users/surya/OneDrive/Desktop/tecno spark solutiomn")
    zip_filename = project_dir / "BUDDY_AI_OS_COMPLETE_FINAL_v3.0.zip"

    # Files to include in zip
    documentation_files = [
        "00_START_HERE.md",
        "FINAL_COMPLETE_PROJECT_REPORT.txt",
        "FINAL_COMPLETE_DELIVERY_REPORT.txt",
        "FINAL_COMPLETE_STATUS_1000AGENTS.md",
        "COMPLETE_1000_AGENTS_SPECIFICATION.md",
        "EXPANSION_RESEARCH_1000_AGENTS.md",
        "ULTIMATE_POWER_UP_PLAN.md",
        "BUDDY_AI_OS_V2_ENHANCED.md",
        "COMPLETE_PROJECT_STATUS.md",
        "DOWNLOAD_AND_DEPLOY.md",
        "QUICK_START.md",
        "1000_AGENTS_DELIVERY_INDEX.txt",
        "DEPLOYMENT_CHECKLIST.md",
        "API_AUDIT_REPORT.md",
        "API_AUDIT_EXECUTIVE_SUMMARY.md",
    ]

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add documentation files
        for doc_file in documentation_files:
            file_path = project_dir / doc_file
            if file_path.exists():
                arcname = f"Documentation/{doc_file}"
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

        # Add backend directory structure
        backend_dir = project_dir / "backend"
        if backend_dir.exists():
            for root, dirs, files in os.walk(backend_dir):
                for file in files:
                    if file.endswith(('.py', '.txt', '.md', '.yml', '.yaml', '.json')):
                        file_path = Path(root) / file
                        arcname = str(file_path.relative_to(project_dir))
                        if len(arcname) < 200:  # Avoid too long paths
                            zipf.write(file_path, arcname)

        # Add root config files if they exist
        root_files = ['requirements.txt', '.env.production', '.gitignore', 'README.md']
        for root_file in root_files:
            file_path = project_dir / root_file
            if file_path.exists():
                zipf.write(file_path, root_file)
                print(f"Added: {root_file}")

    # Get size
    size_mb = zip_filename.stat().st_size / (1024 * 1024)
    print(f"\n✓ Package created: {zip_filename}")
    print(f"✓ Size: {size_mb:.2f} MB")
    print(f"✓ Ready for download and deployment")

    return zip_filename

if __name__ == "__main__":
    zip_file = create_deployment_package()
