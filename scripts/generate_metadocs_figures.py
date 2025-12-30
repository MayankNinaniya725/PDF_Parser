from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

BOX_STYLE = {
    "facecolor": "#E8F1FB",
    "edgecolor": "#1F4E79",
    "linewidth": 2,
    "boxstyle": "round,pad=0.3",
}

FLOW_COLORS = ["#3F51B5", "#26A69A", "#FF7043"]


def _init_canvas(title: str, figsize: tuple[float, float] = (14, 8)):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.suptitle(title, fontsize=18, fontweight="bold", y=0.95)
    return fig, ax


def _draw_box(ax, xy, text, size=(2.2, 1.4), facecolor="#E8F1FB"):
    rect = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.15,rounding_size=0.08",
        facecolor=facecolor,
        edgecolor="#1F4E79",
        linewidth=2,
        zorder=2,
    )
    ax.add_patch(rect)
    ax.text(
        xy[0] + size[0] / 2,
        xy[1] + size[1] / 2,
        text,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        wrap=True,
    )
    return (xy[0] + size[0] / 2, xy[1] + size[1] / 2)


def _arrow(ax, start, end, color="#1F4E79"):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=15,
        linewidth=2,
        color=color,
        zorder=1,
    )
    ax.add_patch(arrow)


def figure_2_1_system_architecture():
    fig, ax = _init_canvas("Figure 2.1: System Architecture of MetaDocs")
    positions = {
        "user": ((0.8, 6.5), (2.4, 1.6)),
        "core": ((3.8, 5.2), (2.4, 1.6)),
        "ocr": ((2.0, 3.2), (2.4, 1.4)),
        "vendor": ((5.8, 7.0), (2.4, 1.4)),
        "hash": ((6.0, 5.0), (2.4, 1.4)),
        "db": ((8.2, 3.6), (2.4, 1.6)),
        "output": ((5.5, 2.4), (2.6, 1.4)),
        "email": ((8.0, 6.2), (2.6, 1.4)),
    }

    centers = {
        key: _draw_box(
            ax,
            xy,
            {
                "user": "User /\nCloud Storage\n(Google Drive)",
                "core": "MetaDocs\nCore Engine",
                "ocr": "OCR Module",
                "vendor": "Vendor Template\nDetector",
                "hash": "Hashing &\nDuplicate Checker",
                "db": "Database\n(Master Records)",
                "output": "Output PDFs",
                "email": "Email /\nNotification System",
            }[key],
            size=size,
            facecolor="#F7FBFF" if key == "core" else "#E8F1FB",
        )
        for key, (xy, size) in positions.items()
    }

    _arrow(ax, centers["user"], centers["core"])
    _arrow(ax, centers["core"], centers["ocr"])
    _arrow(ax, centers["core"], centers["vendor"])
    _arrow(ax, centers["vendor"], centers["hash"])
    _arrow(ax, centers["hash"], centers["db"])
    _arrow(ax, centers["db"], centers["output"])
    _arrow(ax, centers["output"], centers["email"], color="#FF7043")
    _arrow(ax, centers["core"], centers["output"], color="#26A69A")
    _arrow(ax, centers["core"], centers["email"], color="#26C6DA")

    fig.savefig(OUTPUT_DIR / "figure_2_1_architecture.png", bbox_inches="tight")
    plt.close(fig)


def figure_2_2_workflow():
    fig, ax = _init_canvas("Figure 2.2: Workflow Diagram of Document Processing")
    steps = [
        "PDF Upload /\nAuto Scan",
        "Vendor Detection",
        "Field Extraction",
        "Duplicate Check",
        "Data Storage",
        "Output PDF\nGeneration",
    ]
    for idx, step in enumerate(steps):
        y = 8.5 - idx * 1.4
        _draw_box(ax, (4, y - 0.6), step, size=(2.8, 1.1), facecolor="#FFF8E1")
        if idx < len(steps) - 1:
            _arrow(ax, (5.4, y - 0.6), (5.4, y - 1.2), color="#FF7043")
    fig.savefig(OUTPUT_DIR / "figure_2_2_workflow.png", bbox_inches="tight")
    plt.close(fig)


def _draw_table(ax, xy, width, header, rows):
    row_height = 0.5
    height = row_height * (len(rows) + 1)
    rect = Rectangle(
        xy,
        width,
        height,
        facecolor="#F1F8E9",
        edgecolor="#33691E",
        linewidth=2,
        zorder=2,
    )
    ax.add_patch(rect)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height - row_height / 2,
        header,
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=11,
    )
    # header line
    ax.plot([xy[0], xy[0] + width], [xy[1] + height - row_height, xy[1] + height - row_height], color="#33691E", linewidth=2)
    for idx, row in enumerate(rows):
        y = xy[1] + height - row_height * (idx + 1.5)
        ax.text(
            xy[0] + 0.2,
            y,
            row,
            ha="left",
            va="center",
            fontsize=10,
        )
    return (
        xy[0] + width / 2,
        xy[1] + height / 2,
        width,
        height,
    )


