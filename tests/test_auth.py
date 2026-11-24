import os
import re
import unittest
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
                json={"business_type": "Aesthetic clinic", "location": "Birmingham, United Kingdom", "radius_m": 5000},
                headers={"Authorization": f"Bearer {TOKEN}"},
            )

        self.assertEqual(response.status_code, 200)
        discover.assert_called_once_with("Aesthetic clinic", "Birmingham, United Kingdom", 5000, limit=40)

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





