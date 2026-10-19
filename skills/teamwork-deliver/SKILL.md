---
name: teamwork-deliver
description: Run a teamwork-plan delivery plan - each step implemented by its own subagent in a git worktree, wave by wave in parallel, gated by its test command, checked mechanically (files touched stay within the step, the gate passes, new tests fail without the change) and optionally reviewed, then cherry-picked as one commit onto a deliver/<slug> branch with a Plan-Step trailer. After each wave, a commit on that branch ticks the plan with each landed step's SHA; a re-run resumes from the trailers in git history. A step that fails twice is blocked with its dependents; independent steps continue. Never touches your checkout, never pushes. Use when the user says "teamwork-deliver", "deliver this plan", "run the plan" or "execute the plan". Usage - /teamwork-deliver path/to/plan.md.
---

# teamwork-deliver

Runs a plan written by `teamwork-plan`. It does not plan, re-judge or reorder: the plan's steps, edges, gates and messages are taken as written. It is not a `teamwork-core` wrapper (core's stages produce cited claims; this runs a judged plan), but it follows core's **Orchestration rules**, **Models** table and scratch-dir rule (core stage 0). If the Skill tool can't load core, read `../teamwork-core/SKILL.md` relative to this skill's base directory for those sections.

**The plan comes first.** The user supplies the plan file at invocation. If none is given, ask once via `AskUserQuestion`, offering up to 4 candidates (plan `.md` files mentioned in the conversation, then `plan-*.md`, `docs/plans/`, `plans/`) with "Other" for a typed path. Needs a git repo, and the plan must be inside it; otherwise say so and stop.

**Writes to the user's world, narrowly.** The only exception to read-only: commits go on `deliver/<slug>` via worktrees under `.teamwork/<slug>/wt/`; the checkout's own branch and working tree are never touched. Only commands the user approved in stage 1 are run. Never push, never run code from an upstream clone.

Paths below: `<skill>` is this skill's base directory, `<plan>` the plan's absolute path, `<run>` the absolute path of `.teamwork/<slug>/`, `<int>` = `<run>/wt/integrate`, `<wt>` = `<run>/wt/<step>`, `<rel>` the plan's path relative to the repo root.

**Git is the record.** Each step commit carries the trailer `Plan-Step: <slug>/<step>`; trailers survive cherry-pick, rebase and GitHub's default squash message. A step is done when its trailer is in the branch's history. The ticked plan on `deliver/<slug>` is a view of that, committed once per wave; a commit can't hold its own SHA, so ticks always land in a later commit.

## Stage 0: Load

1. `slug`: the plan file's basename without `plan-` and `.md`. Make `<run>` per core stage 0.
2. Branch. If `deliver/<slug>` exists, resume on it; otherwise `git branch deliver/<slug> HEAD`. Then `git worktree add <int> deliver/<slug>`. If `<int>/<rel>` doesn't exist (the plan isn't committed), copy `<plan>` there; the first tick commit adds it. From here, the plan is `<int>/<rel>`.
3. `python3 <skill>/../teamwork-plan/plan-graph.py doc <int>/<rel>` must print no `FAIL:`. If it does, show the failures and stop: the plan needs fixing in `teamwork-plan`, not here. Save its output as `<run>/schedule.md`.
4. Done steps: `git -C <int> log --format='%(trailers:key=Plan-Step,valueonly)' | grep "^<slug>/"`. A ticked step with no trailer: stop and name it. A trailer whose step isn't ticked (a run stopped mid-wave): tick it with that commit's SHA in the first tick commit. Steps merged to `main` earlier count as done too, since `HEAD`'s history carries their trailers.
5. Spawn one `Explore` setup scout (`sonnet`). It reads `CONTRIBUTING`, `README`, CI config, `Makefile`, lockfiles and returns the command a fresh checkout needs before tests run (e.g. `npm ci`, `uv sync`), with its `path:line`, or `none`. Save as `<run>/setup.md`.

## Stage 1: Run settings

One `AskUserQuestion` call:

1. **Commands**: the question text lists the setup command and every distinct `Gate:` command verbatim. `Run these (Recommended)` / `Stop`. "Other" lets the user correct a command; use what they type.
2. **Parallelism**: `K subagents (Recommended)` with K from `schedule.md` / `1 (serial)`. Each parallel step costs one worktree and one setup run.
3. **Review**: `Per step (Recommended)`: a reviewer reads each diff against the step and design; one extra `opus` call per step. / `Gate only`: mechanical checks only.
4. **Red-green**: `On (Recommended)`: a step that changes test files must fail its gate without its non-test changes, proving the tests exercise it; one extra gate run per step. / `Off`.

If `git status --porcelain` in the checkout is non-empty, say in the Commands question that uncommitted changes are not part of `HEAD` and won't be delivered. Write the answers, `<int>/<rel>`, the design path the plan names and `deliver/<slug>` to `<run>/brief.md`.

## Stage 2: Waves

