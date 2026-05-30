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


class DevSquadDispatchPolicyTests(unittest.TestCase):
    def test_rejects_worker_handoffs_without_orchestrator_mentions_and_legacy_reviewer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            protocol = root / "squads" / "dev-squad" / "protocol.md"
            engineer = root / "agents" / "dev-engineer-agent" / "instructions.md"
            reviewer = root / "agents" / "dev-cc-reviewer-agent" / "instructions.md"
            orchestrator = root / "agents" / "dev-orchestrator-agent" / "instructions.md"
            squad_yaml = root / "squads" / "dev-squad" / "squad.yaml"
            protocol.parent.mkdir(parents=True)
            engineer.parent.mkdir(parents=True)
            reviewer.parent.mkdir(parents=True)
            orchestrator.parent.mkdir(parents=True)
            squad_yaml.write_text(
                """
name: dev-squad
members:
  orchestrator: agents/dev-orchestrator-agent
  engineer: agents/dev-engineer-agent
  reviewer: agents/dev-reviewer-agent
protocol: squads/dev-squad/protocol.md
""",
                encoding="utf-8",
            )
            protocol.write_text(
                """
Multica, not Linear.
Continuous Handoff requires exactly one trigger mention.
Use `multica issue runs` during resume.
Dev CC Reviewer is the reviewer.
Non-target agents do not post a Multica issue comment; use cancel/no-op if needed.

```markdown
## Dispatch: Review
**Target agent**: [@dev-reviewer-agent](mention://agent/{reviewer-id})
**Next action**: dev-reviewer-agent reviews the PR.

**Agent Directory**:
- dev-orchestrator: `{orchestrator-id}`
- dev-engineer: `{engineer-id}`

## Implementation Ready
**PR**: {pr_url}
**Next action**: Orchestrator dispatches code review

## Review Verdict
**Recommendation**: approve
**Next action**: Orchestrator merges PR
```
""",
                encoding="utf-8",
            )
            engineer.write_text("Post Implementation Ready when done.", encoding="utf-8")
            reviewer.write_text("Post Review Verdict when done.", encoding="utf-8")
            orchestrator.write_text("You may dispatch dev-engineer-agent and dev-reviewer-agent.", encoding="utf-8")

            errors = validate.validate_dev_squad_dispatch_policy(root)

        self.assertTrue(any("dev-cc-reviewer-agent" in err for err in errors), errors)
        self.assertTrue(any("Implementation Ready" in err and "Target agent" in err for err in errors), errors)
        self.assertTrue(any("Review Verdict" in err and "Target agent" in err for err in errors), errors)
        self.assertTrue(any("Agent Directory" in err and "Dev CC Reviewer" in err for err in errors), errors)
        self.assertTrue(any("legacy dev-reviewer-agent" in err for err in errors), errors)

    def test_accepts_dev_squad_continuous_handoff_protocol(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            protocol = root / "squads" / "dev-squad" / "protocol.md"
            engineer = root / "agents" / "dev-engineer-agent" / "instructions.md"
            reviewer = root / "agents" / "dev-cc-reviewer-agent" / "instructions.md"
            orchestrator = root / "agents" / "dev-orchestrator-agent" / "instructions.md"
            dev_skill = root / "agents" / "dev-orchestrator-agent" / "skills" / "dev-coordination" / "SKILL.md"
            dev_protocol_copy = (
                root
                / "agents"
                / "dev-orchestrator-agent"
                / "skills"
                / "dev-coordination"
                / "references"
                / "squad-communication-protocol.md"
            )
            squad_yaml = root / "squads" / "dev-squad" / "squad.yaml"
            protocol.parent.mkdir(parents=True)
            engineer.parent.mkdir(parents=True)
            reviewer.parent.mkdir(parents=True)
            orchestrator.parent.mkdir(parents=True)
            dev_protocol_copy.parent.mkdir(parents=True)
            squad_yaml.write_text(
                """
name: dev-squad
members:
  orchestrator: agents/dev-orchestrator-agent
  engineer: agents/dev-engineer-agent
  reviewer: agents/dev-cc-reviewer-agent
protocol: squads/dev-squad/protocol.md
""",
                encoding="utf-8",
            )
            protocol.write_text(
                """
Multica, not Linear.

## Continuous Handoff
Continuous tasks must include exactly one target agent mention link in `Target agent`.
Worker handoffs to Orchestrator must mention Dev Orchestrator.
Use `multica issue runs` and comments to resume from the latest actionable state.
Non-target agents do not post a Multica issue comment and use cancel/no-op if the runtime requires a terminal action.

## Dispatch: Review
**Target agent**: [@Dev CC Reviewer](mention://agent/{reviewer-id})
**Next action**: Dev CC Reviewer reviews the PR.

**Agent Directory**:
- Dev Orchestrator: `{orchestrator-id}`
- Dev Engineer: `{engineer-id}`
- Dev CC Reviewer: `{reviewer-id}`

## Implementation Ready
**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator dispatches code review

## Review Verdict
**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator merges PR or dispatches revision

## Revision Complete
**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator dispatches re-review
""",
                encoding="utf-8",
            )
            dev_protocol_copy.write_text(protocol.read_text(), encoding="utf-8")
            dev_skill.write_text(
                """
# Dev Coordination

Read `references/squad-communication-protocol.md` for the full protocol.
""",
                encoding="utf-8",
            )
            engineer.write_text(
                """
Build handoff mentions from the Agent Directory.
Implementation Ready and Revision Complete must contain `Target agent: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})`.
Before posting, verify exactly one trigger mention is present.
If this agent is not the target, do not post a Multica issue comment; use cancel/no-op if needed.
""",
                encoding="utf-8",
            )
            reviewer.write_text(
                """
Build handoff mentions from the Agent Directory.
Review Verdict must contain `Target agent: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})`.
Before posting, verify exactly one trigger mention is present.
If this agent is not the target, do not post a Multica issue comment; use cancel/no-op if needed.
""",
                encoding="utf-8",
            )
            orchestrator.write_text(
                "You may dispatch dev-engineer-agent and dev-cc-reviewer-agent. Resume by reading comments and `multica issue runs`.",
                encoding="utf-8",
            )

            errors = validate.validate_dev_squad_dispatch_policy(root)

        self.assertEqual([], errors)

    def test_rejects_dev_skill_reference_to_unuploaded_squad_protocol_or_stale_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            protocol = root / "squads" / "dev-squad" / "protocol.md"
            dev_skill = root / "agents" / "dev-orchestrator-agent" / "skills" / "dev-coordination" / "SKILL.md"
            dev_protocol_copy = (
                root
                / "agents"
                / "dev-orchestrator-agent"
                / "skills"
                / "dev-coordination"
                / "references"
                / "squad-communication-protocol.md"
            )
            protocol.parent.mkdir(parents=True)
            dev_protocol_copy.parent.mkdir(parents=True)
            protocol.write_text("Multica, not Linear.\nContinuous Handoff.\n", encoding="utf-8")
            dev_protocol_copy.write_text("stale copy\n", encoding="utf-8")
            dev_skill.write_text(
                "Read `squads/dev-squad/protocol.md` for complete message templates.",
                encoding="utf-8",
            )

            errors = validate.validate_dev_squad_dispatch_policy(root)

        self.assertTrue(any("must reference references/squad-communication-protocol.md" in err for err in errors), errors)
        self.assertTrue(any("dev protocol copy differs" in err for err in errors), errors)


if __name__ == "__main__":
    unittest.main()