def figure_2_3_db_schema():
    fig, ax = _init_canvas("Figure 2.3: Database Schema Design")
    tables = {
        "documents": ((1.0, 2.0), ["PK id", "vendor_id", "file_hash", "uploaded_at", "status"]),
        "extracted_fields": ((4.0, 5.5), ["PK id", "document_id", "field_name", "field_value", "confidence"]),
        "vendors": ((4.0, 2.0), ["PK id", "name", "template_path", "last_updated"]),
        "processing_logs": ((7.0, 2.0), ["PK id", "document_id", "stage", "message", "timestamp"]),
    }
    centers = {}
    for name, (xy, rows) in tables.items():
        centers[name] = _draw_table(ax, xy, 2.8, name, rows)

    def connect(table_from, table_to):
        start = (centers[table_from][0] + centers[table_from][2] / 2, centers[table_from][1])
        end = (centers[table_to][0] - centers[table_to][2] / 2, centers[table_to][1])
        _arrow(ax, start, end, color="#8E24AA")

    connect("documents", "extracted_fields")
    connect("documents", "processing_logs")
    _arrow(ax, (centers["vendors"][0], centers["vendors"][1] + centers["vendors"][3] / 2), (centers["documents"][0], centers["documents"][1] + centers["documents"][3] / 2), color="#00897B")

    fig.savefig(OUTPUT_DIR / "figure_2_3_database_schema.png", bbox_inches="tight")
    plt.close(fig)


def figure_3_1_testing_results():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    fig.suptitle("Figure 3.1: Testing Results Visualization", fontsize=18, fontweight="bold", y=0.95)
    metrics = ["Accuracy", "Time Reduction", "Duplicate Detection"]
    values = [95, 80, 93]
    colors = ["#3F51B5", "#26A69A", "#FF7043"]
    bars = ax.bar(metrics, values, color=colors, edgecolor="#263238", linewidth=1.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Performance (%)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2, f"{value}%", ha="center", va="bottom", fontweight="bold")
    fig.savefig(OUTPUT_DIR / "figure_3_1_testing_results.png", bbox_inches="tight")
    plt.close(fig)


def figure_3_2_ui_design():
    fig, ax = _init_canvas("Figure 3.2: User Interface Design", figsize=(14, 8))
    dashboard = Rectangle((0.8, 1.2), 8.4, 7.0, facecolor="#FAFAFA", edgecolor="#B0BEC5", linewidth=2)
    ax.add_patch(dashboard)
    ax.text(5.0, 7.6, "MetaDocs Dashboard", fontsize=14, fontweight="bold", ha="center")

    upload = Rectangle((1.2, 6.2), 3.5, 1.2, facecolor="#E3F2FD", edgecolor="#1E88E5", linewidth=2)
    ax.add_patch(upload)
    ax.text(2.95, 6.8, "PDF Upload", fontsize=12, fontweight="bold", ha="center")
    ax.text(2.95, 6.4, "Drag & Drop or Browse", fontsize=10, ha="center")

    status = Rectangle((5.0, 6.2), 3.8, 1.2, facecolor="#FCE4EC", edgecolor="#D81B60", linewidth=2)
    ax.add_patch(status)
    ax.text(6.9, 6.8, "Processing Status", fontsize=12, fontweight="bold", ha="center")
    ax.text(6.1, 6.4, "Current: Vendor Detection", fontsize=10)
    ax.text(6.1, 6.1, "Queue: 2 documents", fontsize=10)

    table = Rectangle((1.2, 2.6), 7.6, 3.2, facecolor="#FFFFFF", edgecolor="#CFD8DC", linewidth=2)
    ax.add_patch(table)
    columns = ["Field", "Value", "Confidence"]
    x_positions = [1.4, 4.2, 7.0]
    for col, x in zip(columns, x_positions):
        ax.text(x, 5.6, col, fontweight="bold", fontsize=11)
    sample_rows = [
        ("Invoice Number", "INV-2045", "97%"),
        ("Vendor", "Hengrun Steel", "94%"),
        ("Amount", "$45,200", "91%"),
    ]
    for idx, row in enumerate(sample_rows):
        y = 5.2 - idx * 0.6
        for value, x in zip(row, x_positions):
            ax.text(x, y, value, fontsize=10)

    button = Rectangle((6.5, 1.6), 2.0, 0.8, facecolor="#26A69A", edgecolor="#00695C", linewidth=2)
    ax.add_patch(button)
    ax.text(7.5, 2.0, "Download Results", fontsize=11, fontweight="bold", color="white", ha="center")

    fig.savefig(OUTPUT_DIR / "figure_3_2_ui_design.png", bbox_inches="tight")
    plt.close(fig)


def main():
    figure_2_1_system_architecture()
    figure_2_2_workflow()
    figure_2_3_db_schema()
    figure_3_1_testing_results()
    figure_3_2_ui_design()
    print("All figures generated in", OUTPUT_DIR)


if __name__ == "__main__":
    main()
