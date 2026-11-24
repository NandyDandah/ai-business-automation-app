import csv
import os
import re
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

TEST_DB = Path("work/repo-update/auth-test.db").resolve()
TEST_DB.parent.mkdir(parents=True, exist_ok=True)
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ.update({
    "APP_ENV": "testing",
    "APP_COOKIE_SECURE": "false",
    "APP_SESSION_SECRET": "test-session-secret-" + "x" * 40,
    "DATABASE_URL": "sqlite:///" + TEST_DB.as_posix(),
})

from app.security import hash_api_token, hash_password
PASSWORD = "correct horse battery staple"
TOKEN = "test-api-token-for-auth-checks-0123456789"
os.environ["APP_PASSWORD_HASH"] = hash_password(PASSWORD)
os.environ["APP_API_TOKEN_HASH"] = hash_api_token(TOKEN)

from fastapi.testclient import TestClient
from app.database import Automation, Campaign, CampaignProspect, Prospect, SessionLocal
from app.main import app, AUTH_CONFIG
from app.prospecting import ProspectingError, discover_openstreetmap_businesses
from app.security import get_session_csrf_token

FAKE_AI = {"category": "sales", "priority": "medium", "lead_score": 42, "reply": "Synthetic test reply."}


def login(client):
    page = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
    return client.post("/login", data={"password": PASSWORD, "csrf_token": csrf}, follow_redirects=False)


