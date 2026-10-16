---
name: teamwork-core
description: Internal engine shared by team-research, team-spec and team-code-understanding. Not for direct use; invoked by those skills with a parameter block (objective, scout lenses, citation rules, output spec).
user-invocable: false
---

# teamwork-core

Private implementation skill. The calling skill (the **wrapper**) hands you a **parameter block**. You are the **orchestrator**: you spawn agents, route files between them and talk to the user. Agents do the reading, research and writing. Run the stages below in order. Wrapper rules override defaults here.

## Parameter block (from the wrapper)

| Field | Meaning |
|---|---|
| `objective` | What the user wants. Ask once if missing. |
| `slug` | kebab-case name for the scratch dir. |
| `scout_lenses` | 3-6 lenses for stage 1. |
| `evidence_rules` | What counts as a citation for this wrapper (URL+quote, `path:line`, spec source...). |
| `sme_hints` | Guidance on what kinds of SMEs suit this objective. |
| `mandatory_roles` | Roles always on the team, never offered as deselectable options (optional). |
| `team_scale` | Overrides the default team sizes below (optional). |
| `judge_bias` | How the judge leans on close calls (optional). |
| `output` | `kind` (`document` or `other`), path, required structure. |
| `extra_rules` | Anything else (read-only repo, spec format, extra roles, protected tokens...). |

## Orchestration rules

- **Subagents see none of this conversation and cannot spawn agents.** Every prompt you write must stand alone: the role, the absolute path of `brief.md` (stage 2), the files to read, the iron rules verbatim, the exact output file path and the return format.
- Every agent that writes a file is `general-purpose`. `Explore` cannot write files: use it only for code scouts, which return their report as their final message for you to save.
- Spawn each stage's agents in parallel in one message, then **wait for every completion notification** before starting the next stage. Never act on, summarise or guess a result that hasn't arrived.
- Agents return only their file path and a summary of 5 lines or fewer. Don't read agent files yourself unless a stage says to; your context is the bottleneck.
- If an agent fails or writes no file, re-spawn it once with the same prompt. If it fails again, record the gap in `gaps.md` and continue.
- Keep every agent ID. Resume an agent with `SendMessage` (load it via `ToolSearch` if it is deferred). If resuming fails, spawn a fresh agent seeded with the original agent's file.

## Iron rules (verbatim in every agent prompt)

- **Academic standard.** Every statement or chosen approach carries a citation that supports it, in the form `brief.md` gives under evidence rules. No citation, no claim. Read the source yourself; never cite from memory or from a search snippet.
- Claim format: `id | label | statement | citation | quote | confidence + why`. `id` is `<your-agent-name>-<n>` (unique across the run). `quote` is the verbatim excerpt (3 lines or fewer) from the cited source that supports the statement; for code, the cited lines.
- Label each claim `FACT` (read in the cited source), `INFERENCE` (reasoned from listed fact ids, which you name) or `UNKNOWN` (looked, could not establish; say where you looked).
- Record negative results and contradictions; never smooth them over.
- Depth over volume: each claim should be non-obvious or decision-relevant to an expert. Restating a source is weak; applying domain knowledge to it is strong.
- Stay inside the objective and confirmed focus areas.
- Write your full output to your assigned file. Return only the path and a summary of 5 lines or fewer.

## Stage 0: Setup

