import unittest

from app.simulation import build_demo_simulation, one_business_timeline, simulate_business_fit


class OneBusinessSimulationTests(unittest.TestCase):
    def test_dental_listing_is_scored_with_explainable_signals(self):
        campaign = {
            "business_type": "UK dental practice",
            "industry": "Healthcare",
            "country": "United Kingdom",
            "region": "West Midlands",
        }
        business = {
            "business_name": "Demo Dental Practice",
            "business_type": "Dentist",
            "industry": "",
            "source_url": "https://example.invalid/demo-listing",
            "website": "",
            "business_email": "",
            "business_phone": "",
            "city": "Birmingham",
            "region": "West Midlands",
            "country": "England",
        }

        result = simulate_business_fit(campaign, business)

        self.assertEqual(result["components"][0]["score"], 92)
        self.assertEqual(result["components"][1]["score"], 100)
        self.assertEqual(result["components"][3]["score"], 100)
        self.assertEqual(result["score"], 66)
        self.assertEqual(result["band"], "review fit")
        self.assertIn("not a sales prediction", result["method"])

    def test_wrong_business_type_is_flagged_and_timeline_never_sends(self):
        result = simulate_business_fit(
            {"business_type": "Dental practice", "industry": "Healthcare", "country": "United Kingdom"},
            {
                "business_name": "Demo Beauty Salon",
                "business_type": "Beauty salon",
                "source_url": "https://example.invalid/source",
                "country": "England",
            },
        )
        timeline = one_business_timeline("new")

        self.assertEqual(result["components"][0]["score"], 28)
        self.assertTrue(all("send" not in step["action"].lower() or "manually" in step["action"].lower() for step in timeline))
        self.assertIn("do not assume a sale", timeline[-1]["action"])

    def test_demo_is_synthetic_and_never_saves_or_sends(self):
        result = build_demo_simulation()

        self.assertTrue(result["demo"])
        self.assertEqual(result["business"]["name"], "Example Dental Practice")
        self.assertFalse(result["saved"])
        self.assertFalse(result["sent"])
        self.assertEqual(result["draft_mode"], "Local demo (no AI call)")
        self.assertEqual(result["business"]["source_url"], "")
        self.assertIn("Synthetic example only", result["note"])


if __name__ == "__main__":
    unittest.main()
