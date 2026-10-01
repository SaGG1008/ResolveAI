"""
ResolveAI Multi-Provider LLM Abstraction Layer
Supports:
1. OmniRoute (Local OpenAI-compatible API at OMNIROUTE_BASE_URL, default: http://localhost:20128/v1)
2. Anthropic Claude (ANTHROPIC_API_KEY)
3. OpenAI (OPENAI_API_KEY)
4. Deterministic Mock / Fallback Mode (offline resilience)

All requests are strictly executed server-side.
The LLM has zero execution authority; all proposed actions pass through
the allowlisted ToolRegistry, RiskPolicy, and Human Approval Gate.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any

# Ensure environment files are loaded
from ..core import env_loader  # noqa: F401
from ..models.schemas import Diagnosis, Evidence

logger = logging.getLogger("ResolveAI.LLMProvider")

class LLMProvider:
    """
    Unified LLM Provider interface for ResolveAI agents.
    Agents interact exclusively through LLMProvider methods (e.g. generate, analyze_incident).
    """

    def __init__(self):
        self.reload_config()

    def reload_config(self):
        """Reload configuration from environment variables."""
        self.provider_override = os.getenv("LLM_PROVIDER", "").lower().strip()
        self.enable_mock = os.getenv("ENABLE_MOCK_LLM", "false").lower() in ["true", "1", "yes"]

        # OmniRoute Configuration
        self.omniroute_key = os.getenv("OMNIROUTE_API_KEY", "").strip()
        self.omniroute_base_url = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1").rstrip("/")
        self.omniroute_model = os.getenv("OMNIROUTE_MODEL", "gpt-4o").strip()

        # Anthropic Configuration
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()

        # OpenAI Configuration
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o").strip()

    def get_active_provider_name(self) -> str:
        """Determine which provider is active based on environment variables."""
        self.reload_config()
        if self.enable_mock:
            return "mock"

        has_omniroute_key = bool(self.omniroute_key and not self.omniroute_key.startswith("PASTE_MY_") and not self.omniroute_key.startswith("your_"))
        has_anthropic_key = bool(self.anthropic_key and not self.anthropic_key.startswith("your_"))
        has_openai_key = bool(self.openai_key and not self.openai_key.startswith("your_"))

        if self.provider_override == "omniroute" and has_omniroute_key:
            return "omniroute"
        elif self.provider_override == "anthropic" and has_anthropic_key:
            return "anthropic"
        elif self.provider_override == "openai" and has_openai_key:
            return "openai"
        elif self.provider_override in ["mock", "deterministic"]:
            return "mock"

        # Auto-detect if override is not explicitly active
        if has_omniroute_key:
            return "omniroute"
        if has_anthropic_key:
            return "anthropic"
        if has_openai_key:
            return "openai"

        return "mock"

    def is_configured(self) -> bool:
        """Check if any real LLM provider is configured and reachable."""
        provider = self.get_active_provider_name()
        return provider in ["omniroute", "anthropic", "openai"]

    def check_health(self) -> Dict[str, Any]:
        """Check provider reachability and return diagnostics."""
        provider = self.get_active_provider_name()
        info = {
            "active_provider": provider,
            "configured": self.is_configured(),
            "mock_mode": self.enable_mock
        }

        if provider == "omniroute":
            info["base_url"] = self.omniroute_base_url
            info["model"] = self.omniroute_model
            # Test ping to base URL / models endpoint
            try:
                test_url = f"{self.omniroute_base_url}/models"
                req = urllib.request.Request(
                    test_url,
                    headers={"Authorization": f"Bearer {self.omniroute_key}"},
                    method="GET"
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    info["reachable"] = (resp.status == 200)
            except Exception as e:
                info["reachable"] = False
                info["error"] = str(e)
        return info

    def generate(self, prompt: str, system_prompt: Optional[str] = None, timeout: int = 10) -> Optional[str]:
        """
        Generic text generation endpoint across providers.
        Returns generated text or None if error/fallback.
        """
        self.reload_config()
        provider = self.get_active_provider_name()

        if provider == "omniroute":
            return self._call_omniroute(prompt, system_prompt, timeout)
        elif provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt, timeout)
        elif provider == "openai":
            return self._call_openai(prompt, system_prompt, timeout)
        else:
            return None

    def analyze_incident(self, description: str, category: str, evidence: List[Evidence]) -> Optional[Diagnosis]:
        """
        Synthesize incident root-cause diagnosis using active LLM provider.
        Returns typed Diagnosis or None on error/mock fallback.
        """
        if not self.is_configured():
            return None

        prompt = self._build_diagnosis_prompt(description, category, evidence)
        system_prompt = "You are ResolveAI's Senior Incident Diagnosis AI. Return STRICT raw JSON only."

        raw_response = self.generate(prompt, system_prompt, timeout=8)
        if not raw_response:
            return None

        try:
            cleaned = self._clean_json_text(raw_response)
            parsed = json.loads(cleaned)
            return Diagnosis(
                likelyCause=parsed.get("likelyCause", "LLM Diagnosis generated."),
                confidence=int(parsed.get("confidence", 85)),
                supportingEvidence=evidence,
                uncertainty=parsed.get("uncertainty")
            )
        except Exception as e:
            logger.warning(f"Failed to parse LLM diagnosis JSON response: {e}")
            return None

    def _build_diagnosis_prompt(self, description: str, category: str, evidence: List[Evidence]) -> str:
        evidence_text = "\n".join([
            f"- [{e.type.upper()}] {e.title}: {e.content} (Relevance: {e.relevance}%)"
            for e in evidence
        ]) or "No direct evidence retrieved."

        return f"""Analyze the IT incident based ONLY on the verified evidence gathered below:

Incident Category: {category}
Incident Description: {description}

Gathered Evidence:
{evidence_text}

Respond in STRICT JSON format with these exact keys:
{{
  "likelyCause": "<concise explanation of root cause>",
  "confidence": <integer percentage 10 to 99>,
  "uncertainty": "<any risk or uncertainty, or null if certain>"
}}
Do NOT output markdown code fences or conversational text. Output raw JSON only."""

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown code wrappers from json text."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    # =========================================================================
    # Provider Implementations
    # =========================================================================

    def _call_omniroute(self, prompt: str, system_prompt: Optional[str], timeout: int) -> Optional[str]:
        """Call OmniRoute through its OpenAI-compatible /chat/completions interface."""
        url = f"{self.omniroute_base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.omniroute_key}"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.omniroute_model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            logger.warning(f"OmniRoute HTTP error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"OmniRoute connection unavailable at {url}: {e.reason}")
            return None
        except Exception as e:
            logger.warning(f"OmniRoute request failed: {e}")
            return None

    def _call_anthropic(self, prompt: str, system_prompt: Optional[str], timeout: int) -> Optional[str]:
        """Call Anthropic Claude API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": self.anthropic_model,
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"].strip()
        except Exception as e:
            logger.warning(f"Anthropic API request failed: {e}")
            return None

    def _call_openai(self, prompt: str, system_prompt: Optional[str], timeout: int) -> Optional[str]:
        """Call OpenAI Chat Completions API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI API request failed: {e}")
            return None

# Singleton instance
llm_provider = LLMProvider()
