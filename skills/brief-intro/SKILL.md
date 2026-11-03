---
name: brief-intro
description: Give a short, high-level introduction to the current project — its purpose, its main modules, and a brief overview of its data pipeline — without explaining code. Use when the user asks for a project overview, a brief intro, or "what is this project about".
allowed-tools: Read, Grep, Glob, Bash(cd:*), Bash(pwd:*), Bash(ls:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(file:*), Bash(stat:*), Bash(du:*), Bash(tree:*), Bash(find:*), Bash(grep:*), Bash(rg:*), Bash(which:*), Bash(sort:*), Bash(uniq:*), Bash(git log:*), Bash(git status:*), Bash(git show:*), Bash(git diff:*), Bash(git branch:*), Bash(git ls-files:*), Bash(git remote:*)
---

# Brief Project Introduction

Give me a brief, high-level introduction to this project.

## What to cover

1. **Purpose** — What problem does this project solve, and what is it for? (6-8 sentences)
2. **Modules** — List the main modules/packages. For each, give one line on what it is responsible for.
3. **Data pipeline** — Briefly describe how data flows through the system: where it comes from (e.g. sensors, files, topics, APIs), which modules process it, and where the results go. A short arrow diagram (`A → B → C`) is welcome.

## Rules

- **Read-only.** You may read any file in the project (README, source, launch/config files, package manifests, git log) to understand it. Do **not** create, edit, or delete any file, and do not run builds, tests, or commands that change state.
- **Do not explain the code.** No walkthroughs of functions, classes, or implementation details. Stay at the level of purpose, responsibilities, and data flow.
- **Keep it brief.** Aim for something readable in about one minute. Use headings and bullet points.
- If something is unclear or cannot be determined from the files, say so briefly instead of guessing.
- **Respond in Traditional Chinese (zh-TW).** Keep module names, file names, tool names, and technical terms (e.g. ROS topic, node, launch file) in their original English.
