"""
Tests for main application
"""

from unittest.mock import MagicMock, patch

import pytest

# Import PROFILE_PROMPTS directly from app module
# This should work because conftest.py mocks chainlit before import
from app import PROFILE_PROMPTS


class TestChatProfiles:
    """Test chat profile configuration"""

    def test_profile_prompts_exist(self):
        """Test that all profile prompts are defined"""
        assert "the-architect" in PROFILE_PROMPTS
        assert "the-executive" in PROFILE_PROMPTS
        assert "the-skeptic" in PROFILE_PROMPTS

    def test_profile_prompts_not_empty(self):
        """Test that profile prompts contain content"""
        for profile_name, prompt in PROFILE_PROMPTS.items():
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "You are" in prompt or profile_name.lower() in prompt.lower()

    def test_architect_prompt_technical(self):
        """Test that Architect prompt focuses on technical details"""
        prompt = PROFILE_PROMPTS["the-architect"]
        assert "technical" in prompt.lower()
        assert "code" in prompt.lower() or "implementation" in prompt.lower()

    def test_executive_prompt_brief(self):
        """Test that Executive prompt emphasizes brevity"""
        prompt = PROFILE_PROMPTS["the-executive"]
        assert "brief" in prompt.lower() or "concise" in prompt.lower()
        assert "high-level" in prompt.lower()

    def test_skeptic_prompt_critical(self):
        """Test that Skeptic prompt emphasizes critical thinking"""
        prompt = PROFILE_PROMPTS["the-skeptic"]
        assert "critical" in prompt.lower() or "question" in prompt.lower()
        assert "evidence" in prompt.lower() or "proof" in prompt.lower()
