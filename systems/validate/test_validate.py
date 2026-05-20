#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path


def load_validate_module():
    validate_path = Path(__file__).with_name("validate")
    loader = importlib.machinery.SourceFileLoader("validate_under_test", str(validate_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


validate = load_validate_module()


class ResearchSquadDispatchPolicyTests(unittest.TestCase):
    def test_rejects_triggering_roster_banned_timeline_fields_and_worker_agent_list(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            protocol = root / "squads" / "research-squad" / "protocol.md"
            worker = root / "agents" / "research-agent" / "instructions.md"
            protocol.parent.mkdir(parents=True)
            worker.parent.mkdir(parents=True)
            protocol.write_text(
                """
### Agent Roster
- Orchestrator: [@Orchestrator](mention://agent/{orchestrator-id})
- Deep Research Agent: [@Deep Research Agent](mention://agent/{research-id})

## Dispatch: review
**Target agent**: [@Research Review Agent](mention://agent/{review-id})
**Next action**: [@Research Review Agent](mention://agent/{review-id}) review

event_seq: 7
parent_event: abc
daemon-style watchdog
""",
                encoding="utf-8",
            )
            worker.write_text(
                "Worker should run `multica agent list --output json` before handoff.",
                encoding="utf-8",
            )

            errors = validate.validate_research_squad_dispatch_policy(root)

        self.assertTrue(any("agent roster" in err for err in errors), errors)
        self.assertTrue(any("multiple trigger mentions" in err for err in errors), errors)
        self.assertTrue(any("event_seq" in err for err in errors), errors)
        self.assertTrue(any("parent_event" in err for err in errors), errors)
        self.assertTrue(any("watchdog" in err for err in errors), errors)
        self.assertTrue(any("worker must not call multica agent list" in err for err in errors), errors)
        self.assertTrue(any("missing silent non-target guard" in err for err in errors), errors)

    def test_rejects_project_planner_roster_language_and_missing_non_target_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            planner = root / "agents" / "project-planner-agent" / "instructions.md"
            planner.parent.mkdir(parents=True)
            planner.write_text(
                """
# Project Planner Agent

Before posting Planner Complete, verify the comment body contains exactly one `mention://agent/`.
If `multica agent list` fails, post `BLOCKED: cannot resolve agent roster`.
""",
                encoding="utf-8",
            )

            errors = validate.validate_research_squad_dispatch_policy(root)

        self.assertTrue(any("agent roster" in err for err in errors), errors)
        self.assertTrue(any("worker must not call multica agent list" in err for err in errors), errors)

    def test_accepts_non_triggering_directory_single_target_and_created_at_timeline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            protocol = root / "squads" / "research-squad" / "protocol.md"
            worker = root / "agents" / "research-agent" / "instructions.md"
            protocol.parent.mkdir(parents=True)
            worker.parent.mkdir(parents=True)
            protocol.write_text(
                """
### Agent Directory
Non-triggering UUID directory.

## Dispatch: review
**Target agent**: [@Research Review Agent](mention://agent/{review-id})
**Next action**: Research Review Agent reviews the artifact.

**Agent Directory**:
- Orchestrator: `{orchestrator-id}`
- Deep Research Agent: `{research-id}`
- Research Review Agent: `{review-id}`
- Technical Writer Agent: `{tw-id}`

Non-target guard: if target agent is not this agent, do not post a Multica issue comment; use runtime output or cancel/no-op.
Timeline: sort `multica issue runs` by `created_at` ascending, then phase and round.
Orchestrator Continuous-Action: same run must post a dispatch, terminal state, or pending actions.
""",
                encoding="utf-8",
            )
            worker.write_text(
                """
Build exactly one target mention from the Agent Directory UUID.
Never call the agent-list CLI from a worker.
If this agent is not the target, do not post a Multica issue comment.
If runtime requires an issue-visible result, use cancel/no-op.
""",
                encoding="utf-8",
            )

            errors = validate.validate_research_squad_dispatch_policy(root)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
