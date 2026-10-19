#!/usr/bin/env python3
"""Checks a plan's dependency graph and schedules it in waves. Needs Python 3.9+.

  python3 plan-graph.py doc FILE              a delivered plan document
  python3 plan-graph.py ledger FILE PLAN_ID   one plan in a planner ledger

Prints `steps N · waves W · recommended subagents K`, then one line per wave.
Every step needs a gate test command. Problems start with FAIL: and make the exit status 1. Steps are treated as equal in length.
"""
import re
import sys
from graphlib import CycleError, TopologicalSorter
from itertools import combinations


def parse_doc(lines):
    steps, deps, touches, stated, fails, gated = {}, set(), {}, {}, [], set()
    cur = None
    for line in lines:
        if m := re.match(r"- \[([ xX])\] \*\*(S\d+)", line):
            cur = m[2]
            steps[cur] = m[1] != " "
        elif cur and (m := re.match(r"\s+- Wave: *(\d+)", line)):
            stated[cur] = int(m[1])
        elif cur and re.match(r"\s+- Gate: *`[^`]+`", line):
            gated.add(cur)
        elif cur and re.match(r"\s+- Depends on:", line):
            deps |= {(d, cur) for d in re.findall(r"\bS\d+\b", line)}
        elif cur and re.match(r"\s+- Touches:", line):
            for p in re.findall(r"`([^`]+)`", line):
                touches.setdefault(p, set()).add(cur)
        elif cur and re.match(r"\s+- Commit:", line):
            if steps[cur] and not re.search(r"\b[0-9a-f]{7,40}\b", line):
                fails.append(f"FAIL: {cur} is ticked but has no commit SHA")
        for key, pat in (("waves", r"Waves: *(\d+)"), ("agents", r"Recommended subagents: *(\d+)")):
            if m := re.search(pat, line):
                stated[key] = int(m[1])
    fails += [f"FAIL: {s} has no Gate test command" for s in steps if s not in gated]
    return steps, deps, touches, stated, fails


def parse_ledger(lines, plan):
    steps, deps, touches, gated = {}, set(), {}, set()
    for line in lines:
        f = [x.strip(" \t`") for x in line.split("|")]
        if len(f) < 3 or not f[1].startswith(plan + "-s"):
            continue
        if f[0] == "step":
            steps[f[1]] = False
        elif f[0] == "after":
            deps.add((f[2], f[1]))
        elif f[0] == "gate" and f[2]:
            gated.add(f[1])
        elif f[0] == "touches":
            touches.setdefault(re.sub(r":[\d-]+$", "", f[2]), set()).add(f[1])
    return steps, deps, touches, [f"FAIL: {s} has no gate test command" for s in steps if s not in gated]


def schedule(preds, rank, k):
    """List schedule on k agents: each wave takes the k ready steps with the longest chain still ahead."""
    ts = TopologicalSorter(preds)
    ts.prepare()
    pool, waves = [], []
    while ts.is_active():
        pool = sorted(pool + list(ts.get_ready()), key=rank)
        wave, pool = pool[:k], pool[k:]
        ts.done(*wave)
        waves.append(wave)
    return waves


def check(steps, deps, touches):
    fails = []
    for a, b in sorted(deps):
        if a not in steps:
            fails.append(f"FAIL: {b} depends on unknown step {a}")
        elif b not in steps:
            fails.append(f"FAIL: unknown step {b} has dependencies")
    preds = {s: {a for a, b in deps if b == s and a in steps} for s in steps}
    try:
        order = list(TopologicalSorter(preds).static_order())
    except CycleError as e:
        return fails + [f"FAIL: dependency cycle {' -> '.join(e.args[1])}"], None
    anc = {}
    for v in order:
        anc[v] = set().union(*(anc[p] | {p} for p in preds[v]))
    for path, users in sorted(touches.items()):
        for a, b in combinations(sorted(users, key=list(steps).index), 2):
            if a not in anc[b] and b not in anc[a]:
                fails.append(f"FAIL: {a} and {b} both touch {path} but neither depends on the other")
    height = {}
    for v in reversed(order):
        height[v] = 1 + max((height[b] for a, b in deps if a == v and b in steps), default=0)
    w = max(height.values())
    pos = {s: i for i, s in enumerate(steps)}
    rank = lambda s: (-height[s], pos[s])
    # Fewest agents that still finish in w waves.
    for k in range(-(-len(steps) // w), len(steps) + 1):
        waves = schedule(preds, rank, k)
        if len(waves) == w:
            break
    return fails, (k, [sorted(x, key=pos.get) for x in waves])


def main(argv):
    if len(argv) < 2 or (argv[0], len(argv)) not in (("doc", 2), ("ledger", 3)):
        sys.exit("usage: plan-graph.py doc FILE | ledger FILE PLAN_ID")
    with open(argv[1], encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if argv[0] == "doc":
        steps, deps, touches, stated, fails = parse_doc(lines)
    else:
        steps, deps, touches, fails = parse_ledger(lines, argv[2])
        stated = None
    if not steps:
        print("FAIL: no steps found")
        return 1
    more, result = check(steps, deps, touches)
    fails += more
    if result:
        k, waves = result
        print(f"steps {len(steps)} · waves {len(waves)} · recommended subagents {k}")
        for i, wave in enumerate(waves, 1):
            print(f"wave {i}: {' '.join(wave)}")
        if stated is not None:
            if stated.get("waves") != len(waves):
                fails.append(f"FAIL: document says Waves: {stated.get('waves')}, graph has {len(waves)}")
            if stated.get("agents") != k:
                fails.append(f"FAIL: document says Recommended subagents: {stated.get('agents')}, graph gives {k}")
            for i, wave in enumerate(waves, 1):
                fails += [f"FAIL: {s} says Wave: {stated.get(s)}, schedule has {i}" for s in wave if stated.get(s) != i]
    for f in fails:
        print(f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