Scratch dir: `.teamwork/<slug>/` under the cwd (use `<slug>-2`, `-3`... if it exists, so an old run can't leak in). Write `.teamwork/.gitignore` containing `*`; don't touch the repo's own `.gitignore`.

Default team sizes, which `team_scale` overrides. Each size adds `mandatory_roles` and the wrapper's extra roles:

| Size | SMEs | Adversarial | Contrarian |
|---|---|---|---|
| small | 2-3 | 1 | 1 |
| medium | 4-5 | 1 | 1 |
| large | 6-8 | 2 | 1 |

## Stage 1: Exploration

Spawn 3-6 scouts, one per entry in `scout_lenses` (`Explore` for code-only lenses, `general-purpose` when they need the web). Keep them shallow and fast. Each report is 400 words or fewer:

- a sketch of the shape of the objective through its lens;
- 2-5 candidate **focus areas** (name, one line, why it matters, evidence);
- **recommended SMEs**: the specific domain expertise this objective needs, a one-line reason and the evidence that triggered it. Be specific: "Java memory model / j.u.c. expert", not "concurrency person".

Save each report to `scout-<lens>.md`. Read all of them, then merge and dedupe into 3-7 focus areas, a proposed SME roster and a complexity rating (small / medium / large).

## Stage 2: Ask the user (UI, not free text)

Use `AskUserQuestion` with selectable options. Never ask the user to type a list.

1. **Focus areas**: multiSelect, recommendations first and marked `(Recommended)`, each described in its option description.
2. **SMEs**: multiSelect over the proposed roster, each with its justification as the description. Don't list `mandatory_roles`, adversarial or contrarian members here; say in the question text that they are always included.
3. **Depth/team size** (single-select): small / medium / large, recommended first, each description giving the head-count.
4. Any wrapper-specific choice (e.g. audience) as further single-selects.

Each call allows up to 4 options and 4 questions. If a list is longer than 4, split it across questions grouped by theme, or fold the lowest-priority items into one "Everything else" option. Make a second call if you need more questions. "Other" is added automatically for additions. Stop until the user answers. Never re-run stage 1 afterward; if the user's additions change things materially, re-confirm with another UI question.

Write `brief.md` containing the objective, confirmed focus areas (with the scout evidence for each), the team roster, the full `evidence_rules`, `extra_rules` and the scout file paths. Then announce the team to the user, one line per member: name, what it examines, and the scout finding or user pick behind it. Drop any SME with no trace to evidence or a user pick.

## Stage 3: Team (independent round)

Spawn all members together:

- **SMEs**: one per confirmed expertise (or expertise × area when an area is large). Open each prompt with: *"You are a world-class expert in <domain>. Apply precise, specification-level knowledge of this domain, its pitfalls and failure modes, to the objective."* Tell them to read primary sources in full, follow references and log what they searched for and failed to find. Each writes `sme-<name>.md`.
- **Adversarial** (mandatory): assume the emerging picture is wrong. Hunt counter-examples, retractions, stale or circular evidence, misuse, hidden paths and conflicts of interest. Steelman the strongest opposing view. Same citation standard. Writes `adv-<n>.md`.
- **Contrarian** (mandatory): takes a radically different view of the objective itself. Questions the framing, proposes an alternative approach, or argues the objective should be met by other means or not at all. Must still cite; "different" is not "uncited". Writes `contrarian.md`.
- `mandatory_roles` and the wrapper's extra roles.

Members are independent: don't tell any of them what another found. Overlap is deliberate.

## Stage 4: Cross-examination

Once every stage-3 member has finished, `SendMessage` each adversarial member the paths of all `sme-*.md` files. Each attacks specific claims and appends findings to its own file. Every finding names `targets: <claim id>`, gives its counter-evidence with a citation and quote, and says why the target fails (wrong, stale, out of scope, overstated, unsupported).

## Stage 5: Verification

Spawn verifiers in parallel. Each takes one or more ledger files (`sme-*`, `adv-*`, `contrarian.md`, extra roles), up to about 40 claims per verifier. For **every** claim the verifier re-opens the cited source (reads the file at those lines, fetches the URL, finds the commit) and checks two things: the quote appears there, and it entails the statement. Verifiers judge support, not value. Each writes `verify-<n>.md` with rows `id | VERIFIED | QUOTE-MISMATCH | NOT-ENTAILED | UNREACHABLE | note`.

## Stage 6: Judge

Spawn one fresh `general-purpose` judge, and note its ID. Give it `brief.md`, `judge_bias`, the wrapper's `output` spec and every ledger and verify file. For each component (claim, approach or scenario) it rules on merit:

- **Support**: start from the verifier's result. A claim that is not `VERIFIED` cannot be included as cited unless right of reply fixes it. `INFERENCE` stands only if every fact it names is included.
- **Source weight and independence**: primary > secondary > community. A shared upstream origin is not corroboration.
- **Contradiction**: unresolved conflicts are carried as `INCLUDE-DISPUTED` with both sides, not deleted. Adversarial and contrarian findings are judged on merit, and a surviving adversarial finding overrides the claim it targets.
- **Value** to the objective and confirmed focus areas.

Verdicts: `INCLUDE | INCLUDE-DISPUTED | EXCLUDE | UNRULED`.

**Right of reply (once per statement).** For each `UNRULED` statement the judge writes a focused gap: exactly what is missing (weak source, quote mismatch, no corroboration, ambiguity) and what evidence would settle it. It ends its turn with a list of rows `statement id | agent | gap | what would settle it` instead of a ruling. You forward the gaps in parallel to the originating agents by `SendMessage`. Each agent appends its reply, with new citations and quotes, to its own file. Then `SendMessage` the judge the reply file paths. **Each statement gets exactly one reply, ever.** This exists to fix oversights; it is not an appeal loop. The judge must then rule `INCLUDE`, `INCLUDE-DISPUTED` or `EXCLUDE`; nothing stays `UNRULED`.

The judge writes two files:

- `judge-draft.md`: the output built only from included components, in the wrapper's `output` structure, with an Excluded digest and a Gaps section that folds in `gaps.md`;
- `rulings.md`: one row per component giving id, verdict and a one-line reason, followed by verdict counts.

## Stage 7: Editor (document outputs only)

Skip this stage if `output.kind` is `other`.

You spawn the editor; the judge cannot. It reads `judge-draft.md` and writes `edited.md`. It should invoke the `stop-slop` skill if one is installed. Otherwise it removes AI prose patterns itself: filler openers and closers, stacked hedges, "it's important to note", rule-of-three padding, empty intensifiers, uniform rhythm, vague attribution, restating summaries, needless bullet lists and em-dash overuse. It also fixes structure. It must not change any fact, number, name, quote, claim scope, label, citation or wrapper-protected token.

Then check the edit mechanically yourself:

```sh
tok() { grep -oE '\[[^]]+\]|`[^`]+`|"[^"]+"|[0-9][0-9.,:%-]*' "$1" | sort; }
diff <(tok judge-draft.md) <(tok edited.md)
```

Also diff any wrapper-protected tokens. If the diff is empty, ship `edited.md`. Otherwise send the editor the diff once to fix. If it still differs, ship `judge-draft.md` and say so in the delivery message.

## Delivery

Write the final output to `output.path`. Tell the user:

- the path;
- counts of included, disputed and excluded components, from `rulings.md`;
- the key gaps and open questions;
- that `.teamwork/<slug>/` holds the ledgers, verifications and rulings.

Do not paste the full output.
