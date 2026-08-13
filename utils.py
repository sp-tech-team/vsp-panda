from __future__ import annotations

from datetime import date, datetime
from typing import Any

import phonenumbers
from phonenumbers import NumberParseException


def normalize_email(email: str | None) -> str | None:
    """Normalize an email address for comparison."""
    if email is None:
        return None

    normalized = email.strip().casefold()
    return normalized or None

def normalize_phone_number(
    phone_number: str | None,
    region: str = "IN",
) -> str | None:
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

def parse_departure_date(value: Any) -> date | None:
    """Convert a Google Sheets dd/MM/yyyy value to a date."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = str(value).strip()
    if not value:
        return None

    return datetime.strptime(value, "%d-%m-%Y").date() # ** Need to move to settings

def get_country_code_map():
    """Generate country code list (Without Flags)"""

    country_code_map = {}

    for cc in sorted(phonenumbers.COUNTRY_CODE_TO_REGION_CODE.keys()):
        regions = phonenumbers.COUNTRY_CODE_TO_REGION_CODE[cc]
        if regions:
            region = regions[0]  # Use the first region if multiple exist
            key = f"{region} (+{cc})"
            country_code_map[key] = str(cc)

    return country_code_map