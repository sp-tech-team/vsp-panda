from __future__ import annotations

from datetime import date, datetime
import random
import string
from typing import Any

import phonenumbers
from phonenumbers import NumberParseException

from entities import CountryCode, Request


def normalize_email(email: str | None) -> str | None:
    """Normalize an email address for comparison."""
    if email is None:
        return None

    normalized = email.strip().casefold()
    return normalized or None

def normalize_phone_number(phone_number: str | None, region: str = "IN") -> str | None:
    """
    Normalize a phone number to E.164.

    The region is used only when the supplied number does not contain
    an international country calling code.
    """
    if phone_number is None:
        return None

    value = phone_number.strip()
    if not value:
        return None

    try:
        parsed_number = phonenumbers.parse(value, region)

        if not phonenumbers.is_valid_number(parsed_number):
            return None

        return phonenumbers.format_number(
            parsed_number,
            phonenumbers.PhoneNumberFormat.E164,
        )
    except NumberParseException:
        return None

def normalize_stored_phone_number(phone_number: str | None) -> str | None:
    """
    Normalize a phone number stored in the Volunteer sheet.

    Current application rule: numbers without an international prefix
    are treated as Indian numbers. This can be replaced later.
    """
    if phone_number is None:
        return None

    value = phone_number.strip()
    if not value:
        return None

    if not value.startswith("+"):
        value = f"+91{value}" # ** Need to move to settings

    return normalize_phone_number(value)

def phone_numbers_match(
    stored_phone_number: str | None,
    input_phone_number: str | None,
) -> bool:
    """
    Compare a stored phone number with user input.

    This is intentionally isolated so the application's matching rules
    can be replaced later without changing the repository or UI.
    """
    normalized_stored = normalize_stored_phone_number(stored_phone_number)
    normalized_input = normalize_phone_number(input_phone_number)

    if normalized_stored is None or normalized_input is None:
        return False

    return normalized_stored == normalized_input

def parse_date(value: Any) -> date | None:
    """Convert a Google Sheets date value to a date."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = str(value).strip()
    if not value:
        return None

    return datetime.strptime(value, "%m/%d/%Y").date() # ** Need to move to settings

def get_country_code_map() -> list[CountryCode]:
    """Generate country code list (Without Flags)"""

    country_codes: list[CountryCode] = []

    for cc in sorted(phonenumbers.COUNTRY_CODE_TO_REGION_CODE.keys()):
        regions = phonenumbers.COUNTRY_CODE_TO_REGION_CODE[cc]
        if regions:
            country_codes.append(CountryCode(
                region = regions[0], # Use the first region if multiple exist
                country_code = cc
            ))

    return country_codes

def generate_request_id(vol_cat_code: str, existing_requests: list[str]):
    full_prefix = f"REQ-{vol_cat_code}"

    existing_numbers = sorted([
        int(request_id.replace(full_prefix, "")) for request_id in existing_requests 
        if request_id.startswith(full_prefix) and request_id.replace(full_prefix, "").isdigit()
    ])

    next_number = 1
    for num in existing_numbers:
        if num == next_number:
            next_number += 1
        else:
            break

    if next_number > 99999:
        for _ in range(10000):
            random_alnum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            request_id = f"{full_prefix}{random_alnum}"
            if request_id not in existing_requests:
                return request_id
        return f"{full_prefix}XXXXX"

    request_id = f"{full_prefix}{next_number:05d}"
    return request_id

# region read appsettings.json

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

APP_SETTINGS_FILE = Path(__file__).resolve().parent / "appsettings.json"


@lru_cache(maxsize=1)
def _load_settings() -> dict[str, Any]:
    """Load and cache application settings from appsettings.json."""

    if not APP_SETTINGS_FILE.exists():
        raise FileNotFoundError(
            f"Application settings file not found: {APP_SETTINGS_FILE}"
        )

    try:
        with APP_SETTINGS_FILE.open("r", encoding="utf-8") as file:
            settings = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {APP_SETTINGS_FILE}: {exc}"
        ) from exc

    if not isinstance(settings, dict):
        raise ValueError(
            f"Expected {APP_SETTINGS_FILE} to contain a JSON object."
        )

    return settings


def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting from appsettings.json.

    Supports both top-level and nested keys using dot notation.
    """

    if not key.strip():
        raise ValueError("Setting key cannot be empty.")

    value: Any = _load_settings()

    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            if default is not None:
                return default

            raise KeyError(
                f"Setting '{key}' was not found in {APP_SETTINGS_FILE}"
            )

        value = value[part]

    return value

# endregion
