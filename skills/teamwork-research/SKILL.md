---
name: teamwork-research
description: Exhaustive, adversarially-tested, fully-cited research into any topic using a team of subagents (scouts, SMEs, adversarial and contrarian members, a judge, an anti-slop editor). Produces a verbose markdown reference document (SLUG.md). Use when the user says "teamwork-research", "research X exhaustively", "deep research on X", or wants rigorous, source-cited research rather than a quick answer. Not for quick lookups.
---

# teamwork-research

Invoke the `teamwork-core` skill with this parameter block (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it). The objective is the user's topic.

- `objective`: the topic. If ambiguous, ask once via `AskUserQuestion` single-selects with inferred options: scope (narrow/broad readings of the topic), time horizon (e.g. last 2 years / last decade / full history), audience (practitioner / researcher / executive).
- `slug`: kebab-case topic.
- `scout_lenses`: overview and terminology; history and origins; current state, key players and numbers; academic/primary literature; practitioner and community experience; controversies, failures, open questions. Scouts are `general-purpose` (web).
- `evidence_rules`: citation = URL / DOI / book+page, a short **verbatim quote**, source type (`primary | peer-reviewed | official-docs | reputable-secondary | practitioner | community | unknown`), date, access date. Sources must be fetched, not taken from snippets. Prefer primary sources. Target 15+ sources per area.
- `sme_hints`: methodology and domain SMEs, e.g. primary-source hunter, literature reviewer, practitioner/empirical, historian, quantitative analyst, plus subject-matter experts for the topic itself. Adversarial member hunts counter-evidence, retractions, conflicts of interest, circular citation.
- `output`: `kind: document`; path `./SLUG.md`; structure: title/date/scope/method; executive summary (only cited claims); one section per area with inline `[n]` citations, numbers, dates, short quotes; contested points; adversarial findings; contrarian view; gaps and unknowns; excluded-claims digest; numbered Sources (type, date, accessed).
- `extra_rules`: none. Editor must keep `[n]` markers and Sources list identical.
