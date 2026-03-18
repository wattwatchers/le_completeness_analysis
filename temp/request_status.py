import os
import sys

import httpx
from dotenv import load_dotenv

UA_API_BASE_URL = "https://ua-api.wattwatchers.net"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(REPO_ROOT, ".env"))

UA_USERNAME = os.getenv("UA_USERNAME", "")
UA_PASSWORD = os.getenv("UA_PASSWORD", "")


def get_ua_token(username: str, password: str) -> str:
    if not username or not password:
        raise ValueError("UA_USERNAME/UA_PASSWORD must be set in the environment")
    payload = {"username": username, "password": password}
    response = httpx.post(f"{UA_API_BASE_URL}/auth", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    token = data.get("token")
    print(token)
    if not token:
        raise RuntimeError("UA auth response missing token")
    return token


def get_device_status(token: str, device_id: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = httpx.get(f"{UA_API_BASE_URL}/devices/{device_id}", headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python request_status.py <DEVICE_ID>")
        return 2
    device_id = sys.argv[1]
    token = get_ua_token(UA_USERNAME, UA_PASSWORD)
    status = get_device_status(token, device_id)
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
