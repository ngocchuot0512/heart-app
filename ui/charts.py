"""Biểu đồ matplotlib đồng bộ bảng màu Navy / Teal / Amber / Coral."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

NAVY, TEAL, CORAL, AMBER, MUTED = "#0F294A", "#0D9488", "#DC2626", "#F59E0B", "#64748B"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#CBD5E1")
    ax.tick_params(colors=MUTED, labelsize=9)


def gauge(p: float, color: str):
    fig, ax = plt.subplots(figsize=(4.2, 2.5))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Wedge((0, 0), 1, 0, 180, width=0.28, facecolor="#E2E8F0"))
    for lo, hi, c in ((0, 0.35, TEAL), (0.35, 0.65, AMBER), (0.65, 1, CORAL)):
        ax.add_patch(Wedge((0, 0), 1, 180 - hi * 180, 180 - lo * 180, width=0.28, facecolor=c, alpha=0.28))
    ang = np.deg2rad(180 - p * 180)
    ax.plot([0, 0.86 * np.cos(ang)], [0, 0.86 * np.sin(ang)], color=NAVY, lw=3, solid_capstyle="round")
    ax.add_patch(plt.Circle((0, 0), 0.06, color=NAVY))
    ax.text(0, -0.28, f"{p*100:.0f}%", ha="center", fontsize=22, fontweight="bold", color=color)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.45, 1.1)
    fig.patch.set_alpha(0)
    return fig


def contributions(contrib: list[dict], top: int = 8):
    items = contrib[:top][::-1]
    fig, ax = plt.subplots(figsize=(6, 0.42 * len(items) + 0.8))
    vals = [d["delta"] * 100 for d in items]
    ax.barh([d["label"] for d in items], vals, color=[CORAL if v > 0 else TEAL for v in vals], height=0.62)
    ax.axvline(0, color="#94A3B8", lw=1)
    ax.set_xlabel("Ảnh hưởng đến xác suất (điểm phần trăm)", color=MUTED, fontsize=9)
    _style(ax)
    fig.tight_layout()
    fig.patch.set_alpha(0)
    return fig


def trend(dates, series: dict, ylabel: str = ""):
    palette = [TEAL, CORAL, NAVY, AMBER]
    fig, ax = plt.subplots(figsize=(6.2, 3))
    for (name, ys), c in zip(series.items(), palette):
        ax.plot(dates, ys, marker="o", lw=2.2, color=c, label=name)
    if len(series) > 1:
        ax.legend(frameon=False, fontsize=9)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    fig.autofmt_xdate()
    _style(ax)
    fig.tight_layout()
    fig.patch.set_alpha(0)
    return fig