# Crypto Review Workflow Reference

## Operating Stance

Break confidence in the report, not validate it. Default to skepticism and only credit claims supported by evidence.

## Attack Surfaces

Critical:

- fabricated or unverifiable sources;
- source-claim mismatch;
- on-chain/off-chain contradiction.

Major:

- logical gaps;
- survivorship bias;
- missing counterarguments;
- confidence inflation;
- tokenomics, security, governance, temporal, or composability blind spots.

Use `domain-checklists.md` for detailed crypto/DeFi checks.

## Method

1. Identify stated scope, audience, and structure.
2. Attempt to disprove important claims.
3. Trace source chains.
4. Stress test assumptions.
5. Check omissions.
6. Evaluate methodology.

Stress scenarios include market crash, team exit, competitive fork, regulatory action, oracle failure, bridge exploit, or dependency protocol failure.

## Finding Standards

Each finding needs:

- what can fail;
- why it is weak;
- impact;
- suggested fix;
- evidence or `[INFERRED]` marker.

Skip style and tone feedback.

## Output

Return valid JSON with:

- `verdict`: `needs-attention` or `approve`;
- `confidence`;
- `summary`;
- `critical_findings`;
- `major_findings`;
- `minor_findings`;
- `stress_test_results`;
- `missing_coverage`;
- `revision_instructions` when needed.

## Verdict

- `needs-attention`: any critical finding, at least 3 major findings, or confidence below 0.6.
- `approve`: no critical findings, fewer than 3 major findings, and confidence at least 0.6.
