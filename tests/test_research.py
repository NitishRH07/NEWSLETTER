"""
Tests for research and verification logic.
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from backend.research.verifier import ToolVerifier

@pytest.mark.asyncio
async def test_verifier_website():
    verifier = ToolVerifier()
    # Test verified check on a known public site
    is_live = await verifier.verify_website("https://example.com")
    assert is_live is True

@pytest.mark.asyncio
async def test_verifier_invalid_website():
    verifier = ToolVerifier()
    # Test non-existent domain
    is_live = await verifier.verify_website("https://thisdomaindoesnotexist123456789xyz.org")
    assert is_live is False
