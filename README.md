# addrnorm

Addresses that mean the same thing get typed a dozen different ways: "Street"
vs "St", "Apartment 4" vs "Apt 4" vs "#4", full state names vs codes, random
casing. That inconsistency breaks naive deduplication and looks unprofessional
on anything you print or mail. `addrnorm` takes a freeform US address and
rewrites it in a consistent USPS-style standard form: uppercase, abbreviated
street suffixes and directionals, two-letter state codes.

It is not a CASS-certified validator and it does not check that an address
actually exists - it just normalizes formatting so that equivalent addresses
come out looking identical.

## Install

No dependencies beyond the Python standard library.

```
pip install -e .
```

## Usage

Pass an address as arguments:

```
$ addrnorm "123 north main street, springfield, illinois 62704"
123 N MAIN ST, SPRINGFIELD, IL 62704
```

Or pipe addresses in, one per line:

```
$ cat addresses.txt
456 Oak Avenue Apt 2, Denver, CO 80202
789 Southwest Broadway, Portland, Oregon 97205-1234

$ addrnorm < addresses.txt
456 OAK AVE APT 2, DENVER, CO 80202
789 SW BROADWAY, PORTLAND, OR 97205-1234
```

Get structured output instead of a formatted line:

```
$ addrnorm --json "123 Main St, Springfield, IL 62704"
{"street": "123 MAIN ST", "city": "SPRINGFIELD", "state": "IL", "zip": "62704"}
```

Print street and city/state/zip on separate lines, mailing-label style:

```
$ addrnorm --multiline "123 Main St, Springfield, IL 62704"
123 MAIN ST
SPRINGFIELD, IL 62704
```

Addresses that don't parse (no ZIP found, no recognizable state, street and
city not separated by a comma) are reported to stderr and skipped; the
process exits non-zero if any address failed.

## How parsing works

The parser expects something shaped like `STREET, CITY, STATE ZIP`:

1. Find a trailing 5-digit or ZIP+4 code.
2. Work backward to find a state - either a two-letter code or a full state
   name, comma-separated or not.
3. Split what's left on the last remaining comma into street and city.
4. Normalize each word of the street against lookup tables for directionals
   (North -> N), street suffixes (Avenue -> AVE), and unit designators
   (Apartment -> APT).

Addresses that don't roughly follow that shape - missing commas, missing
state, no ZIP - will fail to parse. See `addrnorm/data.py` for the current
abbreviation tables.

## License

MIT, see LICENSE.
