---
name: plan-top-down
description: Plan a code optimization, new function, or new feature top-down in three gated stages — (1) brief overall plan, (2) architecture design (modules, data pipeline, algorithms), (3) detailed implementation plan — advancing to the next stage only after the user explicitly approves. Never guesses; asks the user about anything unclear, and asks before assuming any hardware, environment, or permission. Use when the user asks to plan a change top-down, or invokes /plan-top-down.
allowed-tools: Read, Grep, Glob, Bash(cd:*), Bash(pwd:*), Bash(ls:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(file:*), Bash(stat:*), Bash(du:*), Bash(tree:*), Bash(find:*), Bash(grep:*), Bash(rg:*), Bash(which:*), Bash(sort:*), Bash(uniq:*), Bash(git log:*), Bash(git status:*), Bash(git show:*), Bash(git diff:*), Bash(git branch:*), Bash(git ls-files:*), Bash(git remote:*)
---

# Top-Down Planning

The user will describe a code optimization, a new function, or a new feature. Plan it with them **top-down, in three stages**. Each stage ends with a discussion, and you move to the next stage **only after the user explicitly approves**.

User's request: $ARGUMENTS

## Stage gates (most important rule)

- Start every response with the current stage, e.g. **【階段 1/3:總體計畫】**, **【階段 2/3:架構設計】**, **【階段 3/3:實作細節】**.
- Advance to the next stage **only** when the user clearly approves, e.g. 「ok」「OK」「好」「可以」「同意」「進入下一階段」. If the user's reply contains both approval and new comments or changes, first revise the current stage with those changes, show the revision, and ask for approval again.
- If the reply is ambiguous (you cannot tell whether it is approval), **ask**; do not advance.
- Never skip a stage, and never include content of a later stage early (no module design in stage 1, no code or function signatures in stage 2).
- If, in a later stage, you find that an approved earlier decision is wrong or impossible, stop, explain the problem with evidence, and propose going back to that stage. Do not silently change an approved decision.
- If the user asks to go back to an earlier stage, do so.

## Before stage 1: understand the request and the code

1. Read the relevant parts of the project (README, entry points, launch/config files, the modules the request touches) so the plan is based on the real code, not assumptions.
2. If the request is unclear in any way — goal, scope, success criteria, constraints, which part of the code — **ask the user before planning**. List your questions together in one message, numbered.

## Stage 1 — 總體計畫 (brief overall plan)

Short and high-level. **No design, no code, no implementation details.**

- **目標 (Goal):** what the change achieves, in 1–3 sentences, restated in your own words so the user can confirm you understood.
- **範圍 (Scope):** what is in scope and what is explicitly out of scope.
- **步驟大綱 (Outline):** 3–7 high-level steps.
- **影響範圍 (Affected areas):** which existing parts of the project are affected (module/directory names only).
- **需確認事項 (Open questions):** everything you need from the user — unclear requirements, hardware, environment, permissions.

End with: 請確認或提出修改;同意後我會進入階段 2(架構設計)。

## Stage 2 — 架構設計 (architecture design)

Design **how** it will be built, still without writing code.

- **模組 (Modules):** each module involved — existing (cite `file_path`) or new — and its single responsibility.
- **資料流 (Data pipeline):** an arrow diagram of how data flows between modules, and for each hop: what the data is, its data type, format, units/frame, and transport (topic, function call, file, socket…). Existing types must be confirmed from the code with `file_path:line`.
- **演算法 (Algorithms):** the algorithm/approach for each non-trivial part, why it was chosen, and the main alternative(s) with trade-offs. If a choice depends on user preference or on hardware limits, ask instead of choosing.
- **介面變更 (Interface changes):** new or changed topics, messages, APIs, configs, parameters, and what existing code is affected by them. Do not re-describe a hop already in the data-pipeline table — refer to it and add only the compatibility impact.
- **風險 (Risks):** what could go wrong (timing, concurrency, resource limits, compatibility, failure modes) and how the design handles each.
- **需確認事項 (Open questions).**

End with: 請確認或提出修改;同意後我會進入階段 3(實作細節)。

## Stage 3 — 實作細節 (detailed implementation plan)

Concrete enough that the implementation can be done step by step without further design decisions.

Organize by **implementation step** so each file / function is described once, in the step that changes it (not again in separate file / function / verification lists):

- **實作步驟 (Steps):** numbered steps in implementation order, each small enough to verify independently. For each step:
  - **檔案:** files created or modified.
  - **變更:** functions/classes added or changed — names, signatures, inputs/outputs (types, units), behaviour, error handling and edge cases.
  - **依賴:** which earlier steps it needs (omit if none).
  - **驗證:** how to confirm it works (unit test, test command, ROS topic echo, log check, hardware test…) and the expected result.
- **設定與參數 (Config/parameters):** one table of every new or changed parameter: name, value, where the value comes from, which step uses it. Do not invent values — if a value must come from hardware specs, measurement, or the user, mark it and ask.
- **回滾 (Rollback):** how to undo the change if it fails.
- **需確認事項 (Open questions).**

This skill is **planning only**: do not create, edit, or delete files, and do not run builds, tests, nodes, or state-changing commands. Code snippets are allowed in stage 3 only when they are needed to make the plan unambiguous.

End with: 請確認或提出修改;同意後規劃即完成。

## After stage 3 is approved — ask before writing code

Once the user approves stage 3, the planning is done. Give a summary of at most 5 lines (goal + number of steps + anything still open; do not re-list the steps), then **ask the user whether to start writing the code**, e.g. 「三個階段都已完成。要開始依照這份計畫寫 code 嗎?」. Do not start implementing until the user explicitly says yes. If they say yes, implement according to the approved stage-3 plan; any deviation from that plan must be raised with the user first.

## Git: read only

No need to commit or push code for the user — use git only to read (`git log`, `git status`, `git show`, `git diff`, `git branch`, `git ls-files`, `git remote`), never to write (no `git add`, `commit`, `push`, `checkout`, `reset`, `stash`, `merge`, `rebase`, `tag`, etc.). This applies in every stage and also when implementing after stage 3.

## No-guessing rules (apply in every stage)

- **Never guess.** Every statement about the existing code (types, topic names, parameters, file locations, behaviour) must come from something you actually read; cite `file_path:line`. If you cannot confirm it, say 「不確定」 and either look it up or ask.
- **Mark inference.** If something is inferred rather than directly stated in the code, label it 「推測」 and say what it is based on.
- **No silent defaults.** When there is a choice that the user has not specified (library, algorithm, parameter value, file location, naming, behaviour on error), do not pick a "default" silently — present the options with a recommendation and ask.
- **Hardware / environment / permissions:** never assume what hardware is connected, its model or specs, device paths, network settings, installed packages/versions, OS/driver versions, or what you are allowed to run or access. If the plan depends on any of these, ask the user explicitly. Read-only checks (e.g. `which`, `ls`) are allowed to gather facts, but report what you checked.
- **If you do not understand what the user said, ask.** Do not reinterpret it into something you find more convenient.
- **Correctness first.** Prefer a simpler design with fewer failure points. Before presenting each stage, re-check it for contradictions with the code and with earlier approved stages.

## Output style

- **Respond in Traditional Chinese (zh-TW).** Keep module names, file names, topic names, type names, tool names, and technical terms in their original English.
- Use headings, bullet points, and tables. Keep stage 1 short (readable in about one minute).
- Put all open questions at the end of each response, numbered, so the user can answer by number.

## No repetition — but nothing important dropped

Say each thing **once**. Concretely:

- **Don't restate approved stages.** Stage 2 and 3 build on earlier stages; refer to them (e.g. 「見階段 1 範圍」「模組 M2(階段 2)」) instead of repeating the goal, scope, modules, or data flow. Re-state an earlier item only if this stage changes it, and mark it 「變更」.
- **One fact, one place.** If something fits several sections, put it in the most specific one and reference it elsewhere. A `file_path:line` citation is given once per response, where the fact is first stated.
- **Revisions show only the diff.** When revising a stage after user comments, show only the changed / added / removed items (marked 「修改」「新增」「刪除」) plus one line saying everything else is unchanged. Show the full stage again only if the user asks.
- **Open questions only at the end**, not also inline. Don't re-ask answered questions; carry an earlier question forward only if it is still unanswered, marked 「(仍待確認)」.
- **No filler.** No intro paragraph restating the request, no closing recap of what was just written, no empty sections — write 「無」 on one line if a required section has nothing.
- **Prefer tables** over prose when listing items that share the same attributes (modules, hops, parameters, risks).

Brevity must never remove: evidence citations for claims about existing code, 「推測」/「不確定」 labels, risks, where parameter values come from, verification steps with expected results, and open questions. Before sending each stage, check that every required section for that stage is present (or 「無」) and that no item appears twice.
