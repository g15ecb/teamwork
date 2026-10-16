---
name: teamwork-spec
description: Build a rigorous, over-constrained specification from a user-supplied context markdown file using a team of persona/SME subagents plus adversarial and contrarian members, then a judge decides what goes in. Uses the spec instructions/format the user or project specifies, otherwise Gherkin (Given/When/Then). Every Given/When/Then step cites the source of truth it directly derives from. Use when the user says "teamwork-spec", "write a spec for X", or "spec this out from every angle". Usage - /teamwork-spec path/to/context.md [format instructions]
---

# teamwork-spec

Invoke the `teamwork-core` skill with this parameter block (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it).

**Context is given, not researched.** The user supplies a context markdown file path (and possibly spec instructions) at invocation. That file, the documents it links or names, and the code in this repo are the sources of truth (core's `given` mode). If the path is missing, ask once via `AskUserQuestion`, offering up to 4 likely candidates (`.md` files mentioned in the conversation, then recently modified ones outside `.teamwork/`) with "Other" for a typed path. Never proceed from memory. Read it all; split into focus, sources of truth, constraints/non-goals, and any spec instructions. Gaps and contradictions go to Open questions.

**Spec format** is resolved, confirmed and verified by core's **Output format** (see `format` below). Put the context file's absolute path in `brief.md`; every agent reads the context file in full.

**Step citations (all formats).** Every `Given`, `When`, `Then`, `And`, `But` step, every `Rule:` and every `Examples:` row carries its own citation to the source of truth it directly derives from. In Gherkin, put it on a comment line immediately above the step (Gherkin has no trailing comments): `# [S4]` or `# [S4][S9]`. Each `[Sn]` resolves in a Sources table: `id | location | verbatim quote`, where location is `context.md §heading Lnn-mm`, a document the context links (URL or path + section), or `path:line` in the repo. If the user's format defines its own citation style, use it, but per-step granularity still applies. A scenario-level or feature-level citation does not cover its steps. The synthesiser's trace markers go on the citation line, after the `[Sn]`s (`# [S4] {#tester-3}`), never on a step line.

- `objective`: specify the focus described in the context file.
- `slug`: kebab-case name.
- `sources`: `given` (the context file), repo code allowed.
- `scout_lenses`: requirements, rules and actors stated in the context file; documents the context links; existing system and interfaces in the repo; users and flows; failure/abuse/operations; compatibility and constraints.
- `evidence_rules`: every step cites a source of truth (above) with a verbatim quote that on its own entails the step: a direct derivation, not a related passage or an inference chain. A step built from several facts cites each. Steps must be concrete and testable (inputs, thresholds, states, errors); no "fast/secure/user-friendly". Cover negative paths and boundaries where the sources state them. A step with no direct source is excluded; if the scenario needs it, the gap becomes an Open question, never a silent assumption.
- `sme_hints`: at least 5 distinct angles from engineer, QA, product/user, security, SRE, performance, compatibility, plus domain SMEs. SMEs mine the given sources; they don't research beyond them.
- `mandatory_roles`: tester (writes concrete scenarios incl. boundaries, negative paths, error states, each step cited). Adversarial members also attack citations: a quote that doesn't directly entail its step is a finding. Adversarial items are never discarded wholesale.
- `judge_bias`: over-constrained beats under-constrained, within what the sources support. When in doubt, include if cited; on conflict between SMEs take the stricter behaviour or record both as an open question; sharpen weak-but-valid items. Any uncited or not-directly-entailed step excludes its scenario unless the step can be cut or re-cited.
- `output`: `kind: document`; path per the user's instructions, else the project's format, else `specs/<kebab-name>.md` with the Gherkin in fenced `gherkin` blocks. Contents: header (context file, format and its source), the spec with stable IDs and per-step citations, the Sources table, a Dismissed table (item, SME, reason), Open questions/assumptions.
- `extra_rules`: editor touches prose only (rationales, headings, open questions); IDs, steps, citations, Sources table, MUST/SHOULD, thresholds, identifiers, code stay byte-identical; if a rewrite changes meaning keep the original. Protected tokens for the editor diff: every line matching `^\s*(Feature|Rule|Background|Scenario|Scenario Outline|Examples|Given|When|Then|And|But)\b|^\s*#\s*\[S[0-9]+\]|^\s*\|`, every stable ID, every `MUST|SHOULD|MAY` sentence.
- `format`:
  - `search`: `docs/`, `spec(s)/`, `features/`, `rfcs/`, `adr/`, existing specs.
  - `default`: **Gherkin** (Cucumber reference syntax). `Feature:` with a short description; `Rule:` per business rule; `Background:` for shared `Given`s; `Scenario:` / `Scenario Outline:` + `Examples:` for boundaries; steps `Given` (state), `When` (one action), `Then` (observable outcome), `And`/`But`. One `When` per scenario, declarative steps (behaviour, not UI clicks), third person, present tense. Stable IDs as tags: `@FEAT-01`, `@FEAT-01.R2`, `@FEAT-01.S3`.
  - `required`: per-step citations (above). The verifier also checks mechanically that every step line has a citation line directly above it and every `[Sn]` resolves in the Sources table.
