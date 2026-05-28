#!/usr/bin/env python3
"""Template for uploading a STEP to Onshape without hard-coded credentials.

This file is intentionally a template. Fill document/workspace/assembly ids in a
local copy or pass them from your own wrapper. Never commit credentials.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
from pathlib import Path
from urllib.parse import urlencode

import requests


BASE_URL = "https://cad.onshape.com"


def _date_header() -> str:
    return dt.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def _sign(method: str, path: str, query: str, content_type: str, nonce: str, date: str, secret_key: str) -> str:
    string_to_sign = "\n".join([method.lower(), nonce, date.lower(), content_type.lower(), path.lower(), query.lower(), ""])
    digest = hmac.new(secret_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def onshape_headers(method: str, path: str, query: str = "", content_type: str = "application/json") -> dict[str, str]:
    access_key = os.environ["ONSHAPE_ACCESS_KEY"]
    secret_key = os.environ["ONSHAPE_SECRET_KEY"]
    nonce = secrets.token_hex(16)
    date = _date_header()
    signature = _sign(method, path, query, content_type, nonce, date, secret_key)
    return {
        "Date": date,
        "On-Nonce": nonce,
        "Authorization": f"On {access_key}:HmacSHA256:{signature}",
        "Content-Type": content_type,
        "Accept": "application/json",
    }


def upload_step(document_id: str, workspace_id: str, step_path: Path) -> dict:
    params = {
        "storeInDocument": "true",
        "allowFaultyParts": "false",
        "flattenAssemblies": "false",
    }
    query = urlencode(params)
    path = f"/api/v10/documents/d/{document_id}/w/{workspace_id}/translation/upload"
    url = f"{BASE_URL}{path}?{query}"
    content_type = mimetypes.guess_type(step_path.name)[0] or "application/step"

    headers = onshape_headers("POST", path, query, content_type)
    data = step_path.read_bytes()
    response = requests.post(url, headers=headers, data=data, timeout=120)
    response.raise_for_status()
    return response.json()


def main() -> None:
    document_id = os.environ.get("ONSHAPE_DOCUMENT_ID", "")
    workspace_id = os.environ.get("ONSHAPE_WORKSPACE_ID", "")
    step_path = Path(os.environ.get("ONSHAPE_STEP_PATH", "torsion_spring.step"))
    if not document_id or not workspace_id:
        raise SystemExit("Set ONSHAPE_DOCUMENT_ID and ONSHAPE_WORKSPACE_ID first.")

    result = upload_step(document_id, workspace_id, step_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
