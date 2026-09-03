import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from addrnorm.cli import main


class MainTextOutputTests(unittest.TestCase):
    def test_prints_formatted_address(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["123 Main St, Springfield, IL 62704"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "123 MAIN ST, SPRINGFIELD, IL 62704\n")

    def test_json_flag(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--json", "456 Oak Ave Apt 2, Denver, CO 80202"])
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out.getvalue()),
            {"street": "456 OAK AVE", "unit": "APT 2", "city": "DENVER", "state": "CO", "zip": "80202"},
        )

    def test_multiline_flag(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--multiline", "123 Main St, Springfield, IL 62704"])
        self.assertEqual(out.getvalue(), "123 MAIN ST\nSPRINGFIELD, IL 62704\n")

    def test_reads_addresses_from_stdin(self):
        stdin = io.StringIO(
            "123 Main St, Springfield, IL 62704\n456 Oak Avenue Apt 2, Denver, Colorado 80202\n"
        )
        out = io.StringIO()
        with patch("sys.stdin", stdin), redirect_stdout(out):
            code = main([])
        self.assertEqual(code, 0)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[0], "123 MAIN ST, SPRINGFIELD, IL 62704")
        self.assertEqual(lines[1], "456 OAK AVE APT 2, DENVER, CO 80202")

    def test_bad_address_reports_error_and_nonzero_exit(self):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["not an address"])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("error:", err.getvalue())


class CsvBatchModeTests(unittest.TestCase):
    def _write_csv(self, path, header, rows):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def test_batch_normalizes_and_flags_bad_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "in.csv")
            out_path = os.path.join(tmpdir, "out.csv")
            self._write_csv(
                in_path,
                ["id", "address"],
                [
                    ["1", "123 Main St, Springfield, IL 62704"],
                    ["2", "456 Oak Avenue Apt 2, Denver, Colorado 80202"],
                    ["3", "garbage line with no zip"],
                ],
            )

            code = main(["--file", in_path, "--out", out_path])
            self.assertEqual(code, 1)

            with open(out_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

            self.assertEqual(rows[0]["street"], "123 MAIN ST")
            self.assertEqual(rows[0]["unit"], "")
            self.assertEqual(rows[0]["state"], "IL")
            self.assertEqual(rows[0]["error"], "")

            self.assertEqual(rows[1]["street"], "456 OAK AVE")
            self.assertEqual(rows[1]["unit"], "APT 2")
            self.assertEqual(rows[1]["state"], "CO")

            self.assertEqual(rows[2]["street"], "")
            self.assertIn("no ZIP code found", rows[2]["error"])

    def test_missing_address_column_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "in.csv")
            self._write_csv(in_path, ["id", "location"], [["1", "somewhere"]])

            err = io.StringIO()
            with redirect_stderr(err):
                code = main(["--file", in_path])
            self.assertEqual(code, 1)
            self.assertIn("no \"address\" column", err.getvalue())


if __name__ == "__main__":
    unittest.main()
