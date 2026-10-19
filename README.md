# teamwork

Skills for [skills.sh](https://skills.sh) that run a team of subagents against an objective: scouts explore, you pick focus areas and experts from a UI prompt, cited SMEs plus an adversarial and a contrarian member do the work, adversaries cross-examine the SMEs' claims, verifiers re-check every citation, a judge rules (one right of reply per questionable statement), a synthesiser writes the output from the included claims only (trace-checked back to the rulings), and an editor de-slops document outputs.

## Install

```
npx skills add g15ecb/teamwork
```

Installs all seven skills.

**You must always install `teamwork-core`.** `teamwork-research`, `teamwork-spec`, `teamwork-design`, `teamwork-plan` and `teamwork-code-understanding` are thin wrappers that call it and do nothing without it. If you install skills selectively, include it:

```
npx skills add g15ecb/teamwork --skill teamwork-core --skill teamwork-research
```

`teamwork-plan` and `teamwork-deliver` need `python3` 3.9 or later on the PATH (standard library only, no packages): the graph check uses `graphlib`.

## Skills

| Skill | Use |
|---|---|
| `teamwork-research` | `teamwork-research: <topic>` writes `SLUG.md`. Confirms sources (web, this repo, repo + web, given files) and shape (how it works, background, compare, reference, fit) before starting; can read upstream source code |
| `teamwork-spec` | `/teamwork-spec path/to/context.md [format instructions]` writes a spec (your format, the project's, else Gherkin), every step cited to the context |
| `teamwork-design` | `/teamwork-design path/to/spec.md [format instructions]` turns an existing spec into ranked candidate designs: architects with different stances, pre-mortemed by an adversary, scored 0-5 on spec coverage, simplicity, idiomatic fit, maintainability, safety, future-proofing, operability and testability and shown as a table (you pick the format and priority up front, and which design the document proposes once they're ranked). Every design traces each spec component to the code it changes. Writes the project's design-doc format (else a standard design doc), format-verified |
| `teamwork-plan` | `/teamwork-plan path/to/design.md [format instructions]` breaks a design into a delivery plan: a dependency graph of steps, each one git commit gated by a test command that must pass first, scheduled in waves that subagents can run in parallel. Planners with different stances (parallel-first, safe increments, vertical slices) are audited for missing and needless dependencies, and you pick the plan. A bundled Python 3.9+ script checks the graph (no cycles, no unordered steps sharing a file) and computes the recommended subagent count. Steps are a TODO checklist; a ticked step records the SHA it landed as. Plans only; `teamwork-deliver` runs the plan |
| `teamwork-deliver` | `/teamwork-deliver path/to/plan.md` runs a `teamwork-plan` plan: one implementer subagent per step in its own git worktree, wave by wave in parallel. Each step is checked mechanically (it touches only its files, its gate passes, new tests fail without the change), optionally reviewed, and cherry-picked as one commit onto `deliver/<slug>` with a `Plan-Step` trailer. After each wave, a commit on that branch ticks the plan with each landed step's SHA; a re-run resumes from the trailers in git history. A step that fails twice blocks its dependents while independent steps continue. You approve every command it runs; it never touches your checkout or pushes. Standalone (not a core wrapper); needs `teamwork-plan` installed for its graph script |
| `teamwork-code-understanding` | `teamwork-code-understanding: <topic>` writes `understanding-SLUG.md`. Alias for `teamwork-research` with sources repo + web and shape fit; needs `teamwork-research` installed |
| `teamwork-core` | Private engine (`user-invocable: false`); the wrappers above call it with a parameter block; `teamwork-deliver` reuses its orchestration rules and models |

Scratch ledgers and rulings live in `.teamwork/<slug>/`.

## Models

Each subagent is spawned on a fixed model, whatever model your session uses. The orchestrator (your session) should be Opus: it merges the scout reports, picks the team and writes every agent prompt. On hosts with no per-agent model setting, every agent runs on the session model.

| Role | Model | Why |
|---|---|---|
| Orchestrator (your session) | Opus (recommended) | Merges scouts, picks the team, writes standalone prompts, routes right of reply |
| Scouts | Sonnet | Shallow sketches, 400 words or fewer |
| SMEs, adversarial, contrarian, architects, planners, tester, implementers, reviewers | Opus | Expert depth and counter-example hunting decide output quality; implementing a step and reviewing its diff are judgment work |
| Web researchers | Sonnet | Fetch and cite non-code context |
| Verifiers | Sonnet | Narrow check: quote present, statement entailed. Highest call count |
| Judge | Opus | Weighting, contradictions and fidelity; everything downstream depends on it |
| Synthesiser | Opus | Frames the explanation without adding facts |
| Editor, format verifier | Sonnet | Mechanical, and checked by shell diffs |
