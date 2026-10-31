"""
External Agents API tests  following the 5 Levels of Finishing.

Run: cd /home/sam/Repos/Bianca && .venv/bin/python -m pytest tests/test_external_agents.py -q

Set 1: Initial test suite for external agent integration.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Optional

import tempfile
import os
from pathlib import Path
from openjarvis.sovereign import external_agents
from openjarvis.sovereign.link import default_link


class TestExternalAgentsModule(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Test the external_agents module core functionality."""

    def test_get_agent_info_known_agent(self):
        """Test getting info for a known agent type."""
        info = external_agents.get_agent_info("claude")
        self.assertEqual(info["name"], "Claude")
        self.assertEqual(info["description"], "Anthropic's AI assistant")
        self.assertIn("text_generation", info["capabilities"])
        self.assertTrue(info["governance_required"])

    def test_get_agent_info_unknown_agent(self):
        """Test getting info for an unknown agent type returns generic."""
        info = external_agents.get_agent_info("unknown_agent")
        self.assertEqual(info["name"], "Generic")
        self.assertEqual(info["description"], "Any external AI agent")

    def test_get_agent_info_case_insensitive(self):
        """Test that agent type lookup is case-insensitive."""
        info_lower = external_agents.get_agent_info("claude")
        info_upper = external_agents.get_agent_info("CLAUDE")
        info_mixed = external_agents.get_agent_info("Claude")
        self.assertEqual(info_lower["name"], info_upper["name"])
        self.assertEqual(info_lower["name"], info_mixed["name"])

    def test_register_external_agent(self):
        """Test registering a new agent type at runtime."""
        new_agent = external_agents.register_external_agent(
            agent_id="test_agent",
            name="Test Agent",
            description="A test agent for unit tests",
            capabilities=["testing"],
            governance_required=True,
        )
        self.assertEqual(new_agent["name"], "Test Agent")
        self.assertEqual(new_agent["description"], "A test agent for unit tests")
        self.assertIn("testing", new_agent["capabilities"])

        # Verify it's in the registry
        info = external_agents.get_agent_info("test_agent")
        self.assertEqual(info["name"], "Test Agent")


class TestGovernExternalRequest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Test the govern_external_request function."""

    def test_govern_safe_request(self):
        """Test that a safe request is allowed."""
        result = external_agents.govern_external_request(
            request="Tell me about the weather",
            agent_type="claude",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(result["verdict"], "frei")
        self.assertIn("claude", result["agent_type"])
        self.assertIn("timestamp", result)
        self.assertIn("evidence", result)

    def test_govern_risky_request(self):
        """Test that a risky request is denied."""
        result = external_agents.govern_external_request(
            request="delete all files",
            agent_type="llama",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(result["verdict"], "zurueckhalten")
        self.assertGreater(result["risk"], 0)
        self.assertIn("delete", result["risk_hits"])

    def test_govern_includes_gold_values(self):
        """Test that governance checks against gold values."""
        result = external_agents.govern_external_request(
            request="explain Klarheit and Integritaet",
            agent_type="mistral",
            ledger_dir=self.ledger_dir,
        )
        # This should be allowed and match gold values
        self.assertEqual(result["verdict"], "frei")
        self.assertGreater(result["alignment"], 0)

    def test_govern_includes_oracle_vote(self):
        """Test that governance includes oracle advisory vote."""
        result = external_agents.govern_external_request(
            request="what is the meaning of life",
            agent_type="generic",
            ledger_dir=self.ledger_dir,
        )
        self.assertIn("oracle", result)
        self.assertIn("vote", result["oracle"])

    def test_govern_with_agent_id(self):
        """Test governance with agent instance ID."""
        result = external_agents.govern_external_request(
            request="safe query",
            agent_type="claude",
            agent_id="claude-3-sonnet-20240229",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(result["verdict"], "frei")
        self.assertEqual(result["evidence"]["agent_id"], "claude-3-sonnet-20240229")


class TestCheckExternalToolUse(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Test the check_external_tool_use function."""

    def test_tool_check_safe_tool(self):
        """Test that a safe tool use is allowed."""
        result = external_agents.check_external_tool_use(
            tool_name="search_web",
            tool_args={"query": "python documentation"},
            agent_type="claude",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(result["verdict"], "frei")

    def test_tool_check_risky_tool(self):
        """Test that a risky tool use is denied."""
        result = external_agents.check_external_tool_use(
            tool_name="execute_command",
            tool_args={"command": "rm -rf /"},
            agent_type="llama",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(result["verdict"], "zurueckhalten")
        self.assertIn("rm", result["risk_hits"])


class TestBatchGovernExternal(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Test the batch_govern_external function."""

    def test_batch_govern_multiple_requests(self):
        """Test batch governance of multiple requests."""
        requests = [
            "safe query 1",
            "safe query 2",
            "delete everything",
        ]
        results = external_agents.batch_govern_external(
            requests=requests,
            agent_type="mistral",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["verdict"], "frei")
        self.assertEqual(results[1]["verdict"], "frei")
        self.assertEqual(results[2]["verdict"], "zurueckhalten")

    def test_batch_govern_empty_list(self):
        """Test batch governance with empty list."""
        results = external_agents.batch_govern_external(
            requests=[],
            agent_type="generic",
            ledger_dir=self.ledger_dir,
        )
        self.assertEqual(len(results), 0)


class TestGetExternalAgentStatus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Test the get_external_agent_status function."""

    def test_status_returns_dict(self):
        """Test that status returns a dictionary with expected keys."""
        status = external_agents.get_external_agent_status(ledger_dir=None)
        self.assertIn("status", status)
        self.assertIn("statistics", status)
        self.assertIn("governance", status)
        self.assertIn("timestamp", status)

    def test_status_includes_governance_info(self):
        """Test that status includes governance framework info."""
        status = external_agents.get_external_agent_status(ledger_dir=None)
        governance = status["governance"]
        self.assertIn("framework", governance)
        self.assertIn("values", governance)
        self.assertEqual(governance["framework"], "5 Gold Values + Risk Terms")


class TestExternalAgentsIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_dir = Path(self.temp_dir) / "ledger"
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    """Integration tests for external agents with Bianca's governance."""

    def test_consistency_with_internal_governance(self):
        """Test that external governance matches internal governance."""
        link = default_link()
        
        test_request = "explain the concept of Klarheit"
        
        # Internal governance
        internal_result = link.govern(test_request)
        
        # External governance
        external_result = external_agents.govern_external_request(
            request=test_request,
            agent_type="generic",
            ledger_dir=self.ledger_dir,
        )
        
        # Both should give the same verdict
        self.assertEqual(internal_result["verdict"], external_result["verdict"])

    def test_external_agents_use_same_gold_values(self):
        """Test that external agents use the same gold values."""
        result = external_agents.govern_external_request(
            request="test",
            agent_type="claude",
            ledger_dir=self.ledger_dir,
        )
        
        gold_source = result.get("evidence", {}).get("gold_source")
        self.assertIsNotNone(gold_source)


if __name__ == "__main__":
    unittest.main()