For each wave in `schedule.md`, skipping ticked and blocked steps, run up to K steps at a time. Announce each wave in one line (`Wave 2/4 · S3 S4 S5 implementing`) and its outcome in one (`Wave 2/4 · 2 landed, 1 blocked (S5: gate)`).

**Per step** (steps of a wave in parallel):

1. `git worktree add -b tw/<slug>/<step> <wt> deliver/<slug>`, then run the setup command in `<wt>`. Write `<wt>/../<step>-allowed.txt`: every backticked path on the step's `Touches:` and `Tests:` lines, `:line` suffixes and trailing `/` stripped, one per line.
2. Spawn an implementer (`general-purpose`, `opus`). Its prompt carries the step block verbatim, the design path, `<wt>`, the gate command, its notes path `<run>/impl-<step>.md`, and these rules verbatim:
   - Edit only inside `<wt>`, only the files in `<step>-allowed.txt` (a directory entry allows new files under it). If the step can't be done within them, change nothing and say why.
   - Do what the step's `Do:` says, for the design components on its `Design:` line, and write or update the tests on its `Tests:` line.
   - The only command you may run is the gate command, in `<wt>`. Don't commit, push, install or run anything else.
   - Write to your notes file: each change with `path:line`, and any departure from `Do:` with its reason. Return the notes path and a summary of 5 lines or fewer.
3. **Checks**, run by you in `<wt>`; all must hold:

   ```sh
   # scope: prints nothing
   git status --porcelain=v1 -uall --no-renames | cut -c4- | while read -r p; do
     awk -v p="$p" '$0==p || index(p, $0"/")==1 {f=1} END {exit !f}' ../<step>-allowed.txt || echo "out of scope: $p"
   done
   # gate: exits 0
   <gate command>
   ```

   Red-green, if on and the diff changes both a file on the `Tests:` line and a file not on it: stash the non-test changes, run the gate, expect a non-zero exit, restore.

   ```sh
   git stash push -u -- $(git status --porcelain=v1 -uall --no-renames | cut -c4- | grep -vxF -f <tests.txt>)
   <gate command>; echo "exit $?"     # must be non-zero
   git stash pop
   ```

   `<tests.txt>` holds the `Tests:` paths only. Write each check's command and output to `<run>/checks-<step>.md`.
4. **Review**, if on: spawn a reviewer (`general-purpose`, `opus`) with the step block, the design path, `git -C <wt> diff HEAD` saved as `<run>/diff-<step>.patch`, and the notes file. It writes `<run>/review-<step>.md` with rows `id | path:line | finding | citation in plan or design | blocking yes/no`, where blocking means the diff doesn't do the step, breaks a design component, or its tests don't exercise the change. Every finding cites; no citation, no finding. Returns the path and its blocking count.
5. **Commit**: `git -C <wt> add -A && git -C <wt> commit -m "<Message: subject>" -m "Plan-Step: <slug>/<step>"`.

**Integrate**, after the wave's steps finish, in step order: `git -C <int> cherry-pick tw/<slug>/<step>`, then run that step's gate in `<int>` (run setup there first, once per run). On success, tick the step in `<int>/<rel>` (`- [ ]` → `- [x]`, `Commit: —` → `Commit: <git -C <int> rev-parse HEAD>`), then `git worktree remove <wt>` and `git branch -D tw/<slug>/<step>`. After the wave, if anything was ticked: `git -C <int> add <rel> && git -C <int> commit -m "plan: mark <step ids> delivered"`. This commit touches only the plan, so it needs no gate.

**Failure.** A failed check, blocking review finding, conflicting cherry-pick (`git -C <int> cherry-pick --abort`) or failed integrated gate goes back to the implementer once by `SendMessage`, with the failing output or findings; for an integration failure, first `git -C <wt> rebase deliver/<slug> && git -C <wt> reset --soft HEAD~1` (if the rebase conflicts, `rebase --abort` and block the step). Re-run steps 3-5 and integration for that step. A second failure **blocks** the step: record `step | reason | file` in `<run>/blocked.md`, block every step that depends on it, transitively, and leave its worktree for inspection. Independent steps continue.

## Stage 3: Final check

Run every landed step's gate once more in `<int>`, in step order; record failures in `<run>/final-gates.md`. Don't fix them. Then `python3 <skill>/../teamwork-plan/plan-graph.py doc <int>/<rel>` must print no `FAIL:`. Remove `<int>` (`git worktree remove <int>`); the branch stays.

## Delivery

Write `<run>/delivery.md`: one row per step, `step | title | landed / blocked / skipped | SHA or reason`. Tell the user, in a few lines:

- the branch `deliver/<slug>` and how many steps landed, blocked and remain;
- each blocked step with its one-line reason and the worktree left for it;
- any final gate that failed;
- that the plan on the branch is ticked, re-running resumes, and `<run>` holds the notes, checks, reviews and diffs;
- that a rebase merge keeps one commit per step; a rebase or squash makes the plan's SHAs stale, but the `Plan-Step` trailers still say which step landed where.

Don't push, open a PR or merge; say the branch is ready for the user to review.
