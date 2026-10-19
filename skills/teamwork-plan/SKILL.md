---
name: teamwork-plan
description: Break an existing design into a delivery plan - a dependency graph (DAG) of steps, each one git commit, scheduled in waves that subagents can run in parallel - using a team of subagents (scouts, planners with different stances, design-breakdown and delivery SMEs, a dependency adversary, a contrarian, verifiers, a judge). Every step cites the design components it delivers and the files it touches; every dependency cites why. The graph is checked mechanically (no cycles, no unordered steps sharing a file) and the recommended subagent count is computed from it. Steps are a TODO checklist; a completed step records its commit SHA. Use when the user says "teamwork-plan", "plan this design", "break this design into steps" or "how do we deliver this design in parallel". Usage - /teamwork-plan path/to/design.md [format instructions]. Not for quick lookups.
---

# teamwork-plan

Invoke the `teamwork-core` skill with the parameter block below (if the Skill tool can't load it, read `../teamwork-core/SKILL.md` relative to this skill's base directory and follow it). This skill only defines the planning roles, the plan format, the graph check and the plan pick; core owns sources, citation, judging and format. It plans; `teamwork-deliver` runs the plan.

**The design comes first.** The user supplies the design file (e.g. a `teamwork-design` output) at invocation, possibly with format instructions and supporting documents (the spec, a `teamwork-code-understanding` output). If no design path is given, ask once via `AskUserQuestion`, offering up to 4 likely candidates (design `.md` files mentioned in the conversation, then under `docs/design/`, `design/`, `docs/`, `rfcs/` or `design-*.md`, recently modified outside `.teamwork/`) with "Other" for a typed path. Never plan from memory or a one-line description. Put each input file's absolute path in `brief.md`; every agent reads them in full. Gaps and contradictions in the design go to Open questions.

**Design components.** The design scout returns the design's components: every change, touch point, traceability row, migration or rollout step and prerequisite, as rows `id | location | verbatim quote`. Use the design's own IDs (spec component ids, change ids); where it has none, assign `D1`, `D2`... in document order. Save the list as `design-components.md` and include it in `brief.md`.

**Graph check.** `plan-graph.py` (Python 3.9+, standard library only) in this skill's base directory checks a plan and schedules it. Pass its absolute path to the judge and use it yourself. It prints `steps N · waves W · recommended subagents K` and the steps in each wave; problems start with `FAIL:`. A wave is a set of steps that can run at once; W is the longest dependency chain; K is the fewest subagents that still finish in W waves, treating steps as equal in length.

## Parameter block

- `objective`: a delivery plan for the design: steps of one commit each, their dependencies, and the parallel schedule.
- `slug`: kebab-case name of the design.
- `pre_questions`:
  1. **Sources**: `repo` (default in a code base: the design and the code it changes) / `repo + web` (adds tool and library docs, e.g. migration tooling) / `given` (default outside a code base: the input files and what they link).
- `sources`: from pre-question 1. The input files are sources of truth in every mode.
- `scout_lenses` (drop repo lenses without a repo):
  - design: the design components (above), its rollout, prerequisites and open questions;
  - code the design touches: the files each change lands in, module boundaries, and shared files (build manifests, lockfiles, registries, generated code) that force ordering;
  - build, test and CI: the test command per module and how to scope it to one test file or class, test layout and naming, slow suites, CI gates;
  - history and conventions: commit message style and size, branch and review workflow, from `git log`, `CONTRIBUTING` and PR templates;
  - rollout and compatibility: migrations, flags, public APIs, persisted formats; what must land before what (expand, then migrate, then contract).
- `evidence_rules`: input files are cited as `file §heading Lnn-mm`. A step's `touches` rows cite the `path:line` it changes, or the directory a new file goes in. Each `after` row is a claim that names why the order is forced: a symbol, schema, flag or file the earlier step creates, cited. A `gate` cites where its command comes from (CI config, Makefile, `CONTRIBUTING`); a `tests` row cites the existing test it extends, or the test directory and naming convention a new test follows.
- `sme_hints`: two groups. **Design breakdown**: experts in what the design changes (language/runtime, frameworks, build system, data stores and migrations, API compatibility), who establish which changes depend on which. **Delivery**: release engineering and CI, git workflow and merge conflicts, test strategy, rollout and feature flags, who establish what makes a commit safe on its own and what can run in parallel. SMEs establish facts; they don't propose plans.
- `mandatory_roles`: **planners**, 2 / 3 / 3 at small / medium / large. Each proposes one plan from one stance, in order: *parallel-first* (shortest dependency chain, most steps at once); *safe-increments* (every commit builds, passes tests and reverts on its own; expand before contract); *vertical slices* (each step delivers one design component end to end). Planners read the design, `design-components.md` and the scout reports. Each writes `planner-<stance>.md` in the **plan format** below and runs `plan-graph.py ledger` on its own plan until it prints no `FAIL:`.
- `role_overrides`:
  - Adversarial: a **dependency audit**. For each plan, find the missing edge (a step uses what a step not before it creates; two steps touch one file unordered), the false edge (an order nothing forces, which costs parallelism), the step that leaves the build red or isn't one coherent commit, the step whose gate doesn't run a test that exercises its change, and the design component no step delivers. A missing or false edge is a claim with id `<step id>-after-<n>` plus `targets:`.
  - Contrarian: proposes the plan outside the set: a different cut (fewer larger steps, a spike or scaffold first, a flag that lets everything land in parallel). Same plan format.
