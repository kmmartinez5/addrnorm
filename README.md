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
{"street": "123 MAIN ST", "unit": null, "city": "SPRINGFIELD", "state": "IL", "zip": "62704"}
```

A secondary unit designator (apartment, suite, building, ...) is tracked as
its own `unit` field rather than being folded into the street string:

```
$ addrnorm --json "456 Oak Ave Apt 2, Denver, CO 80202"
{"street": "456 OAK AVE", "unit": "APT 2", "city": "DENVER", "state": "CO", "zip": "80202"}
```

A bare `#4` style unit number is kept as-is, since there's no designator
word to standardize:

```
$ addrnorm --json "456 Oak Ave #4, Denver, CO 80202"
{"street": "456 OAK AVE", "unit": "#4", "city": "DENVER", "state": "CO", "zip": "80202"}
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

Drop duplicates from a list, keeping the first occurrence of each address.
Two entries count as the same address if they normalize to the same street,
unit, city, state, and 5-digit ZIP - a ZIP+4 extension and a missing vs.
blank unit don't count as a difference:

```
$ cat addresses.txt
123 Main St, Springfield, IL 62704
123 MAIN STREET, SPRINGFIELD, IL 62704-1234
456 Oak Ave Apt 2, Denver, CO 80202

$ addrnorm --dedup < addresses.txt
123 MAIN ST, SPRINGFIELD, IL 62704
456 OAK AVE APT 2, DENVER, CO 80202
```

`--dedup` isn't available with `--file`; batch mode always writes back one
output row per input row.

## Batch mode

For a CSV file with an `address` column (the column name is matched
case-insensitively), `--file` normalizes every row and writes the original
columns back out with the parsed components appended:

```
$ cat addresses.csv
id,address
1,"123 Main St, Springfield, IL 62704"
2,"456 Oak Avenue Apt 2, Denver, Colorado 80202"

$ addrnorm --file addresses.csv
id,address,street,unit,city,state,zip,error
1,"123 Main St, Springfield, IL 62704",123 MAIN ST,,SPRINGFIELD,IL,62704,
2,"456 Oak Avenue Apt 2, Denver, Colorado 80202",456 OAK AVE,APT 2,DENVER,CO,80202,
```

A row that fails to parse is still written, with the normalized columns
left blank and the reason in `error`, so a batch run never silently drops
input. Use `--out` to write to a file instead of stdout:

```
$ addrnorm --file addresses.csv --out normalized.csv
```

## How parsing works

The parser expects something shaped like `STREET, CITY, STATE ZIP`:

1. Find a trailing 5-digit or ZIP+4 code.
2. Work backward to find a state - either a two-letter code or a full state
   name, comma-separated or not.
3. Split what's left on the last remaining comma into street and city.
4. Pull a secondary unit designator off the end of the street, if there is
   one - a recognized word like Apartment/Apt/Suite/Ste plus whatever
   follows it, a two-word phrase like "Mobile Home" or "Trailer Space"
   that has no official USPS abbreviation but is still recognized as a
   designator, or a bare `#4` style unit number. This becomes its own
   `unit` field instead of trailing text on the street.
5. Normalize each word of the remaining street against lookup tables for
   directionals (North -> N) and street suffixes (Avenue -> AVE).

Addresses that don't roughly follow that shape - missing commas, missing
state, no ZIP - will fail to parse. See `addrnorm/data.py` for the current
abbreviation tables.

## License

MIT, see LICENSE.
