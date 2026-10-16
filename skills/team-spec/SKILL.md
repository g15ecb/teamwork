---
name: team-spec
description: Build a rigorous, over-constrained specification from a context markdown file using a team of persona/SME subagents plus adversarial and contrarian members, then a judge decides what goes in. Follows the project's existing spec format if one exists, otherwise Given/When/Then (BDD). Use when the user says "team-spec", "write a spec for X", or "spec this out from every angle". Usage - /team-spec path/to/context.md
---

# team-spec

Invoke the `teamwork-core` skill with this parameter block.

First, find the spec format: check `CLAUDE.md`, `AGENTS.md`, `README`, `CONTRIBUTING`, `docs/`, `spec(s)/`, `rfcs/`, `adr/`, templates, existing specs, and the conversation. Found: use it exactly (sections, IDs, MUST/SHOULD, location, naming) and record its source. None: BDD `Given / When / Then` (`When / Then` if no precondition), grouped under features with stable IDs (`FEAT-01.S3`).

Context: the user supplies a context markdown file path (ask once if missing; never proceed from memory). Read it all; split into focus, background, constraints/non-goals. Research is evidence, not requirements. Gaps and contradictions go to Open questions. Pass every agent the path and contents.

- `objective`: specify the focus described in the context file.
- `slug`: kebab-case name.
- `scout_lenses`: domain and prior art/standards; existing system and interfaces; users and flows; failure/abuse/operations; compatibility and constraints.
- `evidence_rules`: every spec entry cites its basis: a section/line of the context file, a standard/RFC/prior-art URL with quote, or `path:line` of existing code. Entries must be concrete and testable (inputs, thresholds, states, errors); no "fast/secure/user-friendly". Cover negative paths and boundaries. Unsupported speculation is excluded; unresolved ambiguity becomes an Open question, never silently resolved.
- `sme_hints`: at least 5 distinct angles from engineer, researcher, **tester (mandatory)**, QA, product/user, security, SRE, performance, compatibility, plus domain SMEs. The adversary/skeptic is mandatory and its items are never discarded wholesale.
- Judge bias: over-constrained beats under-constrained. When in doubt, include; on conflict between SMEs take the stricter behaviour or record both as an open question; sharpen weak-but-valid items.
- `output`: `kind: document`; path per the project's format, else `specs/<kebab-name>.md`; the spec in the chosen format with stable IDs, a Dismissed table (item, SME, reason), Open questions/assumptions. Header names the context file and format source.
- `extra_rules`: editor touches prose only (rationales, headings, open questions); IDs, Given/When/Then, MUST/SHOULD, thresholds, identifiers, code stay byte-identical; if a rewrite changes meaning keep the original.
