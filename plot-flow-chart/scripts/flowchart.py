"""Draw a high-level data-flow chart with matplotlib from a Python spec file.

Usage:
    python3 flowchart.py <spec.py> <output.png>

The spec file defines plain Python data (no imports needed):

    TITLE    = "Project X - data flow"
    SUBTITLE = "optional one-line note"                     # optional
    CANVAS   = (20, 11)                                     # width, height (inches == data units)
    GROUPS   = [  # optional containers drawn behind modules
        dict(id="g1", label="package_a", x=1, y=1, w=6, h=8, kind="core"),  # optional label_align="left"/"right"
    ]
    NODES    = [  # modules; x, y = box center
        dict(id="cam", label="Camera", sub="driver", x=2, y=5, w=2.6, h=1.2, kind="external"),
    ]
    EDGES    = [  # data flowing from src to dst
        dict(src="cam", dst="det", label="color image", sub="/camera/image_raw",
             style="solid", rad=0.0, src_side="right", dst_side="left", label_pos=0.5),
    ]
    LEGEND   = True                                         # optional
    # optional font sizes (pt) and edge-label background; defaults shown
    NODE_FS = 11.5   # box title (a node's own "fs" overrides it)
    SUB_FS = 8.8     # box sub line
    EDGE_FS = 9.3    # arrow label
    GROUP_FS = 14    # group title
    LEGEND_FS = 9.5  # legend
    LABEL_BG = True  # False: transparent arrow labels (place them in free space,
                     # off lines and boxes, since nothing hides what is behind)

kind: "external" | "core" | "sub" | "sink" | "debug" | "control" (colors below).
style: "solid" (main data) | "dashed" (control / service / optional data).
side: "left" | "right" | "top" | "bottom" | None (auto: nearest side).
via: optional list of (x, y) waypoints -> the edge is drawn as straight segments
     src anchor -> via... -> dst anchor (use it for right-angle routing instead of rad).
     Each waypoint must share x or y with the previous point. The label sits on the longest
     segment, or on segment index label_seg (0 = first); label_pos / dx / dy still apply.
"""
import runpy
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

KINDS = {
    #            face       edge       text
    "external": ("#EEEEEE", "#555555", "#222222"),
    "core":     ("#E3EEF9", "#2A6BB0", "#123A66"),
    "sub":      ("#FDEBD9", "#C0601A", "#5A2A05"),
    "control":  ("#EDE4F8", "#6A44B8", "#33205E"),
    "sink":     ("#E2F2E3", "#2E7D4F", "#14422A"),
    "debug":    ("#FFFFFF", "#888888", "#555555"),
}
GROUP_FACE = {"core": "#F5F9FD", "sub": "#FFF9F3", "external": "#F8F8F8",
              "control": "#F8F5FC", "sink": "#F4FAF4", "debug": "#FFFFFF"}
LEGEND_TEXT = {"external": "external system / hardware", "core": "project module (ROS node)",
               "sub": "processing stage inside a module", "control": "command / state interface",
               "sink": "output / actuator", "debug": "debug / optional output"}


def _anchor(n, side):
    x, y, w, h = n["x"], n["y"], n["w"], n["h"]
    return {"left": (x - w / 2, y), "right": (x + w / 2, y),
            "top": (x, y + h / 2), "bottom": (x, y - h / 2)}[side]


def _auto_side(a, b):
    dx, dy = b["x"] - a["x"], b["y"] - a["y"]
    if abs(dx) * a["h"] >= abs(dy) * a["w"]:
        return "right" if dx > 0 else "left"
    return "top" if dy > 0 else "bottom"


def _opposite(side):
    return {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]


