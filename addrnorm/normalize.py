"""Parse and format US postal addresses in USPS-style standard form.

Standardization rules (abbreviated street suffixes, directionals, state
codes, uppercasing) follow the spirit of USPS Publication 28. This is not
a CASS-certified implementation - it does not validate against the actual
delivery-point database, just normalizes formatting.
"""

import re

from .data import DIRECTIONALS, STATE_ABBR, STREET_SUFFIXES, UNIT_DESIGNATORS

_ZIP_RE = re.compile(r"(\d{5})(-\d{4})?\s*$")
_STATE_ABBR_SET = set(STATE_ABBR.values())


class AddressError(ValueError):
    """Raised when input text can't be parsed as a US postal address."""


def _abbreviate_word(word):
    upper = word.strip(".,").upper()
    if not upper:
        return ""
    if upper in DIRECTIONALS:
        return DIRECTIONALS[upper]
    if upper in STREET_SUFFIXES:
        return STREET_SUFFIXES[upper]
    if upper in UNIT_DESIGNATORS:
        return UNIT_DESIGNATORS[upper]
    return upper


def _normalize_street(street):
    words = [w for w in street.split() if w]
    return " ".join(_abbreviate_word(w) for w in words)


def _resolve_state(token):
    upper = token.strip(" .,").upper()
    if upper in _STATE_ABBR_SET:
        return upper
    if upper in STATE_ABBR:
        return STATE_ABBR[upper]
    return None


def parse_address(raw):
    """Parse "STREET, CITY, STATE ZIP" style text into components.

    Accepts a state name or two-letter code, with or without a comma
    before it, and a 5 or 9 digit ZIP. Raises AddressError if the text
    doesn't contain a recognizable ZIP, state, city, and street.
    """
    text = raw.strip()
    if not text:
        raise AddressError("empty address")

    zip_match = _ZIP_RE.search(text)
    if not zip_match:
        raise AddressError(f"no ZIP code found in: {raw!r}")
    zip_code = zip_match.group(1) + (zip_match.group(2) or "")
    remainder = text[: zip_match.start()].strip().rstrip(",").strip()

    if "," in remainder:
        head, _, state_token = remainder.rpartition(",")
    else:
        head, _, state_token = remainder.rpartition(" ")
    state = _resolve_state(state_token)
    if state is None:
        raise AddressError(f"unrecognized state in: {raw!r}")

    head = head.strip().rstrip(",").strip()
    if "," not in head:
        raise AddressError(f"could not separate street and city in: {raw!r}")
    street_part, _, city_part = head.rpartition(",")

    street = _normalize_street(street_part.strip())
    city = city_part.strip().upper()
    if not street or not city:
        raise AddressError(f"missing street or city in: {raw!r}")

    return {"street": street, "city": city, "state": state, "zip": zip_code}


def format_address(parts, multiline=False):
    """Render parsed components back into standardized text."""
    line1 = parts["street"]
    line2 = f'{parts["city"]}, {parts["state"]} {parts["zip"]}'
    return f"{line1}\n{line2}" if multiline else f"{line1}, {line2}"
