---
name: teamwork-core
description: Internal engine shared by the teamwork-* skills. Owns the framework (stages, roles, source modes, citation and judging rules, synthesis, editing). Not for direct use; wrappers invoke it with a parameter block (objective, sources, scout lenses, output spec).
user-invocable: false
---

# teamwork-core

Private implementation skill. The calling skill (the **wrapper**) hands you a **parameter block**. You are the **orchestrator**: you spawn agents, route files between them and talk to the user. Agents do the reading, research and writing. Run the stages below in order. Wrapper rules override defaults here.

## Parameter block (from the wrapper)

| Field | Meaning |
|---|---|
| `objective` | What the user wants. If missing, ask once (see the user-input rule). |
| `slug` | kebab-case name for the scratch dir. |
| `pre_questions` | Questions whose answers the scout lenses depend on (e.g. sources, shape), with inferred options. Asked in stage 0 unless the caller preselected the answer (optional). |
| `sources` | A source mode from **Sources** below, or a `pre_questions` entry that picks one. |
| `scout_lenses` | 3-6 lenses for stage 1. |
| `evidence_rules` | Rules on top of the source mode's citation rules (optional). |
| `sme_hints` | Guidance on what kinds of SMEs suit this objective. |
| `mandatory_roles` | Roles always on the team, never offered as deselectable options (optional). |
| `role_overrides` | Replaces or refocuses the default adversarial or contrarian brief (optional). |
| `team_scale` | Overrides the default team sizes below (optional). |
| `judge_bias` | How the judge leans on close calls (optional). |
| `output` | `kind` (`document` or `other`), path, required structure. |
| `extra_rules` | Anything else (spec format, extra roles, protected tokens...). |

## Sources

The source mode decides where evidence may come from, how it is cited and which agents gather it. Copy the chosen mode's rules, the upstream-code rule if it applies, and the weighting into `brief.md` as the evidence rules, followed by the wrapper's `evidence_rules`.

- **`web`**: published sources. Citation: URL, DOI or book+page; a verbatim quote; source type (`primary | peer-reviewed | official-docs | reputable-secondary | practitioner | community | unknown`); date; access date. Fetch the source; never cite a search snippet. Scouts are `general-purpose`.
- **`repo`**: the code base in the cwd. If the cwd is not a code base, say so and stop. Citation: `path:line`, `path:start-end` or a commit SHA. Every agent is read-only on the repo and writes only inside `.teamwork/`. Scouts are `Explore`. Experts apply domain rules to the code (e.g. happens-before edges for a shared field); claims that only restate code are weak. Adversarial members also hunt dead code that looks live, flag-dependent paths and tests that contradict assumptions.
- **`repo + web`**: the repo is the subject; `repo` rules apply. Add **web researchers** (`general-purpose`; 1 / 2 / 3 at small / medium / large) as mandatory roles. They supply non-code context only (specs, RFCs, library docs, known issues, design rationale; dated, primary preferred), cited as under `web`, and make no claims about this repo.
- **`given`**: only the files and URLs the user supplied, what they link or name, and repo code if the wrapper allows it. No research beyond them; a gap becomes an open question, never an assumption. Citation: `file §heading Lnn-mm`, URL + section, or `path:line`. Scouts are `Explore`, or `general-purpose` only to open URLs the given sources link.

**Upstream code** (any mode except `given`). When the subject is open-source software, or a spec with a reference implementation, any agent may shallow-clone the upstream repo at the relevant release tag (`git clone --depth 1 --branch <tag> <url> .teamwork/<slug>/src/<name>`), reuse an existing clone, record the SHA in its ledger and cite `<repo>@<sha>:path:line`. Read only: never run its build, scripts, tests or hooks.

**Weighting** (agents and judge). For what a system does: source code > spec, RFC or paper > official docs > reputable secondary > practitioner > community. For what it should do, the normative spec leads. A shared upstream origin is not corroboration. Where docs and code disagree, the disagreement is a finding.

## Orchestration rules

