---
name: teamwork-design
description: Turn an existing specification or set of requirements into candidate designs, ranked by risk, complexity, future relevance, architectural fit, reversibility, operational impact and testability, using a team of subagents (scouts, architects with different stances, domain SMEs, a pre-mortem adversary, a contrarian, verifiers, a judge). Every design traces each spec component it satisfies to the code it changes; every design element and rating is cited. Writes a design document in the project's design-doc format, else a standard design-doc structure, and verifies the format. Use when the user says "teamwork-design", "design this spec", "design options for X", "how should we implement this spec" or "explore approaches to these requirements". Usage - /teamwork-design path/to/spec.md [format instructions]. Not for quick lookups.
---

# teamwork-design

Invoke the `teamwork-core` skill with the parameter block below (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it). This skill only defines the design roles, traceability, ratings and ranking; core owns sources, citation, judging and format.

**The spec comes first.** The user supplies the spec or requirements file (e.g. a `teamwork-spec` output) at invocation, possibly with format instructions and supporting documents (e.g. a `teamwork-code-understanding` output). If no spec path is given, ask once via `AskUserQuestion`, offering up to 4 likely candidates (spec or requirements `.md` files mentioned in the conversation, then under `specs/`, `docs/` or recently modified outside `.teamwork/`) with "Other" for a typed path. Never design from memory or a one-line description. Put each input file's absolute path in `brief.md`; every agent reads them in full. Gaps and contradictions in the spec go to Open questions.

**Spec components.** The requirements scout returns the spec's components: every rule, requirement, scenario or acceptance criterion, as rows `id | location | verbatim quote | mandatory?`. Use the spec's own IDs (`@FEAT-01.R2`, `REQ-3`); where it has none, assign `R1`, `R2`... in document order. `mandatory?` is `yes` for MUST, Gherkin rules and scenarios, and anything unqualified; `no` for SHOULD/MAY. Save the list as `spec-components.md` and include it in `brief.md`.

## Parameter block

- `objective`: candidate designs that satisfy the spec, ranked.
- `slug`: kebab-case name of the spec.
- `pre_questions`:
  1. **Sources**: `repo + web` (default in a code base: the repo is the subject, the web supplies prior art and library docs) / `repo` (no web) / `given` (the input files, what they link, and repo code; nothing else) / `web` (default outside a code base: greenfield).
- `sources`: from pre-question 1. The input files are sources of truth in every mode.
- `scout_lenses` (drop repo lenses without a repo, the prior-art lens without web):
  - requirements: the spec components (above), constraints and non-goals;
  - code the change touches: entry points, extension points, existing mechanisms that already do part of it;
  - architecture, data flow and conventions any design must fit;
  - direction: `git log` on touched areas, ADRs, TODOs, roadmap docs, deprecations in dependencies;
  - prior art: how upstream projects and libraries solve this, with their known failure reports;
  - compatibility and operations: public APIs, persisted formats, migrations, tests and CI that pin behaviour.
