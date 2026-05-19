# Diagram Upgrade Guide

Decision framework for handling diagrams in the final research report.

## Upgrade Decision Table

| Diagram Type | Treatment | Rationale |
|---|---|---|
| Architecture / system overview | **Upgrade** with `/fireworks-tech-graph` | Spatial relationships and layered architecture are significantly clearer with polished visuals |
| Component relationship / dependency graphs | **Upgrade** with `/fireworks-tech-graph` | Complex node-edge relationships benefit from professional layout algorithms |
| Flowcharts / process diagrams | **Keep as Mermaid** | Mermaid renders linear flows well; they're easier to maintain and version |
| Sequence diagrams | **Keep as Mermaid** | Mermaid's native sequence diagram support is excellent for temporal interactions |
| State diagrams | **Keep as Mermaid** | Straightforward state machines don't need visual polish beyond Mermaid |
| Simple ASCII diagrams | **Upgrade to Mermaid** minimum | ASCII is acceptable in research drafts but not in the final report |

## Rule of Thumb

Use `/fireworks-tech-graph` only when the diagram conveys **spatial relationships, layered architecture, or complex system topology** that Mermaid cannot represent well.

For **sequential, temporal, or process** flows, Mermaid is preferred because it is maintainable, version-controllable, and renders cleanly in markdown viewers.

## `/fireworks-tech-graph` Workflow

When upgrading a diagram:

1. Extract the conceptual content from the source diagram (Mermaid or ASCII)
2. Invoke `/fireworks-tech-graph` with a clear description of nodes, layers, and relationships
3. Save the output (SVG + PNG) to `{project-slug}/report/assets/{descriptive-name}.{ext}`
4. Reference in the report using a relative path: `![Description](assets/{descriptive-name}.png)`
5. Keep the original Mermaid/ASCII as a comment or in a `<details>` block for maintainability

## Unavailability Fallback

If `/fireworks-tech-graph` is not accessible at runtime:

1. Render ALL diagrams as Mermaid (including those that would normally be upgraded)
2. Add a note in the report appendix under "Methodology Notes":
   > Architecture diagrams rendered as Mermaid due to `/fireworks-tech-graph` unavailability. See M1 integration gap.
3. Include this gap in the completion comment under "Unresolved Risks / Integration Gaps"
4. Do NOT block the report — it still ships with Mermaid-only diagrams

## Asset Organization

```
{project-slug}/report/
├── final-report.md
└── assets/
    ├── architecture-overview.png
    ├── architecture-overview.svg
    ├── token-flow.png
    └── ...
```

All asset references inside `final-report.md` use relative paths from the `report/` directory:
```markdown
![Architecture Overview](assets/architecture-overview.png)
```
