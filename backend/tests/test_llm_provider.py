"""
Unit & Integration tests for LLMProvider and OmniRoute integration.
"""

import os
import pytest
from backend.app.agents.llm_provider import LLMProvider
from backend.app.agents.diagnosis import diagnosis_agent
from backend.app.models.schemas import Evidence

class TestLLMProvider:
    """Test suite for LLM provider abstraction and OmniRoute integration."""

    def test_01_provider_defaults_and_env_loading(self):
        provider = LLMProvider()
        assert provider.omniroute_base_url == "http://localhost:20128/v1"
        assert provider.omniroute_model != ""

    def test_02_omniroute_active_when_key_provided(self, monkeypatch):
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-omniroute-key-12345")
        monkeypatch.setenv("ENABLE_MOCK_LLM", "false")
        provider = LLMProvider()
        assert provider.get_active_provider_name() == "omniroute"
        assert provider.is_configured() is True

    def test_03_mock_fallback_when_no_key(self, monkeypatch):
        monkeypatch.setenv("OMNIROUTE_API_KEY", "PASTE_MY_OMNIROUTE_KEY_HERE")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
        monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
        monkeypatch.setenv("ENABLE_MOCK_LLM", "false")
        provider = LLMProvider()
        assert provider.get_active_provider_name() == "mock"
        assert provider.is_configured() is False

    def test_04_omniroute_connection_unavailable_graceful_fallback(self, monkeypatch):
        # Point to a closed port to simulate server offline
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        monkeypatch.setenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:59999/v1")
        monkeypatch.setenv("ENABLE_MOCK_LLM", "false")
        provider = LLMProvider()

        evidence = [Evidence(id="ev1", type="system_status", title="VPN Auth", content="Session expired", relevance=95)]
        # Should gracefully return None without throwing an unhandled exception
        result = provider.analyze_incident("VPN disconnected", "Network", evidence)
        assert result is None

    def test_05_diagnosis_agent_uses_fallback_seamlessly(self, monkeypatch):
        # When OmniRoute is unreachable, diagnosis agent must still produce valid Diagnosis
        monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
        monkeypatch.setenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:59999/v1")
        monkeypatch.setenv("ENABLE_MOCK_LLM", "false")

        evidence = [Evidence(id="ev1", type="knowledge_base", title="VPN Resolution", content="Reset session", relevance=95)]
        diag = diagnosis_agent.run("VPN disconnected", "Network", evidence)
        assert diag is not None
        assert "VPN" in diag.likelyCause or "stale session" in diag.likelyCause
        assert diag.confidence >= 80

    def test_06_check_health_diagnostics(self):
        provider = LLMProvider()
        health = provider.check_health()
        assert "active_provider" in health
        assert "configured" in health
