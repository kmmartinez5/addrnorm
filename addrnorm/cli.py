"""Command-line entry point for addrnorm."""

import argparse
import csv
import json
import sys

from .normalize import AddressError, format_address, parse_address

_NORMALIZED_FIELDNAMES = ["street", "unit", "city", "state", "zip", "error"]


def _read_addresses(args):
    if args.address:
        return [" ".join(args.address)]
    lines = [line.rstrip("\n") for line in sys.stdin if line.strip()]
    return lines


def _find_address_column(fieldnames):
    for name in fieldnames:
        if name and name.strip().lower() == "address":
            return name
    return None


def _run_csv(in_path, out_path):
    """Normalize every row of a CSV file that has an "address" column.

    Original columns are kept and the normalized components are appended.
    A row that fails to parse is still written, with the normalized
    columns left blank and the reason in "error", so a batch run never
    silently drops input. Returns True if any row failed to parse.
    """
    with open(in_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise ValueError(f"{in_path} has no header row")
        column = _find_address_column(reader.fieldnames)
        if column is None:
            raise ValueError(f'{in_path} has no "address" column')
        rows = list(reader)
        fieldnames = list(reader.fieldnames) + [
            name for name in _NORMALIZED_FIELDNAMES if name not in reader.fieldnames
        ]

    out = open(out_path, "w", newline="", encoding="utf-8") if out_path else sys.stdout
    had_error = False
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                parts = parse_address(row[column])
            except AddressError as exc:
                had_error = True
                row.update({name: "" for name in _NORMALIZED_FIELDNAMES})
                row["error"] = str(exc)
            else:
                row.update(parts)
                row["unit"] = parts["unit"] or ""
                row["error"] = ""
            writer.writerow(row)
    finally:
        if out is not sys.stdout:
            out.close()
    return had_error


def build_parser():
    parser = argparse.ArgumentParser(
        prog="addrnorm",
        description="Normalize a US postal address into USPS-style standard form.",
    )
    parser.add_argument(
        "address",
        nargs="*",
        help="address text, e.g. '123 main street, springfield, il 62704'. "
        "If omitted, addresses are read one per line from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print each result as a JSON object instead of formatted text",
    )
    parser.add_argument(
        "--multiline",
        action="store_true",
        help="print street on one line, city/state/zip on the next",
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        help='batch mode: read addresses from a CSV file with an "address" '
        "column, and write the normalized components alongside the "
        "original columns. Ignores stdin and any address arguments.",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="write --file output to this CSV file instead of stdout",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.out and not args.file:
        parser.error("--out requires --file")

    if args.file:
        if args.address:
            parser.error("--file can't be combined with address arguments")
        try:
            had_error = _run_csv(args.file, args.out)
        except (ValueError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 1 if had_error else 0

    addresses = _read_addresses(args)
    if not addresses:
        parser.error("no address given as an argument and nothing on stdin")

    exit_code = 0
    for raw in addresses:
        try:
            parts = parse_address(raw)
        except AddressError as exc:
            print(f"error: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        if args.json:
            print(json.dumps(parts))
        else:
            print(format_address(parts, multiline=args.multiline))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
