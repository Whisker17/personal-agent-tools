# Agent Authoring Workflow Reference

## Prompt Boundary

System prompts define:

- what the agent is;
- what it can do;
- what it cannot do;
- input parameters;
- which skills it must use.

System prompts do not contain long workflows, templates, checklists, examples, CLI recipes, or domain knowledge. Those belong in skills and `references/`.

## Discovery Questions

Collect:

1. purpose;
2. input and output;
3. domain;
4. dynamic parameters;
5. required skills or new skill needs.

Ask one question at a time.

## Prompt Template

```markdown
# {Agent Name}

You are {role}. You {core responsibility}.

You do not {boundaries}.

## Inputs

- `{{param}}`: {meaning}.

## Required Skills

- Use `{skill-name}` for {work type}.

## Boundaries

- {hard rule}
- {hard rule}
```

## Skill Placement

If the agent needs detailed procedures, create or attach a skill:

- workflow details -> `skills/{skill}/SKILL.md` plus `references/workflow.md`;
- examples -> `references/examples.md`;
- schemas -> `references/schema.md`;
- CLI commands -> `references/cli.md`;
- domain facts -> `references/{domain}.md`.

Keep `SKILL.md` as the short entry and navigation layer when details are long.

## Config Generation

Generate:

- `agents/{agent-name}.yaml`;
- `prompts/system/{agent-name}.md`;
- local skill folders if needed.

Use `knowledge: []` unless there is a verified runtime reason to use repo-level knowledge. Prefer skill references for guidance and domain context.

## Validation

Run `scripts/validate` after creating or updating agent configs.
