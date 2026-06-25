# publish-ai

A personal publishing agent that watches notes, drafts content, gates it through human verification, and publishes — under a real byline.

## Why this exists

Most agent harnesses optimize for autonomy. A publishing agent that posts under your name needs the opposite: it should draft freely but **never publish without explicit human approval**. This project builds that pipeline on top of [Hermes](https://github.com/NousResearch/Hermes) (Nous Research), chosen specifically because its defaults point toward isolation and restraint rather than permissiveness.

## Architecture

```
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌────────────────────┐    ┌───────────┐
│  Watcher  │───▶│ Draft Agent  │───▶│ Self-checks  │───▶│ Verification Gate  │───▶│ Publisher  │
│           │    │  (mid-tier)  │    │              │    │   (human-in-loop)  │    │(restricted)│
└──────────┘    └─────────────┘    └─────────────┘    └────────────────────┘    └───────────┘
 deterministic    restricted           internal            NEVER autonomous        per-domain
 wakeAgent        tool list            quality checks      NEVER headless          isolation
```

- **Watcher** — Deterministic `wakeAgent` script that polls for note changes. Only invokes a model when something actually changed.
- **Draft Agent** — Generates drafts using a mid-tier model. Gets a minimal tool list to keep costs down and reduce attack surface.
- **Self-checks** — Internal verification layer before human review.
- **Verification Gate** — The load-bearing control. Human approves or rejects every publish. Pinned outside the learning loop so the agent can never learn to bypass it.
- **Publisher** — Isolated in its own restricted domain behind a permission prompt. Separated from the main conversation.

## Harness selection

**Hermes** was selected over OpenClaw after firsthand experience with both. The full decision record is in [`PLAN-publish.md`](PLAN-publish.md). The short version:

OpenClaw is permissive by default — it gives the agent free rein and expects the user to sandbox it. Its heartbeat model injects background events into the main conversation against unbounded accumulating memory. For an agent whose one load-bearing control is "drafts autonomously, never publishes autonomously," a porous boundary between background processing and the live conversation works against the gate.

Hermes inverts each of those defaults: restrictive by default, sandboxed cron isolated from the main conversation, confined script locations, per-domain isolation.

**Honest counterweights** (included because the plan requires them):
- Hermes's stability record is partly youth (~6 releases vs. OpenClaw's ~82) — it hasn't lived long enough to accumulate the breakage OpenClaw is criticized for.
- The learning loop is double-edged: Hermes can turn recurring tasks into reusable skills unprompted, but bad decisions get learned too and are hard to remove.

## Constraints

| ID | Constraint | Rationale |
|----|-----------|-----------|
| C-H1 | Verification gate sits **outside** the learning loop | The gate must never be self-rewritten or become a learned skill |
| C-H2 | Cost discipline: (1) wake less, (2) route by tier, (3) slim the tool list | Deterministic waking, tiered models, minimal tooling — in that priority order |
| C-H3 | Administer from CLI/TUI, not chat | The harness lives on the cluster; do not assume phone-only administration |

## Status

Pre-implementation. The architecture decision is recorded; implementation begins in Phase P1.

## License

MIT
