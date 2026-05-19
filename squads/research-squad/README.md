# research-squad

Thin orchestration layer for the four runtime research agents.

- Squad config: `squad.yaml`
- Squad instructions: `instructions.md` (injected into the leader agent's prompt)
- Canonical protocol: `protocol.md`

Agent definitions stay under `agents/`; this directory only records composition and coordination rules.

Project Planner is intentionally not a runtime squad member. Use it before starting the squad to design project structure, research issues, slugs, ordering, dependencies, and TW reserved issue metadata.
