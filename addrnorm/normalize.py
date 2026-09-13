"""Parse and format US postal addresses in USPS-style standard form.

Standardization rules (abbreviated street suffixes, directionals, state
codes, uppercasing) follow the spirit of USPS Publication 28. This is not
a CASS-certified implementation - it does not validate against the actual
delivery-point database, just normalizes formatting.
"""

import re

from .data import (
    DIRECTIONALS,
    MULTI_WORD_UNIT_DESIGNATORS,
    STATE_ABBR,
    STREET_SUFFIXES,
    UNIT_DESIGNATORS,
)

_ZIP_RE = re.compile(r"(\d{5})(-\d{4})?\s*$")
_STATE_ABBR_SET = set(STATE_ABBR.values())
_UNIT_DESIGNATOR_TOKENS = set(UNIT_DESIGNATORS) | set(UNIT_DESIGNATORS.values())
_HASH_UNIT_RE = re.compile(r"^#(\w+)$")

# A PO Box has no street suffix for the word-by-word abbreviation pass to
# key off of, and "P.O." in particular has an internal period that
# _abbreviate_word's leading/trailing strip() never touches, so it would
# otherwise pass through unchanged instead of collapsing to the one USPS
# form. Matched and rewritten as a whole before that pass runs. Requires
# the "P.O."/"POST OFFICE" prefix so a real street name that happens to
# start with "Box" (e.g. "Box Elder Court") isn't mistaken for one.
_PO_BOX_RE = re.compile(
    r"^(?:POST\s+OFFICE\s+BOX|P\.?\s*O\.?\s*BOX)\s+(\S.*)$",
    re.IGNORECASE,
)


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
    po_box_match = _PO_BOX_RE.match(street.strip())
    if po_box_match:
        box_id = po_box_match.group(1).strip().rstrip(".,").upper()
        return f"PO BOX {box_id}"
    words = [w for w in street.split() if w]
    return " ".join(_abbreviate_word(w) for w in words)


def _split_unit(street_part):
    """Pull a secondary unit designator (APT 4, STE 200, #12, ...) off the
    end of a street string, so it can be tracked as its own field instead
    of being just more text tacked onto the street line.

    Everything from the first recognized designator word to the end of the
    street text becomes the unit, which covers "BLDG 3 APT 200" without
    trying to track multiple separate unit fields. A two-word designator
    like "MOBILE HOME" is checked before the single-word tokens so its
    first word isn't mistaken for part of the street name.
    """
    words = [w for w in street_part.split() if w]
    for i, word in enumerate(words):
        stripped = word.strip(".,").upper()
        if i + 1 < len(words):
            next_stripped = words[i + 1].strip(".,").upper()
            if (stripped, next_stripped) in MULTI_WORD_UNIT_DESIGNATORS:
                unit = " ".join(w for w in (_abbreviate_word(w) for w in words[i:]) if w)
                return " ".join(words[:i]), unit or None
        if stripped in _UNIT_DESIGNATOR_TOKENS:
            unit = " ".join(w for w in (_abbreviate_word(w) for w in words[i:]) if w)
            return " ".join(words[:i]), unit or None
        hash_match = _HASH_UNIT_RE.match(word)
        if hash_match:
            remaining = words[:i] + words[i + 1 :]
            return " ".join(remaining), f"#{hash_match.group(1).upper()}"
    return street_part, None


def _resolve_state(token):
    upper = token.strip(" .,").upper()
    if upper in _STATE_ABBR_SET:
        return upper
    if upper in STATE_ABBR:
        return STATE_ABBR[upper]
    return None


_MAX_STATE_WORDS = 3  # "DISTRICT OF COLUMBIA" is the longest state name


def _split_state(remainder):
    """Split "...STREET, CITY[,] STATE" into (head, state abbreviation).

    The state may be preceded by a comma or just whitespace, and may be a
    two-letter code or a full name of one to three words ("NEW YORK",
    "DISTRICT OF COLUMBIA"). Trying the comma split first, then falling
    back to a word-count split, means "..., Springfield, IL" and the far
    more common "..., Springfield IL" (comma before city only) both work.
    Returns (remainder, None) if no state is found.
    """
    stripped = remainder.rstrip()
    if "," in stripped:
        head, _, tail = stripped.rpartition(",")
        state = _resolve_state(tail)
        if state is not None:
            return head.strip(), state

    words = stripped.split()
    for word_count in range(_MAX_STATE_WORDS, 0, -1):
        if len(words) <= word_count:
            continue
        state = _resolve_state(" ".join(words[-word_count:]))
        if state is not None:
            return " ".join(words[:-word_count]), state
    return remainder, None


def parse_address(raw):
    """Parse "STREET, CITY, STATE ZIP" style text into components.

    Accepts a state name or two-letter code, with or without a comma
    before it, and a 5 or 9 digit ZIP. Raises AddressError if the text
    doesn't contain a recognizable ZIP, state, city, and street.

    A secondary unit designator at the end of the street (APT 4, STE 200,
    #12, ...) is split out into its own "unit" field, which is None when
    no unit is present.
    """
    text = raw.strip()
    if not text:
        raise AddressError("empty address")

    zip_match = _ZIP_RE.search(text)
    if not zip_match:
        raise AddressError(f"no ZIP code found in: {raw!r}")
    zip_code = zip_match.group(1) + (zip_match.group(2) or "")
    remainder = text[: zip_match.start()].strip().rstrip(",").strip()

    head, state = _split_state(remainder)
    if state is None:
        raise AddressError(f"unrecognized state in: {raw!r}")

    head = head.strip().rstrip(",").strip()
    if "," not in head:
        raise AddressError(f"could not separate street and city in: {raw!r}")
    street_part, _, city_part = head.rpartition(",")

    street_text, unit = _split_unit(street_part.strip())
    street = _normalize_street(street_text)
    city = city_part.strip().upper()
    if not street or not city:
        raise AddressError(f"missing street or city in: {raw!r}")

    return {"street": street, "unit": unit, "city": city, "state": state, "zip": zip_code}


def format_address(parts, multiline=False):
    """Render parsed components back into standardized text."""
    line1 = parts["street"]
    if parts.get("unit"):
        line1 = f'{line1} {parts["unit"]}'
    line2 = f'{parts["city"]}, {parts["state"]} {parts["zip"]}'
    return f"{line1}\n{line2}" if multiline else f"{line1}, {line2}"


def address_key(parts):
    """Return a hashable key for comparing parsed addresses for equality.

    The ZIP+4 extension is dropped since it's a delivery-point detail that
    doesn't change which address is meant, and a missing unit is treated
    the same as an empty one, so callers don't need to special-case None.
    """
    return (
        parts["street"],
        parts["unit"] or "",
        parts["city"],
        parts["state"],
        parts["zip"][:5],
    )
