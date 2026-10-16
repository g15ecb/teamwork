---
name: teamwork-core
description: Internal engine shared by team-research, team-spec and team-code-understanding. Not for direct use; invoked by those skills with a parameter block (objective, scout lenses, citation rules, output spec).
user-invocable: false
---

# teamwork-core

Private implementation skill. The calling skill (the **wrapper**) hands you a **parameter block**. Run the five stages below against it. Wrapper-specific rules override defaults here.

## Parameter block (from the wrapper)

| Field | Meaning |
|---|---|
| `objective` | What the user wants. Ask once if missing. |
| `slug` | kebab-case name; scratch dir is `.teamwork/<slug>/` (add to `.gitignore` if the repo has one). |
| `scout_lenses` | 3-6 lenses for stage 1. |
| `evidence_rules` | What counts as a citation for this wrapper (URL+quote, `path:line`, spec source...). |
| `sme_hints` | Guidance on what kinds of SMEs suit this objective. |
| `output` | `kind` (`document` or `other`), path, required structure. |
| `extra_rules` | Anything else (read-only repo, spec format, etc.). |

## Iron rules (put them in every agent prompt you write)

- **Academic standard.** Every statement or chosen approach carries a citation that supports it, in the wrapper's `evidence_rules` form. No citation, no claim. Quote or point at the exact support; never cite from memory or from a search snippet.
- Label each claim `FACT` (read in the cited source), `INFERENCE` (reasoned from listed facts) or `UNKNOWN` (looked, could not establish).
- Record negative results and contradictions; never smooth them over.
- Agents write full output to files in the scratch dir and return only path + a ≤5-line summary, to keep your context small.
- Claim format: `id | label | statement | citation(s) | confidence + why`.

## Stage 1: Exploration

Spawn 3-6 scouts in parallel in one message (`Explore` for code, `general-purpose` when they need the web), one per `scout_lenses`. Keep them shallow and fast. Each writes `scout-<lens>.md` (≤400 words): a sketch of the shape of the objective, 2-5 candidate **focus areas** (name, one line, why it matters, evidence), and **recommended SMEs**: specific domain expertise this objective needs, one-line reason, and the evidence that triggered it. Be specific ("Java memory model / j.u.c. expert", not "concurrency person").

You merge and dedupe into: focus areas (3-7), a proposed SME roster, and a complexity rating (small / medium / large) that sets team size.

## Stage 2: Ask the user (UI, not free text)

Use `AskUserQuestion` with selectable options. Never ask the user to type a list.

1. **Focus areas**: multiSelect, your recommendations first, marked `(Recommended)`. Pre-describe each in the option description.
2. **SMEs**: multiSelect over the proposed roster, each with its justification as the description.
3. **Depth/team size** (single-select): small / medium / large, recommended one first.
4. Any wrapper-specific choice (e.g. audience) as further single-select.

The tool allows 4 options and 4 questions per call; if a list exceeds 4, split it into several questions (grouped by theme) or batch the lowest-priority ones as one "Everything else" option. "Other" is added automatically for additions. Stop until answered. Never re-run stage 1 afterward; if the user's additions change things materially, re-confirm with another UI question.

Then announce the team in one line per member (name, what it examines, the scout finding that justifies it). Drop any SME that lacks a trace to evidence or a user pick.

## Stage 3: Team

Spawn in parallel, one message. Keep every agent ID.

- **SMEs**: one per confirmed expertise (or expertise × area when an area is large). Brief each as a world-class specialist: *"You are a world-class expert in <domain>. Apply precise, specification-level knowledge of this domain, its pitfalls and failure modes, to the objective."* Give objective, focus areas, relevant scout notes, claim format, iron rules. Each writes `sme-<name>.md`.
- **Adversarial (mandatory; 2 if large)**: assume the emerging picture is wrong. Find counter-examples, retractions, stale or circular evidence, misuse, hidden paths, contradictions between the other SMEs' likely positions. Steelman the strongest opposing view. Same citation standard.
- **Contrarian (mandatory)**: takes a radically different view of the objective itself. Questions the framing, proposes an alternative approach, or argues the objective should be achieved by different means or not at all. Must still cite; "different" is not "uncited".
- Add the wrapper's `extra_rules` roles (e.g. web researcher for code work; tester for specs).

SMEs are independent: do not tell them what others find. Overlap is deliberate.

## Stage 4: Judge

Spawn one fresh `general-purpose` judge (note its ID) with the objective, the wrapper's `evidence_rules`, and every SME file. For each component (claim, approach, scenario) per SME it rules on merit, on the claim ↔ citation pairing:

- **Support**: does the cited source actually entail it?
- **Source weight and independence**: primary > secondary > community; shared upstream origin is not corroboration.
- **Verification**: re-fetch/re-read a sample of citations (all high-impact and borderline ones); reject any that don't check out.
- **Contradiction**: unresolved conflicts are carried as `DISPUTED` with both sides, not deleted. Adversarial and contrarian findings are judged on merit; an adversarial finding that survives overrides the claim it hits.
- **Value** to the objective and confirmed focus.

Verdicts: `INCLUDE | INCLUDE-DISPUTED | EXCLUDE | UNRULED`.

**Right of reply (once per statement).** For each `UNRULED` statement the judge writes a focused gap analysis: exactly what is missing (weak source, quote mismatch, no corroboration, ambiguity) and what evidence would settle it. The judge ends its turn with a list `statement id | SME | gap | what would settle it` instead of a ruling. You forward each to the originating SME in parallel with `SendMessage` (or a fresh agent seeded with that SME's file and the gap if resume isn't available), then pass the replies back to the judge. **Each statement gets exactly one reply, ever**; this is an oversight fix, not an appeal loop. The judge then must rule `INCLUDE`, `INCLUDE-DISPUTED` or `EXCLUDE`; nothing stays `UNRULED`.

The judge writes `judge-draft` (the output built only from included components, in the wrapper's `output` structure, with an Excluded digest and gaps) and `rulings.md` (id, verdict, one-line reason).

## Stage 5: Editor (document outputs only)

If `output.kind` is `document`, the judge hands the draft to an editor agent (invoke the `stop-slop` skill if installed). Remove AI prose and smells (filler openers/closers, hedging stacks, "it's important to note", rule-of-three padding, empty intensifiers, uniform rhythm, vague attribution, restating summaries, needless bullet-ification, em-dash overuse) and fix structure. The editor must not change any fact, number, name, quote, claim scope, label or citation. Verify mechanically: citation markers/paths and quoted strings are identical before and after (`grep`/`diff`); otherwise redo.

If `kind` is `other`, skip the editor.

## Delivery

Write the final output to `output.path`. Tell the user: the path, counts (claims/components included / disputed / excluded), key gaps and open questions, and that `.teamwork/<slug>/` holds ledgers and rulings. Do not paste the full output.