def draw(spec, out):
    W, H = spec.get("CANVAS", (20, 11))
    fig, ax = plt.subplots(figsize=(W, H), dpi=130)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(W / 2, H - 0.45, spec["TITLE"], ha="center", va="center",
            fontsize=20, fontweight="bold", color="#1A1A1A")
    if spec.get("SUBTITLE"):
        ax.text(W / 2, H - 0.95, spec["SUBTITLE"], ha="center", va="center",
                fontsize=11, style="italic", color="#555555")

    for g in spec.get("GROUPS", []):
        face, edge, text = KINDS[g.get("kind", "core")]
        ax.add_patch(FancyBboxPatch((g["x"], g["y"]), g["w"], g["h"],
                                    boxstyle="round,pad=0.02,rounding_size=0.25",
                                    fc=GROUP_FACE[g.get("kind", "core")], ec=edge, lw=2.2,
                                    ls=g.get("ls", "-"), zorder=0))
        # label_align "left" / "right" keeps the title clear of vertical arrows entering the group's top
        align = g.get("label_align", "center")
        lx = {"left": g["x"] + 0.3, "right": g["x"] + g["w"] - 0.3}.get(align, g["x"] + g["w"] / 2)
        ax.text(lx, g["y"] + g["h"] - 0.35, g["label"], ha=align,
                va="center", fontsize=spec.get("GROUP_FS", 14), fontweight="bold", color=edge, zorder=1)
        if g.get("sub"):
            ax.text(g["x"] + g["w"] / 2, g["y"] + g["h"] - 0.72, g["sub"], ha="center",
                    va="center", fontsize=9.5, style="italic", color=edge, zorder=1)

    nodes = {n["id"]: n for n in spec["NODES"]}
    for n in spec["NODES"]:
        face, edge, text = KINDS[n.get("kind", "core")]
        ls = "--" if n.get("kind") == "debug" else "-"
        ax.add_patch(FancyBboxPatch((n["x"] - n["w"] / 2, n["y"] - n["h"] / 2), n["w"], n["h"],
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=face, ec=edge, lw=1.6, ls=ls, zorder=2))
        nfs = n.get("fs", spec.get("NODE_FS", 11.5))
        sfs = spec.get("SUB_FS", 8.8)
        if n.get("sub"):
            # title / sub offsets grow with the font sizes (defaults: +0.14 / -0.24)
            ax.text(n["x"], n["y"] + 0.14 + (nfs - 11.5) * 0.017, n["label"], ha="center",
                    va="center", fontsize=nfs, fontweight="bold", color=text, zorder=3)
            ax.text(n["x"], n["y"] - 0.24 - (sfs - 8.8) * 0.011, n["sub"], ha="center",
                    va="center", fontsize=sfs, color=text, zorder=3, linespacing=1.15)
        else:
            ax.text(n["x"], n["y"], n["label"], ha="center", va="center",
                    fontsize=nfs, fontweight="bold", color=text, zorder=3)

    for e in spec["EDGES"]:
        a, b = nodes[e["src"]], nodes[e["dst"]]
        s_side = e.get("src_side") or _auto_side(a, b)
        d_side = e.get("dst_side") or _opposite(s_side)
        p0, p1 = _anchor(a, s_side), _anchor(b, d_side)
        dashed = e.get("style") == "dashed"
        color = e.get("color", "#6A44B8" if dashed else "#333333")
        rad = e.get("rad", 0.0)
        arrow = "<|-|>" if e.get("both") else "-|>"
        ls = "--" if dashed else "-"
        via = [tuple(v) for v in e.get("via", [])]
        if via:
            # orthogonal route: straight segments through the waypoints, arrow head on the last one
            pts = [p0] + via + [p1]
            ax.plot([p[0] for p in pts[:-1]], [p[1] for p in pts[:-1]], color=color, lw=1.8, ls=ls,
                    zorder=4, solid_capstyle="butt")
            ax.annotate("", xy=p1, xytext=pts[-2], zorder=4,
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, ls=ls,
                                        mutation_scale=16, shrinkA=0, shrinkB=2))
            segs = list(zip(pts, pts[1:]))
            i = e.get("label_seg", max(range(len(segs)), key=lambda j: abs(segs[j][1][0] - segs[j][0][0])
                                       + abs(segs[j][1][1] - segs[j][0][1])))
            p0, p1, rad = segs[i][0], segs[i][1], 0.0  # label goes on this segment
        else:
            ax.annotate("", xy=p1, xytext=p0, zorder=4,
                        arrowprops=dict(arrowstyle=arrow, color=color, lw=1.8,
                                        ls=ls, mutation_scale=16,
                                        shrinkA=2, shrinkB=2,
                                        connectionstyle=f"arc3,rad={rad}"))
        if e.get("label"):
            t = e.get("label_pos", 0.5)
            mx, my = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
            # shift the label onto the arc3 bezier for curved edges
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            k = 2 * t * (1 - t) * rad
            mx, my = mx + k * dy, my - k * dx
            mx, my = mx + e.get("dx", 0), my + e.get("dy", 0)
            txt = e["label"] + (f"\n{e['sub']}" if e.get("sub") else "")
            ax.text(mx, my, txt, ha="center", va="center", fontsize=spec.get("EDGE_FS", 9.3), color=color,
                    zorder=5, linespacing=1.2,
                    bbox=(dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92)
                          if spec.get("LABEL_BG", True) else None))

    if spec.get("LEGEND", True):
        used = [k for k in KINDS if any(n.get("kind", "core") == k for n in spec["NODES"])]
        handles = [Patch(fc=KINDS[k][0], ec=KINDS[k][1], lw=1.3,
                         ls="--" if k == "debug" else "-", label=LEGEND_TEXT[k]) for k in used]
        handles += [Line2D([], [], color="#333333", lw=1.8, label="data flow"),
                    Line2D([], [], color="#6A44B8", lw=1.8, ls="--",
                           label="command / service / optional")]
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0),
                  ncol=min(len(handles), 4), frameon=False, fontsize=spec.get("LEGEND_FS", 9.5),
                  handlelength=2.2, columnspacing=2.0)

    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"saved {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    draw(runpy.run_path(sys.argv[1]), sys.argv[2])
