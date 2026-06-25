# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**publish_ai** is a personal publishing agent that watches notes, drafts content, gates it through human verification, and publishes. It is a named-byline agent — security and trust constraints are load-bearing, not optional.

## Architecture (Target State)

Five components orchestrated by **Hermes (Nous Research)**:

1. **Watcher** — Monitors personal notes for changes. Deterministic `wakeAgent` script; only invokes a model when notes actually change.
2. **Draft Agent** — Generates drafts from watched notes. Uses a mid-tier model with a restricted tool list.
3. **Self-checks** — Internal verification/quality checks on generated content.
4. **Verification Gate** — Human-in-the-loop approval before publishing. **Never headless. Never autonomous.** Sits outside the learning loop (constraint C-H1).
5. **Publisher** — Restricted action domain behind a permission prompt. Isolated from the main conversation via per-domain isolation.

## Load-Bearing Constraints

These constraints are non-negotiable and must survive any refactoring:

- **C-H1**: The verification gate MUST sit OUTSIDE anything the learning loop can modify. Pin it in a confined script location; it must never become a learned skill or be self-rewritten.
- **C-H2**: Cost discipline in priority order — (1) wake less (deterministic `wakeAgent`, model only on actual change); (2) route by tier (cheap/open-weight for watch, mid-tier for drafting, never frontier on a schedule); (3) slim the tool list (draft agent gets only needed tools).
- **C-H3**: Administer from CLI/TUI, not chat. Do not assume phone-only administration.

## Key Design Decisions

- **Hermes over OpenClaw**: OpenClaw's permissive-by-default security posture was rejected. Hermes provides restrictive-by-default behavior, sandboxed cron isolated from the main conversation, confined script locations, and per-domain isolation — all critical for a named-byline agent.
- **No heartbeat model**: Uses explicit `wakeAgent` script gates instead of background events injecting into the main conversation.
- **Learning loop caution**: Hermes can turn recurring tasks into reusable skills unprompted, but bad decisions get learned too. The verification gate is explicitly excluded from this loop.

## Project Status

Pre-implementation (planning phase). See `PLAN-publish.md` for the full ADR on harness selection. Implementation begins in Phase P1.
