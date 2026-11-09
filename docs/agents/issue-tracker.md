# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## Wayfinding: map-only (solo override, 2026-11-09)

The user runs solo and has overridden child tickets for the wayfinder effort `agent-v01-spec`:

- The map at `.scratch/agent-v01-spec/map.md` is the ONLY artifact: no `issues/` directory, no child files.
- **Frontier** = the numbered list in the map's `## Open decisions` section, in order; entries awaiting another decision are marked `(awaits N)` and are skipped until their prerequisite is in Decisions so far.
- **One decision per session**, top-first, unless the user names one.
- A **resolution** is recorded once — as that decision's entry moved into `## Decisions so far` with a compact answer (1–3 sentences + source links). The Decisions-so-far entry is the single home of the decision; it is not restated elsewhere.
- Research that feeds an open decision runs as a subagent; findings land under `research/` at the repo root and are cited from the resolution entry.
- Fog lives at `## Not yet specified`; out-of-scope work at `## Out of scope` (returned only if the destination is redrawn).
