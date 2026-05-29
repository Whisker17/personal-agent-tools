---
name: tdd
description: "Use when implementing features or fixing bugs — drives development through red-green-refactor cycles with vertical slices. Default methodology for all dev-engineer-agent implementation tasks."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Test-Driven Development

## Philosophy

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists.

See [tests.md](references/tests.md) for examples and [mocking.md](references/mocking.md) for mocking guidelines.

## Anti-Pattern: Horizontal Slices

DO NOT write all tests first, then all implementation. This is "horizontal slicing" — it produces tests that test imagined behavior, not actual behavior.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

## Workflow

### 1. Planning

Before writing any code:

- Read existing code and match the project's domain vocabulary, naming conventions, and test patterns.
- Identify the behaviors to test from the task's acceptance criteria.
- Design interfaces for [testability](references/interface-design.md) and [depth](references/deep-modules.md).
- List behaviors to test (not implementation steps).

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:
- One test at a time.
- Only enough code to pass current test.
- Don't anticipate future tests.
- Keep tests focused on observable behavior.

### 4. Refactor

After all tests pass, look for [refactor candidates](references/refactoring.md):

- Extract duplication.
- Deepen modules (move complexity behind simple interfaces).
- Apply SOLID principles where natural.
- Run tests after each refactor step.

**Never refactor while RED.** Get to GREEN first.

## Per-Cycle Checklist

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```

## References

Load as needed:

- `references/tests.md` — good vs bad test examples
- `references/mocking.md` — when and how to mock
- `references/refactoring.md` — refactor candidates after GREEN
- `references/interface-design.md` — designing testable interfaces
- `references/deep-modules.md` — small interface, deep implementation
