#!/usr/bin/env python3
"""Create a credential-free Canvas snapshot for an academic email digest.

Credentials are read only from the environment.  The JSON output never contains
the token, so it is safe for an agent to read when drafting a digest.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import sys
import urllib.parse
import urllib.request
from typing import Any
from zoneinfo import ZoneInfo


HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"
DEFAULT_STATE = HERE / "state"
USER_AGENT = "daily-digest/1.0"


def strip_html(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def load_config(path: pathlib.Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing config file: {path}. Copy config.example.json to config.json.") from exc
    for field in ("canvas_base_url", "timezone"):
        if not config.get(field):
            raise RuntimeError(f"config.json is missing {field!r}.")
    return config


def request_json(url: str, token: str) -> tuple[Any, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - user supplied Canvas host
            payload = json.loads(response.read().decode("utf-8"))
            return payload, response.headers.get("Link")
    except Exception as exc:  # urllib errors vary by Canvas host
        raise RuntimeError(f"Canvas request failed: {url}: {exc}") from exc


def next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for entry in link_header.split(","):
        if 'rel="next"' in entry:
            match = re.search(r"<([^>]+)>", entry)
            return match.group(1) if match else None
    return None


def list_all(base_url: str, token: str, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{base_url}{path}" + (f"?{query}" if query else "")
    items: list[dict[str, Any]] = []
    visited: set[str] = set()
    while url and url not in visited:
        visited.add(url)
        payload, links = request_json(url, token)
        if not isinstance(payload, list):
            raise RuntimeError(f"Canvas returned an unexpected payload for {path}.")
        items.extend(payload)
        url = next_link(links)
    return items


def compact_assignment(item: dict[str, Any]) -> dict[str, Any]:
    submission = item.get("submission") or {}
    return {
        "id": item.get("id"), "name": item.get("name"), "due_at": item.get("due_at"),
        "unlock_at": item.get("unlock_at"), "lock_at": item.get("lock_at"),
        "published": item.get("published"), "html_url": item.get("html_url"),
        "submission_status": submission.get("workflow_state"),
        "submitted_at": submission.get("submitted_at"),
        "description": strip_html(item.get("description")),
    }


def compact_module(module: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": module.get("id"), "name": module.get("name"), "state": module.get("state"),
        "updated_at": module.get("updated_at"),
        "items": [{
            "id": item.get("id"), "type": item.get("type"), "title": item.get("title"),
            "content_id": item.get("content_id"), "page_url": item.get("page_url"),
            "html_url": item.get("html_url"), "due_at": (item.get("content_details") or {}).get("due_at"),
        } for item in module.get("items", [])],
    }


def fetch(config: dict[str, Any], token: str) -> dict[str, Any]:
    base_url = str(config["canvas_base_url"]).rstrip("/")
    now = dt.datetime.now(ZoneInfo(str(config["timezone"])))
    courses = list_all(base_url, token, "/api/v1/courses", {
        "enrollment_state": "active", "include[]": ["term", "favorites"], "per_page": 100,
    })
    visible_courses = [course for course in courses if not course.get("access_restricted_by_date")]
    records = []
    for course in visible_courses:
        course_id = course["id"]
        assignments = list_all(base_url, token, f"/api/v1/courses/{course_id}/assignments", {
            "order_by": "due_at", "include[]": "submission", "per_page": 100,
        })
        modules = list_all(base_url, token, f"/api/v1/courses/{course_id}/modules", {
            "include[]": ["items", "content_details"], "per_page": 100,
        })
        records.append({
            "id": course_id, "code": course.get("course_code") or course.get("name"),
            "name": course.get("name"), "term": (course.get("term") or {}).get("name"),
            "html_url": course.get("html_url"),
            "assignments": [compact_assignment(item) for item in assignments],
            "modules": [compact_module(item) for item in modules],
        })
    return {"generated_at": now.isoformat(), "timezone": config["timezone"], "courses": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_STATE / "current.json")
    args = parser.parse_args()
    token = os.environ.get("CANVAS_ACCESS_TOKEN")
    if not token:
        print("Canvas snapshot failed: set CANVAS_ACCESS_TOKEN in your environment.", file=sys.stderr)
        return 1
    try:
        config = load_config(args.config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        current = args.output.parent / "current.json"
        previous = args.output.parent / "previous.json"
        if current.exists() and args.output.resolve() == current.resolve():
            shutil.copy2(current, previous)
        snapshot = fetch(config, token)
        args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "course_count": len(snapshot["courses"]), "generated_at": snapshot["generated_at"]}))
        return 0
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Canvas snapshot failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
