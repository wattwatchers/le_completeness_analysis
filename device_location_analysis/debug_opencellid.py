import os
import argparse
import requests

DEFAULT_BASE_URL = "https://us1.unwiredlabs.com/v2/process"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Debug OpenCellID lookup for a single cell")
    parser.add_argument("--mcc", type=int, default=505)
    parser.add_argument("--mnc", type=int, default=2)
    parser.add_argument("--lac", type=int, default=57252, help="Use TAC for LTE")
    parser.add_argument("--cellid", type=int, default=23945779, help="Use full ECI for LTE")
    parser.add_argument("--radio", default="lte", help="Radio type (gsm, umts, lte, nbiot, nr)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_key = os.getenv("OPENCELLID_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENCELLID_API_KEY env var is required")

    payload = {
        "token": api_key,
        "radio": args.radio,
        "mcc": args.mcc,
        "mnc": args.mnc,
        "cells": [
            {
                "lac": args.lac,
                "cid": args.cellid,
            }
        ],
        "address": 1,
    }

    print("Request payload:", payload)
    response = requests.post(args.base_url, json=payload, timeout=30)
    print("Status:", response.status_code)
    print("Body:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            data = None
        if isinstance(data, dict):
            if data.get("status") == "error":
                print("Error:", data.get("message"))
            lat = data.get("lat")
            lon = data.get("lon")
            if lat is not None and lon is not None:
                print(f"Latitude: {lat}")
                print(f"Longitude: {lon}")


if __name__ == "__main__":
    main()
