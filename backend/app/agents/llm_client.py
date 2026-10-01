"""
ResolveAI LLM Reasoning Client
Connects to Anthropic Claude (or OpenAI fallback) for generative root-cause analysis and diagnosis.
Safely falls back to deterministic rule-based analysis if API key is missing or offline.
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Optional
from ..models.schemas import Diagnosis, Evidence

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

class LLMReasoningClient:
    """
    LLM Client for incident diagnosis and reasoning.
    Strictly isolated: LLM outputs reasoning/diagnosis only.
    All execution, tool calls, and risk gating remain strictly governed by the orchestrator.
    """

    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.enable_mock = os.getenv("ENABLE_MOCK_LLM", "false").lower() in ["true", "1", "yes"]

    def is_configured(self) -> bool:
        """Check if a valid real LLM API key is present and mock mode is off."""
        if self.enable_mock:
            return False
        return bool(self.anthropic_key and not self.anthropic_key.startswith("your_"))

    def analyze_incident(self, description: str, category: str, evidence: List[Evidence]) -> Optional[Diagnosis]:
        """
        Call LLM provider to synthesize root-cause diagnosis.
        Returns Diagnosis if successful, None if fallback should be used.
        """
        if not self.is_configured():
            return None

        prompt = self._build_prompt(description, category, evidence)

        if self.anthropic_key and not self.anthropic_key.startswith("your_"):
            return self._call_anthropic(prompt, evidence)
        elif self.openai_key and not self.openai_key.startswith("your_"):
            return self._call_openai(prompt, evidence)

        return None

    def _build_prompt(self, description: str, category: str, evidence: List[Evidence]) -> str:
        evidence_text = "\n".join([
            f"- [{e.type.upper()}] {e.title}: {e.content} (Relevance: {e.relevance}%)"
            for e in evidence
        ]) or "No direct evidence retrieved."

        return f"""You are ResolveAI's Senior Incident Diagnosis AI. Analyze the IT incident based ONLY on the verified evidence gathered below.

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

    def _call_anthropic(self, prompt: str, evidence: List[Evidence]) -> Optional[Diagnosis]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": self.model,
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            req = urllib.request.Request(
                ANTHROPIC_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["content"][0]["text"].strip()
                # Clean up json if model wrapped in markdown
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                parsed = json.loads(text.strip())
                return Diagnosis(
                    likelyCause=parsed.get("likelyCause", "LLM Diagnosis generated."),
                    confidence=int(parsed.get("confidence", 85)),
                    supportingEvidence=evidence,
                    uncertainty=parsed.get("uncertainty")
                )
        except Exception as e:
            # Safe fallback if API error or timeout
            return None

    def _call_openai(self, prompt: str, evidence: List[Evidence]) -> Optional[Diagnosis]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(
                OPENAI_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"].strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                parsed = json.loads(text.strip())
                return Diagnosis(
                    likelyCause=parsed.get("likelyCause", "LLM Diagnosis generated."),
                    confidence=int(parsed.get("confidence", 85)),
                    supportingEvidence=evidence,
                    uncertainty=parsed.get("uncertainty")
                )
        except Exception as e:
            return None

llm_client = LLMReasoningClient()
