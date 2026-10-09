#!/usr/bin/env python3
"""
Seed script — creates a demo investigator account and loads the 4 synthetic cases
into the running CrimeNet backend via its REST API.

Usage:
  cd project-root
  python scripts/load_synthetic_data.py

Prerequisites:
  - Backend running at http://localhost:8000
  - Synthetic case files in data/synthetic/cases/
"""
import json
import os
import sys
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")

DEMO_USER = {
    "name": "Demo Investigator",
    "email": "demo@crimenet.local",
    "password": "crimenet2026",
    "role": "INVESTIGATOR",
}

CASES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic", "cases")


def register_or_login() -> str:
    """Register demo user (ignore conflict) then login and return token."""
    requests.post(f"{API_BASE}/auth/register", json=DEMO_USER)
    res = requests.post(f"{API_BASE}/auth/login", json={
        "email": DEMO_USER["email"],
        "password": DEMO_USER["password"],
    })
    res.raise_for_status()
    token = res.json()["access_token"]
    print(f"Logged in as {DEMO_USER['email']}")
    return token


def create_case(token: str, title: str, description: str, priority: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{API_BASE}/cases", json={
        "title": title,
        "description": description,
        "priority": priority,
    }, headers=headers)
    res.raise_for_status()
    case = res.json()
    print(f"  Created case: {case['case_number']} — {case['title']}")
    return case["id"]


def upload_file(token: str, case_id: str, file_path: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, "rb") as f:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        mime = {
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".json": "application/json",
        }.get(ext, "application/octet-stream")
        res = requests.post(
            f"{API_BASE}/cases/{case_id}/documents",
            files={"file": (filename, f, mime)},
            headers=headers,
        )
    if res.ok:
        print(f"    Uploaded: {filename} (job: {res.json().get('job_id', '?')})")
    else:
        print(f"    Failed to upload {filename}: {res.text}")


def main():
    print("CrimeNet Synthetic Data Loader")
    print("=" * 40)

    token = register_or_login()

    manifest_path = os.path.join(CASES_DIR, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    for case_info in manifest:
        print(f"\nLoading: {case_info['title']}")
        case_id = create_case(
            token,
            title=case_info["title"],
            description=case_info["description"],
            priority=case_info["priority"],
        )
        for filename in case_info.get("files", []):
            file_path = os.path.join(CASES_DIR, filename)
            if os.path.exists(file_path):
                upload_file(token, case_id, file_path)
            else:
                print(f"    File not found: {file_path}")

    print("\n\nDone! Open http://localhost:3000 and login with:")
    print(f"  Email: {DEMO_USER['email']}")
    print(f"  Password: {DEMO_USER['password']}")


if __name__ == "__main__":
    main()
