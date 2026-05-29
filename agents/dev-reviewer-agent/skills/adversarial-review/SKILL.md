---
name: adversarial-review
description: "Use when challenging a PR, branch diff, working-tree change, or implementation plan from an adversarial design-review stance: question whether the approach should ship, pressure-test assumptions, and report only material, grounded risks in correctness, security, data integrity, rollback safety, concurrency, compatibility, observability, or failure handling."
---

# Adversarial Review

Challenge the change as if trying to find the strongest defensible reason it should not ship yet. This is not a stricter style pass over code; it is a design-level pressure test after the structural review has found ordinary implementation defects.

## References

Load as needed:

- `references/output-contract.md` - compact JSON result shape and finding field rules.

## Operating Stance

Default to skepticism. Assume the change can fail in subtle, high-cost, or user-visible ways until the evidence says otherwise.

Do not give credit for intent, partial fixes, or likely follow-up work. If behavior only works on the happy path, treat that as a real weakness.

## Workflow

1. Define the target and focus.
   - Target may be a PR diff, branch diff, working tree, design document, or implementation plan.
   - If the user provides a focus area, weight it heavily while still reporting other material risks.
   - If no focus is provided, use the full attack surface below.

2. Collect primary evidence.
   - Review persisted diffs or source files, not summaries alone.
   - For branch reviews, inspect the merge-base diff, changed files, relevant call sites, tests, migrations, configs, and public contracts.
   - For working-tree reviews, include staged, unstaged, and untracked reviewable files.
   - If only a lightweight summary is available, run read-only inspection commands before finalizing.

3. Try to disprove the approach.
   - Look for violated invariants, missing guards, unhandled failure paths, and assumptions that stop being true under stress.
   - Trace bad inputs, retries, concurrent actions, stale state, timeouts, degraded dependencies, and partially completed operations through the code.
   - Compare the chosen design to simpler or safer alternatives only when the alternative exposes a material risk.

4. Apply the attack surface.
   - Auth, permissions, tenant isolation, and trust boundaries.
   - Data loss, corruption, duplication, and irreversible state changes.
   - Rollback safety, retries, partial failure, and idempotency gaps.
   - Race conditions, ordering assumptions, stale state, and re-entrancy.
   - Empty-state, null, timeout, and degraded dependency behavior.
   - Version skew, schema drift, migration hazards, and compatibility regressions.
   - Observability gaps that would hide failure or make recovery harder.

5. Report only material findings.
   - Prefer one strong, well-grounded finding over several weak ones.
   - Do not include style feedback, naming feedback, low-value cleanup, or speculative concerns without evidence.
   - Every finding must answer: what can go wrong, why this path is vulnerable, likely impact, and the concrete change that reduces risk.

## Grounding Rules

- Stay aggressive but grounded.
- Tie every finding to a concrete file and line range when source is available.
- Do not invent files, behavior, incidents, attack chains, or runtime semantics.
- If a conclusion depends on inference, say so in the finding body and lower confidence accordingly.
- If the change looks safe after adversarial inspection, say so directly and return no findings.

## Output

When the caller needs machine-readable output, use the JSON contract in `references/output-contract.md`.

When the caller needs the dev squad verdict template, add adversarial findings into the `Adversarial findings` section defined by the Dev Reviewer instructions and preserve the Orchestrator handoff rules.

Use `needs-attention` or `request-changes` if any material adversarial risk should block shipping. Use `approve` only when no substantive adversarial finding can be supported from the available evidence.
