---
name: team-code-understanding
description: Understand how a topic, objective or change relates to the code base in the current directory (code, design, architecture) using a team of subagents with domain-expert, adversarial, contrarian and web members and a judge who keeps only well-cited claims. Use when the user says "team-code-understanding" or "help me understand how X fits into this code base". Not for quick lookups.
---

# team-code-understanding

Invoke the `teamwork-core` skill with this parameter block (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it). If the cwd is not a code base, say so and stop.

- `objective`: the user's topic/objective, positioned against the code base in the cwd.
- `slug`: kebab-case topic.
- `scout_lenses` (`Explore` agents, shallow): structure (languages, build, layout, entry points); topic hits (code, config, tests, docs, ADRs, commits); architecture and data flow; history and ownership (`git log`/blame, skip if not git); dependencies and integration edges (if large/polyglot).
- `evidence_rules`: `path:line` / `path:start-end`, commit SHA, or URL (with date). Label `FACT | INFERENCE | UNKNOWN`. Experts must apply domain rules to the code (e.g. happens-before edges for a shared field), not restate it; claims that only restate code are weak.
- `sme_hints`: genuine domain experts drawn from what scouts found: language/runtime, frameworks, data stores, protocols, serialization, concurrency/consistency, security, performance, build/supply chain.
- `team_scale`: small 1-2 experts + 1 adversarial + 1 web; medium 3-5 + 1 + 2; large 6+ + 2 + 3 (contrarian always 1).
- `extra_rules`: all agents read-only on the repo (writes only inside `.teamwork/`). Add **web researchers** (`general-purpose`): non-code context only (specs, RFCs, library docs, known issues, design rationale, dated, primary preferred); they make no claims about this repo. Adversarial members also look for dead code that looks live, flag-dependent paths, tests contradicting assumptions.
- `output`: `kind: document`; path `./understanding-<slug>.md`; structure: Summary; How it fits (per focus area, cited); Design and architecture constraints; External context; Risks, gaps and counter-evidence (incl. contrarian view); Open questions; Where to start reading (ordered files). Inline `[path:line]` / `[url]`; INFERENCE marked. Editor must not alter citations.
