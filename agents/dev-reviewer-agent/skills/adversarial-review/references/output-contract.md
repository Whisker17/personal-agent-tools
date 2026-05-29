# Adversarial Review Output Contract

Use this compact JSON shape when the caller asks for structured output or when another tool will consume the review.

```json
{
  "verdict": "approve | needs-attention",
  "summary": "Terse ship/no-ship assessment.",
  "findings": [
    {
      "severity": "critical | high | medium | low",
      "title": "Short risk title",
      "body": "What can go wrong, why this path is vulnerable, impact, and any inference used.",
      "file": "path/to/file",
      "line_start": 1,
      "line_end": 1,
      "confidence": 0.0,
      "recommendation": "Concrete change that reduces the risk."
    }
  ],
  "next_steps": [
    "Specific follow-up action."
  ]
}
```

## Rules

- Return valid JSON only when using this contract.
- Use `needs-attention` if any material risk should block shipping.
- Use `approve` only when no substantive adversarial finding is defensible.
- Keep `findings` empty on approval.
- Keep each finding tied to a concrete location. If source line evidence is unavailable, inspect more context before finalizing.
- Set `confidence` from `0` to `1`; lower it when the finding depends on an inference.
- Keep `summary` blunt and outcome-oriented, not a neutral recap.

## Finding Bar

Each finding must answer:

1. What can go wrong?
2. Why is this code path or design vulnerable?
3. What is the likely impact?
4. What concrete change would reduce the risk?

Before finalizing, remove any finding that is merely stylistic, unsupported, unactionable, or not plausible under a real failure scenario.
