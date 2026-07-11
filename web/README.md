# LoopLine Resolve AI — web UI

A React + TypeScript (Vite) interface for the warranty copilot. Dark-first
"refined ops console" design with a light theme; theme choice persists and
respects your OS preference.

## Running it

The UI needs the FastAPI backend running for its data. Two terminals:

```bash
# Terminal 1 — backend (from repo root, venv active)
uvicorn app.api.main:app --reload        # or: make api

# Terminal 2 — web dev server
cd web && npm install                     # first time only
npm run dev                               # or: make web
```

Then open http://localhost:5173. Vite proxies `/api` and `/health` to the
backend on `:8000`, so the browser talks to a single origin.

## What's real vs. shell

The UI holds to the project's "real schema, honest state" principle:

| View | Backing |
| --- | --- |
| Claim intake | **Real** — the six synthetic cases, live from `/api/cases` |
| Evidence workspace | **Real** — evidence list + live extraction from `/api/cases/{id}` (runs the actual Phase 5 pipeline in the configured provider mode) |
| Knowledge & RAG | Labeled shell — backend arrives in Phase 9/10 |
| Supervisor approval | Labeled shell — backend arrives in Phase 10/11 |
| Evaluation & ops | Labeled shell — backend arrives in Phase 12/13 |

The provider badge (bottom-left / top-right) reflects `APP_PROVIDER_MODE`:
`mock · simulated`, `local`, or `azure`. Flip `.env` to `azure` and the
Evidence view runs real Document Intelligence extraction.

## Build

```bash
npm run build        # tsc type-check + vite production build → dist/
```

## Layout

```
web/src/
├── api/client.ts        typed fetch client + response types
├── components/          AppShell, icons, primitives (badges, confidence bar), ProviderBadge
├── lib/                 theme + async hooks, formatters
├── styles/global.css    the design system (tokens, both themes, all components)
└── views/               Intake, Evidence (data-backed) + Knowledge/Approval/Ops (shells)
```
