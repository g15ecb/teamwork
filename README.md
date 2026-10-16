# teamwork

Skills for [skills.sh](https://skills.sh) that run a team of subagents against an objective: scouts explore, you pick focus areas and experts from a UI prompt, cited SMEs plus an adversarial and a contrarian member do the work, adversaries cross-examine the SMEs' claims, verifiers re-check every citation, a judge rules (one right of reply per questionable statement), and an editor de-slops document outputs.

## Install

```
npx skills add g15ecb/teamwork
```

Installs all four skills.

**You must always install `teamwork-core`.** `team-research`, `team-spec` and `team-code-understanding` are thin wrappers that call it and do nothing without it. If you install skills selectively, include it:

```
npx skills add g15ecb/teamwork --skill teamwork-core --skill team-research
```

## Skills

| Skill | Use |
|---|---|
| `team-research` | `team-research: <topic>` writes `SLUG.md` |
| `team-spec` | `/team-spec path/to/context.md` writes a spec |
| `team-code-understanding` | `team-code-understanding: <topic>` writes `understanding-SLUG.md` |
| `teamwork-core` | Private engine (`user-invocable: false`); the three above call it with a parameter block |

Scratch ledgers and rulings live in `.teamwork/<slug>/`.