- **All user input goes through `AskUserQuestion`**, here and in wrappers. Offer concrete options inferred from the conversation, the cwd or the scouts, recommended option first and marked `(Recommended)`, each with a description that says what it means and what it costs. "Other" is added automatically for free text. Plain-text questions are a last resort, used only when no options can be inferred. Bundle questions into as few calls as possible (up to 4 questions per call, 4 options per question), and never ask what a sensible default answers.
- **Subagents see none of this conversation and cannot spawn agents.** Every prompt you write must stand alone: the role, the absolute path of `brief.md` (stage 2), the files to read, the iron rules verbatim, the exact output file path and the return format.
- Every agent that writes a file is `general-purpose`. `Explore` cannot write files: use it only for scouts that read local files, which return their report as their final message for you to save.
- Spawn each stage's agents in parallel in one message, then **wait for every completion notification** before starting the next stage. Never act on, summarise or guess a result that hasn't arrived.
- Agents return only their file path and a summary of 5 lines or fewer. Don't read agent files yourself unless a stage says to; your context is the bottleneck.
- If an agent fails or writes no file, re-spawn it once with the same prompt. If it fails again, record the gap in `gaps.md` and continue.
- Keep every agent ID. Resume an agent with `SendMessage` (load it via `ToolSearch` if it is deferred). If resuming fails, spawn a fresh agent seeded with the original agent's file.

## Iron rules (verbatim in every agent prompt)

- **Academic standard.** Every statement or chosen approach carries a citation that supports it, in the form `brief.md` gives under evidence rules. No citation, no claim. Read the source yourself; never cite from memory or from a search snippet.
- Claim format: `id | label | statement | citation | quote | confidence + why`. `id` is `<your-agent-name>-<n>`, lowercase letters, digits and hyphens only (unique across the run). `quote` is the verbatim excerpt (3 lines or fewer) from the cited source that supports the statement; for code, the cited lines.
- Label each claim `FACT` (read in the cited source), `INFERENCE` (reasoned from listed fact ids, which you name) or `UNKNOWN` (looked, could not establish; say where you looked).
- Record negative results and contradictions; never smooth them over.
- Depth over volume: each claim should be non-obvious or decision-relevant to an expert. Restating a source is weak; applying domain knowledge to it is strong.
- Stay inside the objective and confirmed focus areas.
- Write your full output to your assigned file. Return only the path and a summary of 5 lines or fewer.

## Stage 0: Setup