- `cross_exam`: every `planner-*.md` and `contrarian.md`.
- `judge_bias`: a step is `INCLUDE` only if its `touches`, `tests` and `gate` are supported, its gate runs tests that exercise its change, and it is one commit that leaves the build green. A plan is `INCLUDE` only if every step it needs is included, unless a step can be dropped or one edge fixes it. A surviving missing-edge finding adds that edge; a surviving false-edge finding removes it. A component no included step delivers is `uncovered`. Repo evidence beats generic practice; when unsure whether an order is forced, keep the edge (lost parallelism is cheaper than a broken build).
- **Format question**: the plan format is confirmed with an `AskUserQuestion` single-select in the run-settings call (core **Output format**), before any planning starts.
- `decision`:
  - `file`: `plans.md`. For each included plan, the judge writes `.teamwork/<slug>/plans/<plan id>.md`: the plan's included rows in plan format, with edges added or removed by surviving findings, then each change and its reason. It runs `plan-graph.py ledger` on that file, which must print no `FAIL:`. It then writes `plans.md`, one row per included plan in rank order: `# | plan | approach (one line) | uncovered | steps | waves | subagents | plan id`. Rank by fewest uncovered components, then fewest waves, then fewest subagents.
  - `question`: if only one plan is included, skip the question; it is the selected plan. Otherwise print the `plans.md` table in the chat as is, then one line per plan in rank order: rank, plan name and the absolute path of its `plans/<plan id>.md` as a link. Then ask **Which plan should the document lay out?** Single-select over the top 4 rows, rank 1 first marked `(Recommended)`; label is the plan name, description gives waves, subagents, steps, uncovered count and the approach. "Other" takes a lower-ranked plan by name. The pick is the **selected plan**. Run `plan-graph.py ledger` on its file and save the output as `schedule.md`.
- `format`:
  - `search`: `docs/plans/`, `plans/`, `docs/`, existing plans, roadmaps and TODO documents.
  - `default`: the **plan document** below.
  - `required`: the `Waves:` line and every step in the step block layout below.
- `output`: `kind: document`; path per the format, else `./plan-<slug>.md`. Content (placed per the format):
  - The plan is the TODO list, nothing more: a title, the design file it plans, the line `Waves: W · Recommended subagents: K` from `schedule.md`, then the checklist below in wave order.
  - Only if there are any: a **Not covered** list (uncovered design components with why, and open questions), and a numbered Sources list for `[n]` citations.
  - Core's Excluded digest and Gaps sections are not written; gaps go under Not covered.
- `extra_rules`:
  - The synthesiser lays out the selected plan from its `plans/<plan id>.md` and `schedule.md`. It renumbers steps `S1`, `S2`... in wave order and doesn't add, drop, merge or reorder steps or edges.
  - The editor keeps every step line, step field line, the `Waves:` line, step ids, design component ids and code citations identical. Protected tokens: every line matching `^- \[[ xX]\] \*\*S[0-9]+|^[ \t]+- (Wave|Depends on|Design|Touches|Do|Tests|Gate|Message|Commit):|^Waves:`.
  - **Pre-delivery checks.** Run from `.teamwork/<slug>/`, with `<final>` the delivered file and `<skill>` this skill's base directory; both must print nothing:

    ```sh
    python3 <skill>/plan-graph.py doc <final> | grep FAIL
    cut -d'|' -f1 design-components.md | tr -d ' ' | grep -v '^$' | while read -r id; do grep -qwF -- "$id" <final> || echo "missing: $id"; done
    ```

    Send failures to the synthesiser (a component no included step covers goes under Not covered), then re-run the editor and format verification.

## Plan format

One block per plan; its id `<agent>-p<n>` and each step id `<plan id>-s<n>` are components the judge rules on.

```
plan | <id> | <name> | <approach, 3 lines or fewer>
step | <plan id>-s<n> | <title> | <design component ids> | <what changes, 2 lines or fewer>
touches | <step id> | <path:line, or directory for a new file>   (one row per file)
after | <step id> | <step id it waits for> | <why> | <claim ids>   (one row per dependency)
tests | <step id> | <test path> | <added or changed: what it checks>   (one row per test file)
gate | <step id> | <test command that must pass before the commit>
message | <step id> | <commit message subject, in the project's style>
uncovered | <design component id> | <why no step delivers it>
```

Each step is exactly one commit: coherent on its own, leaving the build and tests green. **Testing gates every change**: the commit carries the tests for its change (new or updated; a step that changes no behaviour, e.g. a pure refactor, names the existing tests that cover it), and its gate runs those tests and must pass before the commit is made. A gate is a concrete command scoped to the change, not "run CI". Steps that touch the same file must be ordered by a chain of `after` rows. Each `after` row is a claim with id `<step id>-after-<n>`.

## Plan document

Each step is a checklist item in this layout, field names exact:

```
- [ ] **S3 · <title>**
  - Wave: 2                       (from schedule.md)
  - Depends on: S1, S2            (or: none)
  - Design: <design component ids>
  - Touches: `path/a`, `path/b`
  - Do: <what to change, with code citations>
  - Tests: `path/to/test` (added: what it checks), …
  - Gate: `<test command>` passes before committing
  - Message: `<commit message subject>`
  - Commit: —
```

`Waves:` and each step's `Wave:` are the parallelism hint: steps in the same wave can run at once, one subagent each; a wave starts once the waves before it are done. A completed step is ticked, `- [x]`, and its `Commit:` holds the SHA it landed as.