- `evidence_rules`: input files are cited as `file §heading Lnn-mm`. A design's `changes` cite the exact `path:line` it modifies or extends. Each `satisfies` row cites the spec component and names the `changes` rows and claim ids that meet it. Ratings are `INFERENCE` claims naming the fact ids they rest on.
- `sme_hints`: domain experts from what scouts found (language/runtime, frameworks, data stores, protocols, concurrency/consistency, security, performance, migration/compatibility). SMEs establish the facts designs depend on; they don't propose designs.
- `mandatory_roles`: **architects**, 2 / 3 / 4 at small / medium / large. Each proposes 1-2 designs from one stance, in order: *minimal change* (smallest diff on existing mechanisms); *architecture-aligned* (idiomatic for this code base's patterns); *forward-looking* (best fit for the evidenced direction); *alternative* (a different technique or library). Architects read the spec, `spec-components.md` and the scout reports. Each writes `architect-<stance>.md` in the **design format** below.
- `role_overrides`:
  - Adversarial: a **pre-mortem**. For each design, assume it shipped and failed: find the code path, concurrency, migration, performance, security or compatibility reason, cited. Attack `satisfies` rows that don't actually meet their component, and ratings that are too kind; a counter-rating is a claim with id `<design id>-<criterion>` plus `targets:`.
  - Contrarian: proposes the design outside the set: reuse an existing mechanism, adopt a library or service, or meet the spec by other means. Same design format. Arguing against the spec itself goes to Open questions, not the ranking.
- `cross_exam`: every `architect-*.md` and `contrarian.md`.
- `judge_bias`: a design is `INCLUDE` only if its changes and the claims it rests on are included; otherwise `EXCLUDE`, unless one claim can be dropped without breaking it. A `satisfies` row whose support fails becomes `unmet`. A rating whose basis is excluded becomes `UNKNOWN`. On a contested rating, take the worse supported rating as `INCLUDE-DISPUTED`. Repo evidence beats generic best practice. Don't penalise a design for being unconventional; penalise it for being uncited.
- Run setting (core stage 2, item 6), **Ranking priority**: `Balanced (Recommended)` / `Lowest risk` / `Simplest` / `Most future-proof`. Record it in `brief.md`.
- **Format question**: like `teamwork-spec`, the design-doc format is confirmed with an `AskUserQuestion` single-select in the same run-settings call (core **Output format**), before any design work starts. With team size, verification, format and ranking priority, run settings fill one call.
- `decision`:
  - `file`: `ranking.md`. The judge merges near-identical included designs (carrying both ids), applies the **ranking rule** to the included ratings and writes one row per design in rank order: `rank | design id | name | one-line approach | unmet mandatory | score | risk | complexity`. It doesn't re-rate.
  - `question`: **Which design should the document propose?** Single-select over the top 4 rows of `ranking.md`, rank 1 first marked `(Recommended)`; label is the design name, description gives score, unmet count, risk, complexity and the approach. "Other" takes a lower-ranked design by name. The pick is the **selected design**.
- `format`:
  - `search`: `docs/design/`, `design/`, `docs/`, `rfcs/`, `adr/`, `proposals/`, existing design docs and RFCs.
  - `default`: a standard design doc (Google-style design doc / RFC structure): title and metadata (status, date, spec link); Context and scope; Goals and non-goals; Proposed design (overview, detailed design: components, APIs, data model, code changes); Requirements traceability; Alternatives considered; Cross-cutting concerns (security, performance, observability, compatibility and migration, testing); Risks; Rollout and rollback; Open questions.
  - `required`: the selected design in full; a traceability table for the selected design, one row per spec component (`component | how satisfied | changes | status: met / unmet`); the ranking table; every other included design with its traceability; the contrarian option; rejected designs; decisions for the user; Sources list.
- `output`: `kind: document`; path per the format, else `./design-<slug>.md`. Content (placed per the format):
  - Summary: the selected design, its rank, and when the top alternative wins instead.
  - Ranking: the priority used, then a table, one row per design in rank order: one column per criterion, `unmet` (count of mandatory components unmet), score. Each cell is a rating with its trace marker, or `UNKNOWN`.
  - Selected design: approach; what changes (cited files); traceability; fit with the existing architecture; pre-mortem findings; rollout, migration and reversibility; prerequisites.
  - Alternatives, in rank order: the same per design, shorter, with traceability and why it ranks where it does.
  - Contrarian option; rejected designs (from Excluded) with the reason; decisions for the user and open questions; where to start reading (ordered files).
  - Inline `[n]` for published sources with a numbered Sources list at the end; `[path:line]` for code; spec components by id.
- `extra_rules`:
  - The synthesiser takes the ranking from `ranking.md` and the selected design from `brief.md` under `Decision`. It doesn't re-rank or re-rate.
  - The editor keeps `[n]` markers, code citations, the Sources list, design ids, spec component ids, ratings, scores, the ranking table and traceability tables identical.
  - **Pre-delivery traceability check.** Every spec component id must appear in the selected design's traceability table. Run from `.teamwork/<slug>/`, with `<final>` the delivered file; it must print nothing:

    ```sh
    cut -d'|' -f1 spec-components.md | tr -d ' ' | grep -v '^$' | while read -r id; do grep -qwF -- "$id" <final> || echo "missing: $id"; done
    ```

    Send misses to the synthesiser (a component no included claim covers becomes an `unmet` row), then re-run the editor and format verification.

## Design format

One block per design; its id `<agent>-d<n>` is the component the judge rules on.

```
design | <id> | <name> | <approach, 3 lines or fewer>
changes | <path:line> | <what changes there>          (one row per touch point)
satisfies | <spec component id> | <how> | <changes rows, claim ids>   (one row per spec component)
unmet | <spec component id> | <why not, or what else is needed>
rests-on | <claim ids>
rating | <id>-<criterion> | Low|Med|High | <why> | <fact ids>   (one row per criterion)
rollout | <migration, flagging, rollback>
prerequisites | <what must exist or be decided first>
```

Every spec component gets a `satisfies` or an `unmet` row. Each `satisfies` and `rating` row is a claim with id `<design id>-<component id>` or `<design id>-<criterion>`, the component id lowercased with every other character replaced by `-` (`@FEAT-01.R2` → `feat-01-r2`) so it fits core's id rule.

## Criteria and ranking rule

| Criterion | Measures | Better |
|---|---|---|
| risk | likelihood × blast radius of failure; security, data and concurrency hazards | Low |
| complexity | size of diff, new concepts, modules touched | Low |
| future | alignment with the evidenced direction; ease of extending; dependency health | High |
| fit | consistency with existing architecture and conventions | High |
| reversibility | how cheaply it can be rolled back or replaced | High |
| ops | runtime cost, performance, observability, on-call burden | Low |
| testability | how directly existing tests and harnesses can cover it | High |

Designs with fewer unmet mandatory components always rank higher. Within the same count, score each included rating 3 (better end), 2 (Med), 1 (worse end); `UNKNOWN` scores 1. Weight every criterion 1, except: `Balanced` risk ×2; `Lowest risk` risk ×3, reversibility ×2; `Simplest` complexity ×3; `Most future-proof` future ×3. Rank by weighted sum; ties go to lower risk, then lower complexity. Show the `unmet` and score columns so the reader can re-rank.
