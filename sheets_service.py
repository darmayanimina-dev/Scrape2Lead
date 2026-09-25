import json
import re
from datetime import datetime, timezone, timedelta
from typing import Set, Dict, Any, Optional
import requests
from config import DEFAULT_SHEETS_WEBAPP_URL


def clean_phone(raw_phone: str) -> str:
    """Format and validate Indonesian phone numbers into +62 standard."""
    if not raw_phone:
        return ""
    digits = re.sub(r"\D", "", raw_phone)
    if digits.startswith("0"):
        formatted = "+62" + digits[1:]
    elif digits.startswith("62"):
        formatted = "+" + digits
    else:
        formatted = "+62" + digits
    return formatted if 10 <= len(formatted) <= 16 else ""


def get_now_wita_str() -> str:
    """Get current time formatted in WITA (UTC+8)."""
    tz_wita = timezone(timedelta(hours=8))
    return datetime.now(tz_wita).strftime("%Y-%m-%d %H:%M:%S")


def get_existing_numbers(webapp_url: str = DEFAULT_SHEETS_WEBAPP_URL) -> Set[str]:
    """Fetch set of phone numbers already recorded in Google Sheets to avoid duplicates."""
    try:
        res = requests.get(webapp_url, timeout=15)
        if res.status_code == 200:
            data = res.json()
            # Clean and normalize existing numbers
            cleaned = set()
            for n in data:
                c = clean_phone(str(n))
                if c:
                    cleaned.add(c)
                cleaned.add(str(n).strip())
            return cleaned
    except Exception as e:
        print(f"[Sheets Warning] Could not fetch existing numbers: {e}")
    return set()


def update_live_progress(
    status: str,
    message: str,
    count: int,
    webapp_url: str = DEFAULT_SHEETS_WEBAPP_URL
) -> bool:
    """Update live progress on Google Sheets WebApp."""
    payload = {
        "action": "update_progress",
        "status": status,
        "message": message,
        "count": count
    }
    try:
        res = requests.post(webapp_url, data=json.dumps(payload), timeout=8)
        return res.status_code == 200
    except Exception as e:
        print(f"[Sheets Warning] Could not update live progress: {e}")
        return False


def send_lead_to_master(
    name: str,
    category: str,
    area: str,
    phone: str,
    address: str,
    url: str,
    current_total: int,
    webapp_url: str = DEFAULT_SHEETS_WEBAPP_URL
) -> bool:
    """Push newly scraped lead into master Google Sheets."""
    payload = {
        "action": "insert_lead",
        "name": name,
        "category": category,
        "area": area,
        "phone": phone,
        "address": address,
        "url": url,
        "date": get_now_wita_str(),
        "current_total": current_total
    }
    try:
        res = requests.post(webapp_url, data=json.dumps(payload), timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"[Sheets Warning] Could not insert lead: {e}")
        return False


def check_remote_task(webapp_url: str = DEFAULT_SHEETS_WEBAPP_URL) -> Optional[Dict[str, Any]]:
    """Poll Google Sheets to check if remote execution was requested."""
    try:
        res = requests.get(f"{webapp_url}?action=check_task", timeout=12)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"[Sheets Warning] Error checking task: {e}")
    return None
