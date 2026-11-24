import unittest

from app.csv_import import MAX_CSV_BYTES, MAX_CSV_ROWS, parse_business_csv


class BusinessCsvImportTests(unittest.TestCase):
    def test_parses_utf8_bom_semicolon_export_and_normalizes_websites(self):
        content = (
            "\ufeffCompany;Website URL;Phone;Public Email;Town;Listing URL\n"
            "Sample Dental;sample-dental.invalid;+44 20 5555 0100;hello@example.invalid;Leeds;https://directory.invalid/sample\n"
        ).encode("utf-8")

        result = parse_business_csv(content)

        self.assertEqual(len(result["rows"]), 1)
        row = result["rows"][0]
        self.assertEqual(row["business_name"], "Sample Dental")
        self.assertEqual(row["website"], "https://sample-dental.invalid")
        self.assertEqual(row["source_url"], "https://directory.invalid/sample")
        self.assertEqual(row["business_email"], "hello@example.invalid")
        self.assertEqual(result["invalid"], [])

    def test_skips_missing_names_sources_and_malformed_urls(self):
        content = (
            "name,website,source_url\n"
            "No source,,\n"
            ",https://example.invalid,https://example.invalid/listing\n"
            "Bad URL,javascript:alert(1),https://example.invalid/listing\n"
        ).encode("utf-8")

        result = parse_business_csv(content)

        self.assertEqual(result["rows"], [])
        self.assertEqual(len(result["invalid"]), 3)

    def test_requires_name_header_and_enforces_file_and_row_limits(self):
        with self.assertRaisesRegex(ValueError, "column named business_name"):
            parse_business_csv(b"email,website\na@example.invalid,https://example.invalid\n")
        with self.assertRaisesRegex(ValueError, "5 MB"):
            parse_business_csv(b"x" * (MAX_CSV_BYTES + 1))
        too_many = "name,website,source_url\n" + "A,https://a.invalid,https://a.invalid\n" * (MAX_CSV_ROWS + 1)
        with self.assertRaisesRegex(ValueError, "more than 2,000 rows"):
            parse_business_csv(too_many.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