Scratch dir: `.teamwork/<slug>/` under the cwd (use `<slug>-2`, `-3`... if it exists, so an old run can't leak in). Write `.teamwork/.gitignore` containing `*`; don't touch the repo's own `.gitignore`.

Ask `pre_questions` the caller didn't preselect, in one `AskUserQuestion` call, inferred option first. Then fix the source mode and the scout lenses.

Default team sizes, which `team_scale` overrides. Each size adds `mandatory_roles` and the wrapper's extra roles:

| Size | SMEs | Adversarial | Contrarian |
|---|---|---|---|
| small | 2-3 | 1 | 1 |
| medium | 4-5 | 1 | 1 |
| large | 6-8 | 2 | 1 |

## Stage 1: Exploration

Spawn 3-6 scouts, one per entry in `scout_lenses`, typed per the source mode (`general-purpose` for any lens that needs the web or an upstream clone). Keep them shallow and fast. Each report is 400 words or fewer:

- a sketch of the shape of the objective through its lens;
- 2-5 candidate **focus areas** (name, one line, why it matters, evidence);
- **recommended SMEs**: the specific domain expertise this objective needs, a one-line reason and the evidence that triggered it. Be specific: "Java memory model / j.u.c. expert", not "concurrency person".

Save each report to `scout-<lens>.md`. Read all of them, then merge and dedupe into 3-7 focus areas, a proposed SME roster and a complexity rating (small / medium / large).

## Stage 2: Ask the user (UI, not free text)

Use `AskUserQuestion` with selectable options. Never ask the user to type a list.

**Scope**
1. **Focus areas**: multiSelect, recommendations first and marked `(Recommended)`, each described in its option description.
2. **SMEs**: multiSelect over the proposed roster, each with its justification as the description. Don't list `mandatory_roles`, adversarial or contrarian members here; say in the question text that they are always included.

**Run settings** (single-selects, recommended first)

3. **Team size**: small / medium / large, recommending the complexity rating, each description giving the head-count.
4. **Citation verification**:
   - `Full (Recommended)`: verifiers re-open every citation. Slowest and most token-hungry, but the most reliable.
   - `Targeted`: verifiers check claims the adversaries targeted, claims resting on a single source, and a random 25% of the rest. Any file whose sample fails more than 10% is escalated to full.
   - `Judge spot-check`: no verifiers; the judge re-checks high-impact and borderline citations itself. Fastest, and the weakest guarantee.
5. Any wrapper-specific choice (e.g. audience).

Use one call when everything fits in 4 questions. Otherwise ask scope first and run settings second. If a list is longer than 4, split it across questions grouped by theme, or fold the lowest-priority items into one "Everything else" option. "Other" is added automatically for additions. Stop until the user answers. Never re-run stage 1 afterward; if the user's additions change things materially, re-confirm with another UI question.

Write `brief.md` containing the objective, confirmed focus areas (with the scout evidence for each), the team roster, the verification mode, the source mode and the full evidence rules (assembled per **Sources**), `extra_rules` and the scout file paths. Then announce the team to the user, one line per member: name, what it examines, and the scout finding or user pick behind it. Drop any SME with no trace to evidence or a user pick.

## Stage 3: Team (independent round)

Spawn all members together. `role_overrides` replaces the default adversarial or contrarian brief below, never the citation standard.

- **SMEs**: one per confirmed expertise (or expertise × area when an area is large). Open each prompt with: *"You are a world-class expert in <domain>. Apply precise, specification-level knowledge of this domain, its pitfalls and failure modes, to the objective."* Tell them to read primary sources in full, follow references and log what they searched for and failed to find. Each writes `sme-<name>.md`.
- **Adversarial** (mandatory): assume the emerging picture is wrong. Hunt counter-examples, retractions, stale or circular evidence, misuse, hidden paths and conflicts of interest. Steelman the strongest opposing view. Same citation standard. Writes `adv-<n>.md`.
- **Contrarian** (mandatory unless `role_overrides` replaces it): takes a radically different view of the objective itself. Questions the framing, proposes an alternative approach, or argues the objective should be met by other means or not at all. Must still cite; "different" is not "uncited". Writes `contrarian.md`.
- `mandatory_roles` and the wrapper's extra roles.

Members are independent: don't tell any of them what another found. Overlap is deliberate.

## Stage 4: Cross-examination

Once every stage-3 member has finished, `SendMessage` each adversarial member the paths of all `sme-*.md` files. Each attacks specific claims and appends findings to its own file. Every finding names `targets: <claim id>`, gives its counter-evidence with a citation and quote, and says why the target fails (wrong, stale, out of scope, overstated, unsupported).

## Stage 5: Verification

Skip this stage under `Judge spot-check`.

Spawn verifiers in parallel. Each takes one or more ledger files (`sme-*`, `adv-*`, `contrarian.md`, extra roles), up to about 40 claims per verifier. The claims in scope depend on the mode: every claim under `Full`; the targeted set plus escalations under `Targeted` (rows not checked are marked `UNCHECKED`). For each claim in scope, the verifier re-opens the cited source (reads the file at those lines, fetches the URL, finds the commit) and checks two things: the quote appears there, and it entails the statement. Verifiers judge support, not value. Each writes `verify-<n>.md` with rows `id | VERIFIED | QUOTE-MISMATCH | NOT-ENTAILED | UNREACHABLE | UNCHECKED | note`.

## Stage 6: Judge

Spawn one fresh `general-purpose` judge, and note its ID. Give it `brief.md`, `judge_bias` and every ledger and verify file. The judge rules; it does not write the output. For each component (claim, approach or scenario) it rules on merit:

- **Support**: start from the verifier's result. A claim marked `QUOTE-MISMATCH`, `NOT-ENTAILED` or `UNREACHABLE` cannot be included as cited unless right of reply fixes it. For `UNCHECKED` claims (or every claim under `Judge spot-check`), the judge re-opens the citations of all high-impact and borderline ones itself. `INFERENCE` stands only if every fact it names is included.
- **Source weight and independence**: per the weighting in `brief.md`.
- **Contradiction**: unresolved conflicts are carried as `INCLUDE-DISPUTED` with both sides, not deleted. Adversarial and contrarian findings are judged on merit, and a surviving adversarial finding overrides the claim it targets.
- **Value** to the objective and confirmed focus areas.

Verdicts: `INCLUDE | INCLUDE-DISPUTED | EXCLUDE | UNRULED`.

**Right of reply (once per statement).** For each `UNRULED` statement the judge writes a focused gap: exactly what is missing (weak source, quote mismatch, no corroboration, ambiguity) and what evidence would settle it. It ends its turn with a list of rows `statement id | agent | gap | what would settle it` instead of a ruling. You forward the gaps in parallel to the originating agents by `SendMessage`. Each agent appends its reply, with new citations and quotes, to its own file. Then `SendMessage` the judge the reply file paths. **Each statement gets exactly one reply, ever.** This exists to fix oversights; it is not an appeal loop. The judge must then rule `INCLUDE`, `INCLUDE-DISPUTED` or `EXCLUDE`; nothing stays `UNRULED`.

The judge writes `rulings.md`: one row per component, `id | verdict | one-line reason` (no leading pipe; for `INCLUDE-DISPUTED`, the reason names the opposing claim ids), followed by verdict counts.

## Stage 7: Synthesis

Spawn one fresh `general-purpose` synthesiser. Give it `brief.md`, `judge_bias`, the wrapper's `output` spec, `rulings.md`, `gaps.md` and every ledger file. It writes `draft.md` in the `output` structure, built only from `INCLUDE` and `INCLUDE-DISPUTED` claims (disputed claims show both sides). Its job is the explanation: order, connect and frame the included claims so the reader understands the subject, not a list of findings.

- Every sentence that carries a claim ends with a trace marker naming its claim ids, `{#sme-jmm-3}` or `{#sme-jmm-3,adv-1-2}`, alongside the wrapper's citation. Wrapper rules may say where markers go.
- Connecting prose may not add facts. A sentence that asserts something no included claim states is cut, or becomes an `INFERENCE` that names the included ids it rests on.
- It adds an Excluded digest (from `rulings.md`) and a Gaps section (from `rulings.md` and `gaps.md`).

Then check the trace yourself. Every marker id must be an included claim; this must print nothing:

```sh
grep -oE '\{#[a-z0-9,-]+\}' draft.md | tr -d '{}#' | tr ',' '\n' | sort -u > used.txt
awk -F'|' '$2 ~ /INCLUDE/ {gsub(/ /,"",$1); print $1}' rulings.md | sort -u > ok.txt
comm -23 used.txt ok.txt
```

Then `SendMessage` the judge the path of `draft.md`. It checks fidelity: each marked sentence says no more than its claims (scope, numbers, hedges, disputed status), and no unmarked sentence asserts a fact. It writes `fidelity.md` with rows `line | OK | OVERREACH | UNMARKED | BAD-ID | note`, folding in any ids the trace check printed. Send failures to the synthesiser once to fix, then re-run the trace check and send the judge the revised draft once more. The synthesiser deletes any sentence still failing after that.

## Stage 8: Editor (document outputs only)

Skip this stage if `output.kind` is `other`; `edited.md` is then `draft.md`.

You spawn the editor. It reads `draft.md` and writes `edited.md`. It should invoke the `stop-slop` skill if one is installed. Otherwise it removes AI prose patterns itself: filler openers and closers, stacked hedges, "it's important to note", rule-of-three padding, empty intensifiers, uniform rhythm, vague attribution, restating summaries, needless bullet lists and em-dash overuse. It also fixes structure. It must not change any fact, number, name, quote, claim scope, label, citation, trace marker or wrapper-protected token; a sentence it moves keeps its marker.

Then check the edit mechanically yourself:

```sh
tok() { grep -oE '\{#[^}]+\}|\[[^]]+\]|`[^`]+`|"[^"]+"|[0-9][0-9.,:%-]*' "$1" | sort; }
diff <(tok draft.md) <(tok edited.md)
```

Also diff any wrapper-protected tokens. If the diff is empty, ship `edited.md`. Otherwise send the editor the diff once to fix. If it still differs, ship `draft.md` and say so in the delivery message.

## Delivery

Strip the trace markers from the shipped file to get `final.md`, keeping the marked copy for audit:

```sh
sed -E 's/ ?\{#[a-z0-9,-]+\}//g' edited.md > final.md
```

Run any wrapper pre-delivery check on `final.md`; its fixes go to the editor on `edited.md`, then strip again. Write `final.md` to `output.path`. Tell the user:

- the path;
- counts of included, disputed and excluded components, from `rulings.md`, and the verification mode used;
- the key gaps and open questions;
- that `.teamwork/<slug>/` holds the ledgers, verifications, rulings and the trace-marked draft.

Do not paste the full output.
