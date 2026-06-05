# personalos-core

The canonical schema-first core for `Project_Codex`.

## What it is

- TypeScript `core + adapters` package
- One chief-of-staff orchestration surface
- Interaction router built around:
  - `cue`
  - `likely inference`
  - `correct inference`
  - `optimal mode`
  - `failure mode`
  - `recovery move`
- Approval-gated `intake -> route -> act` loop
- Self-contained runtime state inside this package

## Modules

- `src/core/interaction-router.ts`
  - schema-first assessment and mode routing
- `src/core/context-builder.ts`
  - builds configurable `Life_OS` context bundles
- `src/core/orchestrator.ts`
  - public API and work-item lifecycle
- `src/core/action-coordinator.ts`
  - turns plans into safe action proposals and approvals
- `src/storage/file-runtime-store.ts`
  - local runtime persistence for sessions, ledgers, work items, approvals, executions, and reflections
- `src/adapters/*`
  - thin translators for ChatGPT, local, Cloudflare, and derived memory/vector use

## Defaults

- Runtime state defaults to `runtime/state.json` inside this package.
- Context roots default to `runtime/life-os` inside this package unless `lifeOsRoot` or `LIFE_OS_ROOT` is provided explicitly.
- No sibling project dependencies are required.

## Commands

```bash
npm install
npm run build
npm run test
npm run demo
```
