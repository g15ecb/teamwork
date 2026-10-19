# AGENTS.md

Guidance for agents editing this repo. The repo ships [skills.sh](https://skills.sh) skills; each lives at `skills/<name>/SKILL.md` and is installed with `npx skills add g15ecb/teamwork`.

## Layout

- `skills/teamwork-core/` is the engine: stages, roles, source modes, citation, judging, synthesis and editing rules. It is `user-invocable: false`.
- `skills/teamwork-*` (everything else) are wrappers. A wrapper builds a parameter block and invokes `teamwork-core`. Nothing more.

## Guiding principles

1. **One home per rule.** A rule shared by more than one wrapper belongs in `teamwork-core`. A wrapper only fills in the parameter block (`objective`, `sources`, `scout_lenses`, `output`, `extra_rules`...) and never restates or forks core behaviour. If a wrapper needs new behaviour, add a parameter to core rather than copying a stage.
2. **Wrappers stay thin.** If a wrapper is just another wrapper with preselected answers, make it an alias (see `teamwork-code-understanding`).
3. **Evidence over assertion.** The skills enforce citation, verification and judging. Don't add a stage or role that lets an uncited claim reach the output, and don't weaken the iron rules to save tokens; make the expensive path a user choice instead (see citation verification).
4. **Mechanical checks beat trust.** Where an agent's output can be checked with a shell one-liner (trace markers, editor token diff), check it that way. Keep those snippets runnable and POSIX-ish.
5. **Subagent prompts stand alone.** Subagents see no conversation. Any rule an agent must follow is passed to it verbatim, with absolute paths and an exact return format.
6. **The orchestrator's context is the bottleneck.** Agents write to files under `.teamwork/<slug>/` and return a path plus 5 lines or fewer. Don't add steps that have the orchestrator read ledgers wholesale.
7. **Every user decision point is UI-based.** Any choice the user makes (scope, team, run settings, sources, format, confirmations) is an `AskUserQuestion` prompt with selectable options, never a request to type a reply or a list. Infer the options, put the recommended one first marked `(Recommended)`, and describe what each means and costs. Free text only via the automatic "Other", even when options are hard to infer: offer best guesses and let "Other" take the typed answer. Never ask what a sensible default answers. A new skill or stage that needs a user decision must add it as a UI question.
8. **Focus on user ergonomics.** Respect the user's time and attention. Ask as few times as possible: bundle questions into one call, preselect what can be inferred, and use good defaults instead of asking. Invocation should be one line (`teamwork-research: <topic>`). Say what's happening at each stage in a line or two, and keep the delivery message short: path, counts, key gaps. Never dump the full output or the ledgers into the chat. When a change makes a skill more rigorous but more tedious to use, find a way to keep the rigour without the tedium, or make it a user choice.
9. **Read-only on the user's world.** Agents never modify the user's repo outside `.teamwork/` and never run builds, scripts, tests or hooks from cloned upstream code. The one exception is `teamwork-deliver`: it commits only to its own `deliver/<slug>` branch through worktrees under `.teamwork/`, never touches the user's checkout, runs only commands the user approved, and never pushes.
10. **Every subagent has a prescribed model.** A new role gets a row in `teamwork-core`'s **Models** table, picked for its job: `opus` for judgment (expert analysis, attack, ruling, synthesis), `sonnet` for shallow or mechanical work (scouting, fetching, verification, editing). No role inherits the session model by omission.
11. **Documents are for humans.** Every output document follows `teamwork-core`'s **Write for a human reader** rules: answer first, plain words, explanation over lists, no run machinery (ids, verdicts, roles) in the prose. Don't add a wrapper output rule that pushes pipeline jargon into the document.
12. **Terse, plain prose.** Skill files are instructions for a model. Short imperative sentences, tables for structured fields, no filler. Run new prose past `stop-slop` if it's installed.

## When you change something

- Update the README skill table and install notes if a skill is added, renamed or changes its invocation.
- Keep the README **Models** table in sync with `teamwork-core`'s **Models** table. A new role gets a row in both.
- Keep each `SKILL.md` frontmatter `description` accurate: it's what triggers the skill.
- A rename touches every wrapper that names the skill and any relative fallback path (`../<skill>/SKILL.md`).