def session_csrf(client):
    return get_session_csrf_token(client.cookies.get("app_session", ""), AUTH_CONFIG)


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        with SessionLocal() as db:
            db.query(CampaignProspect).delete()
            db.query(Campaign).delete()
            db.query(Prospect).delete()
            db.query(Automation).delete()
            db.commit()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_private_routes_require_authentication(self):
        self.assertEqual(self.client.get("/history").status_code, 401)
        self.assertEqual(self.client.get("/export").status_code, 401)
        page = self.client.get("/dashboard", headers={"accept": "text/html"}, follow_redirects=False)
        self.assertEqual(page.status_code, 303)
        self.assertEqual(self.client.put("/history/1/status?new_status=Closed").status_code, 401)

    def test_health_check_is_public_and_reports_database_readiness(self):
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_campaign_studio_has_sample_setup_and_twenty_result_default(self):
        self.assertEqual(login(self.client).status_code, 303)
        response = self.client.get("/campaigns")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="fillSampleBrief"', response.text)
        self.assertIn('id="runDemoSimulation"', response.text)
        self.assertIn('id="campaignCsvPreviewForm"', response.text)
        self.assertIn('id="importCampaignCsv"', response.text)
        self.assertIn(
            'name="max_results"><option value="10">Up to 10</option><option value="20" selected>Up to 20</option>',
            response.text,
        )

    def test_one_business_demo_is_protected_and_does_not_call_providers(self):
        denied = self.client.post("/api/simulations/one-business-demo", json={})
        self.assertEqual(denied.status_code, 401)
        self.assertEqual(login(self.client).status_code, 303)

        with patch("app.main.draft_outreach_messages") as draft_provider:
            response = self.client.post(
                "/api/simulations/one-business-demo",
                json={},
                headers={"X-CSRF-Token": session_csrf(self.client)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["demo"])
        self.assertFalse(response.json()["saved"])
        self.assertFalse(response.json()["sent"])
        self.assertEqual(response.json()["draft_mode"], "Local demo (no AI call)")
        draft_provider.assert_not_called()

    def test_campaign_pipeline_supports_the_full_sales_progression(self):
        with SessionLocal() as db:
            campaign = Campaign(title="Pipeline stages test", offer="Synthetic offer")
            prospect = Prospect(
                business_name="Pipeline Demo Business", source_url="https://example.invalid/listing",
                fingerprint="pipeline-stage-demo",
            )
            db.add_all([campaign, prospect])
            db.commit()
            db.add(CampaignProspect(campaign_id=campaign.id, prospect_id=prospect.id))
            db.commit()
            campaign_id, prospect_id = campaign.id, prospect.id

        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = self.client.patch(
            f"/api/campaigns/{campaign_id}/leads/{prospect_id}",
            json={
                "pipeline_stage": "meeting", "campaign_notes": "Asked for a proposal next week.",
                "follow_up_date": "2026-12-02", "deal_value": 2500,
            }, headers=headers,
        )
        self.assertEqual(response.status_code, 200, response.text)
        detail = self.client.get(f"/api/campaigns/{campaign_id}", headers=headers)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["leads"][0]["pipeline_stage"], "meeting")
        self.assertEqual(detail.json()["leads"][0]["campaign_notes"], "Asked for a proposal next week.")
        self.assertEqual(detail.json()["leads"][0]["follow_up_date"], "2026-12-02")
        self.assertEqual(detail.json()["leads"][0]["deal_value"], 2500)
        lost = self.client.patch(
            f"/api/campaigns/{campaign_id}/leads/{prospect_id}",
            json={"pipeline_stage": "lost", "lost_reason": "price"}, headers=headers,
        )
        self.assertEqual(lost.status_code, 200)
        self.assertEqual(
            self.client.get(f"/api/campaigns/{campaign_id}", headers=headers).json()["leads"][0]["lost_reason"],
            "price",
        )
        invalid = self.client.patch(
            f"/api/campaigns/{campaign_id}/leads/{prospect_id}",
            json={"pipeline_stage": "scheduled"}, headers=headers,
        )
        self.assertEqual(invalid.status_code, 422)

    def test_campaign_export_includes_pipeline_fields_and_neutralizes_formulas(self):
        with SessionLocal() as db:
            campaign = Campaign(title="Export safety test", offer="Synthetic offer")
            prospect = Prospect(
                business_name='=HYPERLINK("https://example.invalid")',
                source_url="https://example.invalid/listing", fingerprint="export-safety-demo",
            )
            db.add_all([campaign, prospect])
            db.commit()
            db.add(CampaignProspect(
                campaign_id=campaign.id, prospect_id=prospect.id, pipeline_stage="proposal",
                campaign_notes="=2+2", follow_up_date=date(2026, 12, 2), deal_value=2500,
            ))
            db.commit()
            campaign_id = campaign.id

        response = self.client.get(f"/api/campaigns/{campaign_id}/export.csv")
        self.assertEqual(response.status_code, 401)
        response = self.client.get(
            f"/api/campaigns/{campaign_id}/export.csv",
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(response.text.splitlines()))
        headers = rows[0]
        values = dict(zip(headers, rows[1]))
        self.assertEqual(values["Business"], "'=HYPERLINK(\"https://example.invalid\")")
        self.assertEqual(values["Pipeline stage"], "proposal")
        self.assertEqual(values["Follow-up date"], "2026-12-02")
        self.assertEqual(values["Deal value"], "2500")
        self.assertEqual(values["Campaign notes"], "'=2+2")

    def test_login_csrf_write_protection_and_logout(self):
        page = self.client.get("/login")
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
        bad = self.client.post("/login", data={"password": PASSWORD, "csrf_token": "wrong"})
        self.assertEqual(bad.status_code, 403)
        self.assertEqual(login(self.client).status_code, 303)
        self.assertEqual(self.client.get("/history").json(), [])
        with patch("app.main.analyse_business_message", return_value=FAKE_AI) as analyse:
            denied = self.client.post("/automate", json={"email": "test@example.invalid", "message": "test"})
            self.assertEqual(denied.status_code, 403)
            analyse.assert_not_called()
            made = self.client.post(
                "/automate",
                json={"email": "test@example.invalid", "message": "synthetic test lead"},
                headers={"X-CSRF-Token": session_csrf(self.client)},
            )
        self.assertEqual(made.status_code, 200)
        record_id = made.json()["id"]
        changed = self.client.put(
            f"/history/{record_id}/status?new_status=Contacted",
            headers={"X-CSRF-Token": session_csrf(self.client)},
        )
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(self.client.post(
            "/logout", headers={"X-CSRF-Token": session_csrf(self.client)}, follow_redirects=False
        ).status_code, 303)
        self.assertEqual(self.client.get("/history").status_code, 401)

    def test_bearer_token_for_reads_and_writes(self):
        headers = {"Authorization": f"Bearer {TOKEN}"}
        self.assertEqual(self.client.get("/history", headers=headers).status_code, 200)
        with patch("app.main.analyse_business_message", return_value=FAKE_AI):
            made = self.client.post("/automate", json={"message": "synthetic API test"}, headers=headers)
        self.assertEqual(made.status_code, 200)
        exported = self.client.get("/export", headers=headers)
        self.assertEqual(exported.status_code, 200)
        self.assertIn("synthetic API test", exported.text)
        invalid = self.client.get("/history", headers={"Authorization": "Bearer invalid"})
        self.assertEqual(invalid.status_code, 401)

    def test_docs_require_authentication_and_advertise_bearer(self):
        self.assertEqual(self.client.get("/openapi.json").status_code, 401)
        response = self.client.get("/openapi.json", headers={"Authorization": f"Bearer {TOKEN}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("BearerAuth", response.json()["components"]["securitySchemes"])

    def test_production_rejects_insecure_cookie_setting(self):
        from app.security import load_auth_config
        with patch.dict(os.environ, {"APP_ENV": "production", "APP_COOKIE_SECURE": "false"}):
            with self.assertRaises(RuntimeError):
                load_auth_config()


    def test_prospect_api_requires_auth_deduplicates_and_returns_saved_leads(self):
        payload = {
            "prospects": [{
                "clinic_name": "North Demo Dental",
                "website": "https://north-demo-dental.invalid",
                "town": "Leeds",
                "postcode": "LS1 1AA",
                "public_email": "hello@north-demo-dental.invalid",
                "phone": "+44 113 555 0100",
                "source_url": "https://north-demo-dental.invalid/about",
                "contact_source_url": "https://north-demo-dental.invalid/contact",
                "fit_score": 82,
                "fit_summary": "Synthetic test prospect; no real clinic data."
            }]
        }
        denied = self.client.post("/prospects/batch", json=payload)
        self.assertEqual(denied.status_code, 401)
        headers = {"Authorization": f"Bearer {TOKEN}"}
        created = self.client.post("/prospects/batch", json=payload, headers=headers)
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json()["created"], 1)
        repeated = self.client.post("/prospects/batch", json=payload, headers=headers)
        self.assertEqual(repeated.json()["created"], 0)
        self.assertEqual(repeated.json()["duplicates"], 1)
        saved = self.client.get("/prospects", headers=headers)
        self.assertEqual(len(saved.json()), 1)
        self.assertEqual(saved.json()[0]["clinic_name"], "North Demo Dental")
        self.assertEqual(saved.json()[0]["public_email"], "hello@north-demo-dental.invalid")
        invalid = self.client.post("/prospects/batch", json={"prospects": [{"clinic_name": "Missing source"}]}, headers=headers)
        self.assertEqual(invalid.status_code, 422)

    def test_campaign_discovery_uses_the_location_the_user_entered(self):
        with SessionLocal() as db:
            campaign = Campaign(
                title="Map search test", industry="Healthcare", business_type="Aesthetic clinic",
                region="northwest", country="United Kingdom", offer="Synthetic test only",
            )
            db.add(campaign)
            db.commit()
            campaign_id = campaign.id

        result = {
            "results": [], "location_label": "Birmingham, West Midlands, England, United Kingdom",
            "attribution": "© OpenStreetMap contributors", "license": "Open Database License (ODbL)",
        }
        with patch("app.main.discover_openstreetmap_businesses", return_value=result) as discover:
            response = self.client.post(
                f"/api/campaigns/{campaign_id}/discover",
                json={
                    "business_type": "Aesthetic clinic",
                    "location": "Birmingham, United Kingdom",
                    "radius_m": 5000,
                    "max_results": 20,
                },
                headers={"Authorization": f"Bearer {TOKEN}"},
            )

        self.assertEqual(response.status_code, 200)
        discover.assert_called_once_with("Aesthetic clinic", "Birmingham, United Kingdom", 5000, limit=20)

    def test_campaign_csv_preview_saves_nothing_and_import_deduplicates(self):
        with SessionLocal() as db:
            campaign = Campaign(
                title="CSV import test", industry="Healthcare", business_type="Dental clinic",
                country="United Kingdom", offer="Synthetic test only",
            )
            db.add(campaign)
            db.commit()
            campaign_id = campaign.id

        csv_content = (
            "company;website;public_email;city;source_url\n"
            "Sample Dental;https://sample-dental.invalid;hello@sample-dental.invalid;Leeds;https://directory.invalid/sample-dental\n"
            "Sample Dental;https://sample-dental.invalid;hello@sample-dental.invalid;Leeds;https://directory.invalid/sample-dental\n"
            "Missing source;;;Leeds;\n"
        ).encode("utf-8")
        files = {"file": ("businesses.csv", csv_content, "text/csv")}
        denied = self.client.post(f"/api/campaigns/{campaign_id}/import-csv/preview", files=files)
        self.assertEqual(denied.status_code, 401)

        headers = {"Authorization": f"Bearer {TOKEN}"}
        preview = self.client.post(
            f"/api/campaigns/{campaign_id}/import-csv/preview", files=files, headers=headers
        )
        self.assertEqual(preview.status_code, 200, preview.text)
        self.assertEqual(preview.json()["valid_rows"], 1)
        self.assertEqual(preview.json()["duplicate_rows"], 1)
        self.assertEqual(preview.json()["invalid_rows"], 1)
        self.assertEqual(preview.json()["will_add"], 1)
        self.assertFalse(preview.json()["saved"])
        with SessionLocal() as db:
            self.assertEqual(db.query(Prospect).count(), 0)
            self.assertEqual(db.query(CampaignProspect).count(), 0)

        imported = self.client.post(
            f"/api/campaigns/{campaign_id}/import-csv", files=files, headers=headers
        )
        self.assertEqual(imported.status_code, 200, imported.text)
        self.assertEqual(imported.json()["created_businesses"], 1)
        self.assertEqual(imported.json()["added_to_campaign"], 1)
        self.assertEqual(imported.json()["invalid_rows"], 1)
        self.assertEqual(imported.json()["duplicate_rows"], 1)
        self.assertEqual(imported.json()["campaign"]["leads"][0]["business_email"], "hello@sample-dental.invalid")

        repeated = self.client.post(
            f"/api/campaigns/{campaign_id}/import-csv", files=files, headers=headers
        )
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(repeated.json()["created_businesses"], 0)
        self.assertEqual(repeated.json()["added_to_campaign"], 0)
        self.assertEqual(repeated.json()["already_in_campaign"], 1)

    def test_openstreetmap_retries_a_busy_wide_search_at_one_kilometre(self):
        place = {
            "lat": 52.49, "lon": -1.85, "label": "Birmingham", "city": "Birmingham",
            "region": "West Midlands", "country": "United Kingdom", "country_code": "gb",
        }
        with patch("app.prospecting._geocode", return_value=place), patch(
            "app.prospecting._overpass_businesses",
            side_effect=[ProspectingError("busy", 503), []],
        ) as search:
            result = discover_openstreetmap_businesses(
                "Aesthetic clinic", "Birmingham fallback test", 5000, 40
            )

        self.assertEqual(result["radius_m"], 1000)
        self.assertIn("used a 1 km radius", result["notice"])
        self.assertEqual([call.args[1] for call in search.call_args_list], [5000, 1000])

    def test_one_business_simulation_is_authenticated_safe_and_does_not_write(self):
        with SessionLocal() as db:
            campaign = Campaign(
                title="UK dental website pilot", industry="Healthcare", business_type="Dental practice",
                region="West Midlands", country="United Kingdom", offer="Website and booking improvements for dental practices.",
            )
            prospect = Prospect(
                business_name="Demo Dental Practice", industry="Healthcare", business_type="Dentist",
                website="", city="Birmingham", region="West Midlands", country="England",
                business_email="public@example.invalid", business_phone="+44 121 555 0100",
                contact_name="Synthetic Contact", source_url="https://example.invalid/demo-listing",
                fingerprint="one-business-simulation-test",
            )
            db.add_all([campaign, prospect])
            db.commit()
            link = CampaignProspect(
                campaign_id=campaign.id, prospect_id=prospect.id,
                draft_subject="Existing draft", draft_body="Keep this draft unchanged.",
                draft_status="needs_review", pipeline_stage="new",
            )
            db.add(link)
            db.commit()
            campaign_id, prospect_id = campaign.id, prospect.id

        path = f"/api/campaigns/{campaign_id}/leads/{prospect_id}/simulate"
        self.assertEqual(self.client.post(path, json={}).status_code, 401)
        login(self.client)
        with patch("app.main.draft_outreach_messages", return_value=[{
            "business_id": prospect_id,
            "subject": "A question about online bookings",
            "body": "A synthetic review-only message.",
            "reason": "Mock provider response for an isolated test.",
        }]) as draft_call:
            response = self.client.post(path, json={}, headers={"X-CSRF-Token": session_csrf(self.client)})

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["business"]["name"], "Demo Dental Practice")
        self.assertEqual(result["draft"]["body"], "A synthetic review-only message.")
        self.assertFalse(result["saved"])
        self.assertFalse(result["sent"])
        self.assertTrue(result["timeline"])
        sent_to_provider = draft_call.call_args.args[1][0]
        self.assertNotIn("business_email", sent_to_provider)
        self.assertNotIn("business_phone", sent_to_provider)
        self.assertNotIn("contact_name", sent_to_provider)
        with SessionLocal() as db:
            unchanged = db.query(CampaignProspect).filter_by(
                campaign_id=campaign_id, prospect_id=prospect_id
            ).one()
            self.assertEqual(unchanged.draft_body, "Keep this draft unchanged.")
            self.assertEqual(unchanged.draft_status, "needs_review")

    def test_business_skill_documents_tool_costs_and_safe_api_use(self):
        root = Path(__file__).resolve().parents[1] / "skills" / "business-prospect-finder"
        skill = (root / "SKILL.md").read_text(encoding="utf-8")
        api = (root / "references" / "api-integration.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: Business Prospect Finder\n"))
        self.assertIn("quote_tool", skill)
        self.assertIn("approved the exact quote and amount", skill)
        self.assertIn("POST to `/businesses/batch`", api)
        self.assertIn("Authorization: Bearer", api)

    def test_sensitive_html_is_not_cached_and_has_csrf(self):
        login(self.client)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertIn('name="csrf-token"', response.text)
        self.assertIn("function escapeHtml", response.text)
        self.assertIn('id="logoutButton"', response.text)
        self.assertEqual(response.headers["x-frame-options"], "DENY")


if __name__ == "__main__":
    unittest.main()





