# teamwork

Skills for [skills.sh](https://skills.sh) that run a team of subagents against an objective: scouts explore, you pick focus areas and experts from a UI prompt, cited SMEs plus an adversarial and a contrarian member do the work, adversaries cross-examine the SMEs' claims, verifiers re-check every citation, a judge rules (one right of reply per questionable statement), a synthesiser writes the output from the included claims only (trace-checked back to the rulings), and an editor de-slops document outputs.

## Install

```
npx skills add g15ecb/teamwork
```

Installs all five skills.

**You must always install `teamwork-core`.** `teamwork-research`, `teamwork-spec`, `teamwork-design` and `teamwork-code-understanding` are thin wrappers that call it and do nothing without it. If you install skills selectively, include it:

```
npx skills add g15ecb/teamwork --skill teamwork-core --skill teamwork-research
```

## Skills

| Skill | Use |
|---|---|
| `teamwork-research` | `teamwork-research: <topic>` writes `SLUG.md`. Confirms sources (web, this repo, repo + web, given files) and shape (how it works, background, compare, reference, fit) before starting; can read upstream source code |
| `teamwork-spec` | `/teamwork-spec path/to/context.md [format instructions]` writes a spec (your format, the project's, else Gherkin), every step cited to the context |
| `teamwork-design` | `/teamwork-design path/to/spec.md [format instructions]` turns an existing spec into ranked candidate designs: architects with different stances, pre-mortemed by an adversary, scored 0-5 on spec coverage, simplicity, idiomatic fit, maintainability, safety, future-proofing, operability and testability and shown as a table (you pick the format and priority up front, and which design the document proposes once they're ranked). Every design traces each spec component to the code it changes. Writes the project's design-doc format (else a standard design doc), format-verified |
| `teamwork-code-understanding` | `teamwork-code-understanding: <topic>` writes `understanding-SLUG.md`. Alias for `teamwork-research` with sources repo + web and shape fit; needs `teamwork-research` installed |
| `teamwork-core` | Private engine (`user-invocable: false`); the four above call it with a parameter block |

Scratch ledgers and rulings live in `.teamwork/<slug>/`.

## Models

Each subagent is spawned on a fixed model, whatever model your session uses. The orchestrator (your session) should be Opus: it merges the scout reports, picks the team and writes every agent prompt. On hosts with no per-agent model setting, every agent runs on the session model.

| Role | Model | Why |
|---|---|---|
| Orchestrator (your session) | Opus (recommended) | Merges scouts, picks the team, writes standalone prompts, routes right of reply |
| Scouts | Sonnet | Shallow sketches, 400 words or fewer |
| SMEs, adversarial, contrarian, architects, tester | Opus | Expert depth and counter-example hunting decide output quality |
| Web researchers | Sonnet | Fetch and cite non-code context |
| Verifiers | Sonnet | Narrow check: quote present, statement entailed. Highest call count |
| Judge | Opus | Weighting, contradictions and fidelity; everything downstream depends on it |
| Synthesiser | Opus | Frames the explanation without adding facts |
| Editor, format verifier | Sonnet | Mechanical, and checked by shell diffs |
