"""Command-line entry point for addrnorm."""

import argparse
import json
import sys

from .normalize import AddressError, format_address, parse_address


def _read_addresses(args):
    if args.address:
        return [" ".join(args.address)]
    lines = [line.rstrip("\n") for line in sys.stdin if line.strip()]
    return lines


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
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

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
