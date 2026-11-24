import json
import os
import unittest
from unittest.mock import MagicMock, patch

from app.ai_service import AIProviderError, analyse_business_message


class AIServiceTests(unittest.TestCase):
    def test_uses_local_classifier_when_key_is_missing(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            result = analyse_business_message("Please send pricing information.")

        self.assertEqual(result["category"], "sales")
        self.assertEqual(result["lead_score"], 60)

    def test_calls_configured_provider_and_validates_result(self):
        provider_result = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "category": "sales",
                        "priority": "medium",
                        "lead_score": 74,
                        "reply": "Thanks for your enquiry. When would you like to speak?",
                    })
                }
            }]
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(provider_result).encode("utf-8")

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-secret",
            "OPENAI_MODEL": "test-model",
            "OPENAI_BASE_URL": "",
        }, clear=False), patch("app.ai_service.urlopen", return_value=response) as mocked_urlopen:
            result = analyse_business_message("Please send pricing information.")

        self.assertEqual(result["lead_score"], 74)
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        sent_payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(sent_payload["model"], "test-model")
        self.assertEqual(sent_payload["messages"][1]["content"], "Please send pricing information.")

    def test_rejects_invalid_provider_results_without_local_fallback(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "choices": [{"message": {"content": "not json"}}]
        }).encode("utf-8")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-secret"}, clear=False), patch(
            "app.ai_service.urlopen", return_value=response
        ):
            with self.assertRaises(AIProviderError):
                analyse_business_message("Please send pricing information.")

    def test_rejects_non_https_provider_url(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-secret",
            "OPENAI_BASE_URL": "http://example.com/v1",
        }, clear=False):
            with self.assertRaises(AIProviderError):
                analyse_business_message("A sample request.")


if __name__ == "__main__":
    unittest.main()
