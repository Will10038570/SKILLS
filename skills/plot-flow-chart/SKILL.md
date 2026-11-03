---
name: plot-flow-chart
description: Draw a high-level data-flow chart of the current project as a .png — the modules, the data passed between them (in plain words), and the direction it flows — without data types, sizes or shapes. Use when the user asks to plot / draw / visualize the data pipeline, data flow, or module diagram of the project, or invokes /plot-flow-chart.
---

# Plot Data-Flow Chart

Produce a **high-level** picture of how data moves through this project: which **modules** exist, **what data** goes between them, and **which direction** it flows. Save it as a `.png` in the **current working directory**.

## 1. Investigate (read-only)

1. Start from the wiring: launch files, config (YAML/JSON), docker-compose, README / CLAUDE.md, `main` entry points. They show which processes run and how they connect.
2. Find every data boundary: ROS topics / services / actions / TF, sockets / HTTP, serial / CAN, files read or written, hardware drivers, external systems.
3. Confirm each connection from source code (publisher / subscriber / client / server / file write). **Never guess** a connection; if something cannot be confirmed, leave it out or mark it `(unconfirmed)` in the label and tell the user.
4. Inside the main module(s), identify only the few big processing stages (e.g. "target selection → error filter → controller"), not functions.
5. Ignore stale docs / old diagrams that disagree with the code; the code wins.

## 2. Decide what goes on the chart

- **Modules** = boxes: external hardware/systems, the project's nodes/processes, and (optionally) the major stages inside a node.
- **Data** = arrow labels in plain words: "color image", "detected tag poses", "velocity command", "dock / undock goal". A topic / service name may be added as a small second line.
- **Direction** = arrow heads. Request/response pairs: one arrow each way, or a dashed double arrow for a service call.
- **Do NOT put** data types, message types, sizes, shapes, dtypes, rates, units, or algorithm parameters on the chart.
- Keep it readable: ≈ 6–20 boxes. Group a node's internal stages inside a container box. Put debug / optional outputs as dashed boxes. Put alternative setups (e.g. a simulator replacing hardware) as a short note, not as a second full graph, unless asked.
- Lay out left → right in the order data flows: sources → processing → sinks/actuators. Commands from users/clients may enter from the top.

### Clean lines (the user rejects messy charts)

Plan a **grid** before writing coordinates, so most arrows are straight and nothing crosses:
- One **row per pipeline** (e.g. main pipeline in the middle row, calibration / setup pipeline in the bottom row, commands / network in the top row). Sources sit in a left column, aligned with the row they feed.
- **Columns**: boxes in the same column share the exact same `x`, so vertical links (row ↔ row, e.g. a file read by a stage directly above it) are straight lines. Same `y` within a row → straight horizontal arrows.
- Equal box widths and equal gaps (≥ 1.2 units) so every short arrow has room for its label.
- **Straight lines only** (the user asked for this): every arrow is horizontal or vertical. Never use `rad` curves or diagonal lines. When two boxes are not in the same row/column, route the edge at right angles with `via=[(x, y), ...]` waypoints (each waypoint shares x or y with the previous point), e.g. `src right → via (dst_x, src_y) → dst top`. Run the corridors through empty space (between rows, under the bottom row). One source feeding two targets may share a trunk segment and branch off.
- Put the label on a segment that is long and free (`label_seg`, `label_pos`), never on top of a group title.
- **No crossings**: no arrow may pass through a box, a group title, or another arrow's label. If one does, move boxes (or drop a low-value edge and say it in a box `sub` or the subtitle) rather than bending lines more.
- Keep top-level boxes clear of the subtitle. Don't wrap the whole chart in one big container whose title gets crossed by arrows; put "Entry: main.py …" context in `SUBTITLE` instead.
- A group title sits at the group's top center by default; if a vertical arrow enters there, set `label_align="left"` or `"right"` on the group so the title is clear of the line.
- Short arrow labels (1–3 words); details go in the box `sub` line.
- Optional / disabled-by-default features: mention them in the subtitle instead of adding a box with long dashed lines.

## 3. Draw

1. Check libraries **before** writing code:
   ```bash
   python3 -c "import matplotlib; print(matplotlib.__version__)"
   ```
   - matplotlib present → use the bundled helper (below).
   - If matplotlib (or any library you want, e.g. graphviz) is missing → **stop and ask the user for permission to install it** (state the exact command, e.g. `pip3 install --user matplotlib`). Do not install without approval. Do not use a different library silently.
2. Write a spec file in the scratchpad (not in the project) describing `TITLE`, `SUBTITLE`, `CANVAS`, `GROUPS`, `NODES`, `EDGES`. The format is documented at the top of `scripts/flowchart.py`, including optional font sizes (`NODE_FS`, `SUB_FS`, `EDGE_FS`, `GROUP_FS`, `LEGEND_FS`) and `LABEL_BG = False` for transparent arrow labels (then every label must sit in free space, off lines and boxes). Box coordinates are centers in canvas units; leave ≥ 0.6 units between boxes so arrow labels fit.
3. Render:
   ```bash
   python3 ~/.claude/skills/plot-flow-chart/scripts/flowchart.py <spec.py> ./<project>_data_flow.png
   ```
   Output path = the **current working directory**. Use a descriptive name; if a file of that name already exists, ask before overwriting (or pick a new name).
4. **Look at the PNG** with the Read tool. Fix overlapping labels, arrows crossing boxes, clipped text, unreadable fonts (adjust coordinates, `via` waypoints, `label_seg`, `label_pos`, `dx`/`dy`, sides) and re-render until it is clean.
5. Use English text in the chart unless the user asks otherwise (avoids missing-CJK-font boxes). If Chinese is required, set a CJK font (e.g. `Noto Sans CJK TC`) and verify it renders.

## 4. Report

Reply in **Traditional Chinese (zh-TW)**: the PNG path, a 3–6 line summary of the flow shown, and anything left out or unconfirmed. Do not explain code.

## Rules

- Read-only on the project: only the PNG is written into the working directory; the spec and any temp files go in the scratchpad.
- Do not run builds, nodes, or tests to draw the chart.
- Correctness over completeness: every box and arrow must be backed by something read in the project.
