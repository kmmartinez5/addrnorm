# Lookup tables for USPS-style address standardization.
# Suffix/directional abbreviations follow USPS Publication 28; this is a
# working subset covering the common cases, not the full appendix list.

STATE_ABBR = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "DISTRICT OF COLUMBIA": "DC", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI",
    "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA",
    "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME",
    "MARYLAND": "MD", "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN",
    "MISSISSIPPI": "MS", "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE",
    "NEVADA": "NV", "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM",
    "NEW YORK": "NY", "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH",
    "OKLAHOMA": "OK", "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC", "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX",
    "UTAH": "UT", "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV", "WISCONSIN": "WI", "WYOMING": "WY",
}

DIRECTIONALS = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}

STREET_SUFFIXES = {
    "ALLEY": "ALY", "AVENUE": "AVE", "BOULEVARD": "BLVD", "BRANCH": "BR",
    "BRIDGE": "BRG", "CANYON": "CYN", "CAUSEWAY": "CSWY", "CIRCLE": "CIR",
    "COURT": "CT", "COVE": "CV", "CREEK": "CRK", "CROSSING": "XING",
    "DRIVE": "DR", "EXPRESSWAY": "EXPY", "EXTENSION": "EXT", "FREEWAY": "FWY",
    "GARDENS": "GDNS", "HARBOR": "HBR", "HEIGHTS": "HTS", "HIGHWAY": "HWY",
    "HILL": "HL", "HOLLOW": "HOLW", "ISLAND": "IS", "JUNCTION": "JCT",
    "LANDING": "LNDG", "LANE": "LN", "LOOP": "LOOP", "MOUNTAIN": "MTN",
    "PARK": "PARK", "PARKWAY": "PKWY", "PASS": "PASS", "PATH": "PATH",
    "PIKE": "PIKE", "PLACE": "PL", "PLAZA": "PLZ", "POINT": "PT",
    "RIDGE": "RDG", "ROAD": "RD", "ROUTE": "RTE", "SPRING": "SPG",
    "SQUARE": "SQ", "STATION": "STA", "STREET": "ST", "SUMMIT": "SMT",
    "TERRACE": "TER", "TRAIL": "TRL", "TUNNEL": "TUNL", "TURNPIKE": "TPKE",
    "VALLEY": "VLY", "VIEW": "VW", "VILLAGE": "VLG", "WAY": "WAY",
}

UNIT_DESIGNATORS = {
    "APARTMENT": "APT", "BUILDING": "BLDG", "DEPARTMENT": "DEPT",
    "FLOOR": "FL", "ROOM": "RM", "SUITE": "STE", "UNIT": "UNIT",
}
