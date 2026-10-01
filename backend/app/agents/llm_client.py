"""
ResolveAI LLM Client Alias
Forwards to unified LLMProvider supporting OmniRoute, Anthropic, OpenAI, and deterministic fallbacks.
"""

from .llm_provider import llm_provider, LLMProvider

# Re-export for backward compatibility
llm_client = llm_provider
__all__ = ["llm_client", "llm_provider", "LLMProvider"]
