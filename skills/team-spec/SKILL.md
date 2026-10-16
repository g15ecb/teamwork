---
name: team-spec
description: Build a rigorous, over-constrained specification from a context markdown file using a team of persona/SME subagents plus adversarial and contrarian members, then a judge decides what goes in. Follows the project's existing spec format if one exists, otherwise Given/When/Then (BDD). Use when the user says "team-spec", "write a spec for X", or "spec this out from every angle". Usage - /team-spec path/to/context.md
---

# team-spec

Invoke the `teamwork-core` skill with this parameter block (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it).

First, find the spec format: check `CLAUDE.md`, `AGENTS.md`, `README`, `CONTRIBUTING`, `docs/`, `spec(s)/`, `rfcs/`, `adr/`, templates, existing specs, and the conversation. Found: use it exactly (sections, IDs, MUST/SHOULD, location, naming) and record its source. If several formats conflict, ask which to follow with an `AskUserQuestion` single-select (one option per format, each with its source) in the stage-2 run-settings call. None: BDD `Given / When / Then` (`When / Then` if no precondition), grouped under features with stable IDs (`FEAT-01.S3`).

Context: the user supplies a context markdown file path. If missing, ask once via `AskUserQuestion`, offering up to 4 likely candidates (`.md` files mentioned in the conversation, then recently modified ones outside `.teamwork/`) with "Other" for a typed path. Never proceed from memory. Read it all; split into focus, background, constraints/non-goals. Research is evidence, not requirements. Gaps and contradictions go to Open questions. Put the context file's absolute path, the chosen format and its source in `brief.md`; every agent reads the context file in full.

- `objective`: specify the focus described in the context file.
- `slug`: kebab-case name.
- `scout_lenses`: domain and prior art/standards; existing system and interfaces; users and flows; failure/abuse/operations; compatibility and constraints.
- `evidence_rules`: every spec entry cites its basis: a section/line of the context file, a standard/RFC/prior-art URL with quote, or `path:line` of existing code. Entries must be concrete and testable (inputs, thresholds, states, errors); no "fast/secure/user-friendly". Cover negative paths and boundaries. Unsupported speculation is excluded; unresolved ambiguity becomes an Open question, never silently resolved.
- `sme_hints`: at least 5 distinct angles from engineer, researcher, QA, product/user, security, SRE, performance, compatibility, plus domain SMEs.
- `mandatory_roles`: tester (writes concrete scenarios incl. boundaries, negative paths, error states). Adversarial items are never discarded wholesale.
- `judge_bias`: over-constrained beats under-constrained. When in doubt, include; on conflict between SMEs take the stricter behaviour or record both as an open question; sharpen weak-but-valid items.
- `output`: `kind: document`; path per the project's format, else `specs/<kebab-name>.md`; the spec in the chosen format with stable IDs, a Dismissed table (item, SME, reason), Open questions/assumptions. Header names the context file and format source.
- `extra_rules`: editor touches prose only (rationales, headings, open questions); IDs, Given/When/Then, MUST/SHOULD, thresholds, identifiers, code stay byte-identical; if a rewrite changes meaning keep the original. Protected tokens for the editor diff: every line matching `^\s*(Given|When|Then|And|But)\b`, every stable ID, every `MUST|SHOULD|MAY` sentence.
