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
from app.database import Automation, SessionLocal
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


