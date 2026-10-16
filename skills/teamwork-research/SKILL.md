---
name: teamwork-research
description: Rigorous, adversarially-tested, fully-cited research using a team of subagents (scouts, SMEs, adversarial and contrarian members, verifiers, a judge, a synthesiser, an anti-slop editor). Handles how something works, background on a topic, comparing options, exhaustive reference, and how a topic fits into the code base in the cwd; sources can be the web, this repo, upstream source code or given files. Writes a markdown document. Use when the user says "teamwork-research", "research X", "deep research on X", "how does X work", "background on X", "compare X and Y", or wants rigorous, source-cited research rather than a quick answer. Not for quick lookups.
---

# teamwork-research

Invoke the `teamwork-core` skill with the parameter block below (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it). The objective is the user's topic. This skill only defines the research shapes; core owns sources, citation, roles and judging.

## Parameter block

- `objective`: the topic, with the confirmed sources and shape.
- `slug`: kebab-case topic.
- `pre_questions`:
  1. **Sources**: `web` (default when the cwd has nothing to do with the topic) / `repo + web` / `repo` / `given`.
  2. **Shape**: `how-it-works` (the mechanism of a system, protocol, algorithm or feature) / `background` (what it is, where it came from, where it stands) / `compare` (options against criteria, toward a decision) / `reference` (exhaustive cited reference). Offer `fit` (how a topic, objective or change relates to this code base) only with a repo source; with 5 options, drop the least likely.
  3. Only if the topic is ambiguous: scope (narrow/broad readings), then time horizon or audience. Otherwise default the horizon to what the topic needs and the audience to practitioner.
- `sources`: from pre-question 1.
- `scout_lenses`, `role_overrides`, `output.structure`: from the shape's profile below.
- `evidence_rules`: under `reference` and `background`, target 15+ sources per area.
- `sme_hints`: methodology SMEs as the shape needs them (primary-source hunter, literature reviewer, practitioner/empirical, historian, quantitative analyst) plus domain experts for the topic. With a repo source, draw domain experts from what scouts found: language/runtime, frameworks, data stores, protocols, serialization, concurrency/consistency, security, performance, build/supply chain.
- `output`: `kind: document`; path `./understanding-<slug>.md` for `fit`, else `./<slug>.md`. Inline `[n]` for published sources with a numbered Sources list (type, date, accessed) at the end; `[path:line]` for code; `INFERENCE` marked.
- `extra_rules`: the editor keeps `[n]` markers, code citations and the Sources list identical.

## Profiles

**how-it-works**
- Lenses: components and vocabulary; the mechanism end to end (control and data flow, step order); invariants and guarantees; failure modes, edge cases, version and config differences; where the primary sources live (code, spec, reference implementation).
- Roles: the contrarian becomes a **misconception hunter**. It finds what popular docs, blogs, talks and answers get wrong or leave out of date, cites where each misconception appears, and refutes it from a primary source. The adversarial member asks where the explanation breaks: version differences, docs against implementation, edge cases, configs that change behaviour.
- Output: Summary (the mechanism in one paragraph); Model (components and their roles); Walkthrough (numbered steps in execution order, each cited); Invariants and guarantees, and what violates them; Failure modes and edge cases; Version and config differences; Common misconceptions; Open questions; Where to read the source (ordered, with why).

**background**
- Lenses: overview and terminology; history and origins; current state, key players and numbers; academic and primary literature; practitioner and community experience; controversies, failures and open questions.
- Roles: default.
- Output: Summary; Terminology; History (dated); Current state (players, numbers, dates); Debates and controversies (both sides); Contrarian view; Open questions; Further reading (ordered, with why).

**compare**
- Lenses: candidate options and decision criteria; each option's primary docs and source; benchmarks and empirical evidence; practitioner experience and failure reports; cost, licence, maintenance and project health.
- Roles: the contrarian argues for an option not on the list, or for not choosing at all. The adversarial member hunts vendor-funded or cherry-picked benchmarks, stale versions and unlike-for-like comparisons.
- Output: Summary (a recommendation conditional on the criteria); Criteria; Comparison table (every cell cited or `UNKNOWN`); Per-option detail; When each option wins; Contrarian view; Open questions.

**reference**
- Lenses: as `background`.
- Roles: the adversarial member also hunts retractions, conflicts of interest and circular citation.
- Output: title, date, scope and method; Executive summary (cited claims only); one section per area with numbers, dates and short quotes; Contested points; Adversarial findings; Contrarian view.

**fit**
- Lenses (shallow): structure (languages, build, layout, entry points); topic hits (code, config, tests, docs, ADRs, commits); architecture and data flow; history and ownership (`git log`/blame; skip if not git); dependencies and integration edges (if large or polyglot).
- Roles: default.
- Output: Summary; How it fits (per focus area, cited); Design and architecture constraints; External context; Risks and counter-evidence (including the contrarian view); Open questions; Where to start reading (ordered files).
