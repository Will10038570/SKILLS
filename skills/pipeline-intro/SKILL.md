---
name: pipeline-intro
description: Introduce the data pipeline of the current project — where data comes from, every hop it takes, and where it ends up — specifying for each hop what the data is, its data type, and its format, without explaining code. Use when the user asks how data flows, for a data pipeline overview, or "what data goes where" in this project.
allowed-tools: Read, Grep, Glob, Bash(cd:*), Bash(pwd:*), Bash(ls:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(file:*), Bash(stat:*), Bash(du:*), Bash(tree:*), Bash(find:*), Bash(grep:*), Bash(rg:*), Bash(which:*), Bash(sort:*), Bash(uniq:*), Bash(git log:*), Bash(git status:*), Bash(git show:*), Bash(git diff:*), Bash(git branch:*), Bash(git ls-files:*), Bash(git remote:*)
---

# Data Pipeline Introduction

Analyze this project and explain its **data pipeline**: how data flows from its sources, through each processing stage, to its final destinations. Focus on the **data itself**, not on the code that moves it.

## How to investigate

1. **Find the entry points and wiring first.** Look at launch files, config files (YAML/JSON/TOML/INI), Docker/compose files, package manifests, README, and `main` entry points. These usually reveal which processes run and how they are connected.
2. **Find every data boundary.** Search for where data enters, leaves, or crosses between components, e.g.:
   - ROS topics / services / actions (publishers, subscribers, message types in `msg/`, `srv/`, `action/`)
   - Sockets, HTTP/REST/WebSocket endpoints, gRPC/protobuf, MQTT, serial/CAN/UART, shared memory
   - File reads/writes (CSV, JSON, YAML, images, maps, logs, model weights), databases
   - Hardware drivers / SDKs (cameras, LiDAR, IMU, motors, encoders)
3. **For each boundary, confirm the data type from the source**: the message definition, struct/class, schema, serializer call, or file-writing code. Do not infer a type from a variable or topic name alone.

## What to report

### 1. Pipeline overview
A short arrow diagram of the end-to-end flow, labelling each arrow with the data on it, e.g.

```
Camera driver --[sensor_msgs/Image, bgr8, /camera/image_raw]--> Detector --[custom DetectionArray]--> Planner --> ...
```

If there are several independent pipelines (e.g. perception, control, logging), give one diagram per pipeline.

### 2. Data sources
For each source: what produces the data (sensor, file, user input, external service), and what the raw data is.

### 3. Stage-by-stage flow
For **every hop**, give a table row:

| From → To | What the data is | Data type | Format / encoding | Transport | Evidence |
|---|---|---|---|---|---|
| e.g. LiDAR driver → localization | 3D point cloud of the environment | `sensor_msgs/PointCloud2` | binary, fields x,y,z,intensity (float32) | ROS topic `/points` | `launch/lidar.launch:12` |

- **What the data is** — its meaning in plain words (e.g. "robot pose in map frame", "target velocity command").
- **Data type** — the concrete type: message type, struct/class, primitive array, schema name.
- **Format / encoding** — serialization and layout: JSON, CSV columns, protobuf, raw bytes, image encoding (e.g. `bgr8`, JPEG), array shape/dtype, units and coordinate frame **only if stated in the project**.
- **Transport** — topic/service name, endpoint/URL, port, file path, device path.
- **Evidence** — `file_path:line` where you confirmed it.

### 4. Data sinks
Where data finally ends up: actuators, displays/UI, saved files, databases, logs, external systems — with the type and format of what is written.

### 5. Uncertain or unresolved points
A list of everything you could not confirm, each with the reason (e.g. "type comes from a closed-source SDK", "topic name is set at runtime by a parameter", "file is not in the repo").

## Rules

- **Correctness over completeness. Never guess.** Every type, format, topic name, unit, and rate must come from something you actually read in the project. If you could not confirm it, write **「不確定」** in that cell and list it in section 5. Do not fill gaps with "typical" values (e.g. typical camera resolution, typical update rate).
- **Distinguish fact from inference.** If something is reasonably inferred but not directly stated (e.g. from a variable name), mark it **「推測」** and say what it is based on.
- **Do not explain the code.** No function or class walkthroughs, no algorithm explanations. Mention a file/function only as evidence of where data is defined or crosses a boundary.
- **Read-only.** Do not create, edit, or delete files, and do not run builds, tests, nodes, or any command that changes state.
- Skip vendored third-party code, build outputs, and generated files unless they define a data type that the project's pipeline uses.
- **Respond in Traditional Chinese (zh-TW).** Keep module names, file names, topic names, type names, tool names, and technical terms (e.g. ROS topic, node, PointCloud2, JSON) in their original English.
