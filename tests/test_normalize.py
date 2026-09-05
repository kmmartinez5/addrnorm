import unittest

from addrnorm.normalize import AddressError, _split_state, address_key, format_address, parse_address


class ParseAddressTests(unittest.TestCase):
    def test_readme_example(self):
        parts = parse_address("123 north main street, springfield, illinois 62704")
        self.assertEqual(
            parts,
            {"street": "123 N MAIN ST", "unit": None, "city": "SPRINGFIELD", "state": "IL", "zip": "62704"},
        )

    def test_case_insensitive_and_already_abbreviated(self):
        parts = parse_address("100 W. Elm St., Chicago, IL 60601")
        self.assertEqual(parts["street"], "100 W ELM ST")
        self.assertEqual(parts["state"], "IL")

    def test_ragged_whitespace_and_zip_plus_four(self):
        raw = "  789   SOUTHWEST   broadway ,  portland , oregon   97205-1234  "
        parts = parse_address(raw)
        self.assertEqual(parts["street"], "789 SW BROADWAY")
        self.assertEqual(parts["city"], "PORTLAND")
        self.assertEqual(parts["state"], "OR")
        self.assertEqual(parts["zip"], "97205-1234")

    def test_state_without_comma_before_it(self):
        # Very common real-world shape: only one comma, between street and
        # city, with the state just space-separated after the city.
        parts = parse_address("123 Main St, Springfield IL 62704")
        self.assertEqual(parts["street"], "123 MAIN ST")
        self.assertEqual(parts["city"], "SPRINGFIELD")
        self.assertEqual(parts["state"], "IL")

    def test_two_word_state_name_without_comma(self):
        parts = parse_address("10 Elm St, Buffalo New York 14201")
        self.assertEqual(parts["city"], "BUFFALO")
        self.assertEqual(parts["state"], "NY")

    def test_three_word_state_name_without_comma(self):
        parts = parse_address("1600 Pennsylvania Ave, Washington District of Columbia 20500")
        self.assertEqual(parts["city"], "WASHINGTON")
        self.assertEqual(parts["state"], "DC")

    def test_apartment_unit_becomes_own_field(self):
        parts = parse_address("456 Oak Avenue Apt 2, Denver, CO 80202")
        self.assertEqual(parts["street"], "456 OAK AVE")
        self.assertEqual(parts["unit"], "APT 2")

    def test_suite_unit_lowercase(self):
        parts = parse_address("200 main st suite 100, austin, tx 78701")
        self.assertEqual(parts["street"], "200 MAIN ST")
        self.assertEqual(parts["unit"], "STE 100")

    def test_hash_unit_kept_as_is(self):
        parts = parse_address("456 Oak Ave #4b, Denver, CO 80202")
        self.assertEqual(parts["street"], "456 OAK AVE")
        self.assertEqual(parts["unit"], "#4B")

    def test_building_and_apartment_combo_unit(self):
        parts = parse_address("300 Elm St Bldg 3 Apt 200, Boston, MA 02101")
        self.assertEqual(parts["street"], "300 ELM ST")
        self.assertEqual(parts["unit"], "BLDG 3 APT 200")

    def test_no_unit_present(self):
        parts = parse_address("123 Main St, Springfield, IL 62704")
        self.assertIsNone(parts["unit"])

    def test_directional_word_abbreviated(self):
        parts = parse_address("50 Northeast 2nd Ave, Portland, OR 97232")
        self.assertEqual(parts["street"], "50 NE 2ND AVE")

    def test_directional_already_abbreviated_passes_through(self):
        parts = parse_address("50 NE 2nd Ave, Portland, OR 97232")
        self.assertEqual(parts["street"], "50 NE 2ND AVE")

    def test_empty_input_raises(self):
        with self.assertRaises(AddressError):
            parse_address("   ")

    def test_missing_zip_raises(self):
        with self.assertRaises(AddressError):
            parse_address("123 Main St, Springfield, IL")

    def test_unrecognized_state_raises(self):
        with self.assertRaises(AddressError):
            parse_address("123 Main St, Springfield, Nowhereland 62704")

    def test_missing_street_city_separator_raises(self):
        with self.assertRaises(AddressError) as ctx:
            parse_address("123 Main St IL 62704")
        self.assertIn("could not separate street and city", str(ctx.exception))


class SplitStateTests(unittest.TestCase):
    def test_comma_before_state(self):
        head, state = _split_state("123 Main St, Springfield, IL")
        self.assertEqual(head, "123 Main St, Springfield")
        self.assertEqual(state, "IL")

    def test_no_comma_before_state(self):
        head, state = _split_state("123 Main St, Springfield IL")
        self.assertEqual(head, "123 Main St, Springfield")
        self.assertEqual(state, "IL")

    def test_no_state_found(self):
        head, state = _split_state("123 Main St, Nowhereland")
        self.assertIsNone(state)
        self.assertEqual(head, "123 Main St, Nowhereland")


class FormatAddressTests(unittest.TestCase):
    def test_single_line_with_unit(self):
        parts = {"street": "456 OAK AVE", "unit": "APT 2", "city": "DENVER", "state": "CO", "zip": "80202"}
        self.assertEqual(format_address(parts), "456 OAK AVE APT 2, DENVER, CO 80202")

    def test_single_line_without_unit(self):
        parts = {"street": "123 MAIN ST", "unit": None, "city": "SPRINGFIELD", "state": "IL", "zip": "62704"}
        self.assertEqual(format_address(parts), "123 MAIN ST, SPRINGFIELD, IL 62704")

    def test_multiline(self):
        parts = {"street": "123 MAIN ST", "unit": None, "city": "SPRINGFIELD", "state": "IL", "zip": "62704"}
        self.assertEqual(format_address(parts, multiline=True), "123 MAIN ST\nSPRINGFIELD, IL 62704")


class AddressKeyTests(unittest.TestCase):
    def test_zip_plus_four_ignored(self):
        a = parse_address("123 Main St, Springfield, IL 62704")
        b = parse_address("123 Main St, Springfield, IL 62704-1234")
        self.assertEqual(address_key(a), address_key(b))

    def test_missing_unit_matches_no_unit(self):
        a = parse_address("123 Main St, Springfield, IL 62704")
        b = dict(a, unit="")
        self.assertEqual(address_key(a), address_key(b))

    def test_different_unit_is_not_equal(self):
        a = parse_address("456 Oak Ave Apt 2, Denver, CO 80202")
        b = parse_address("456 Oak Ave Apt 3, Denver, CO 80202")
        self.assertNotEqual(address_key(a), address_key(b))

    def test_different_street_is_not_equal(self):
        a = parse_address("123 Main St, Springfield, IL 62704")
        b = parse_address("124 Main St, Springfield, IL 62704")
        self.assertNotEqual(address_key(a), address_key(b))


if __name__ == "__main__":
    unittest.main()
