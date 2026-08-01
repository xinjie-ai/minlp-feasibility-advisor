"""
visualization.py

Create visualization artifacts from optimization results.

Output folder:

outputs/plots/
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


# ==========================================================
# OUTPUT DIRECTORY
# ==========================================================

PLOT_DIR = Path("outputs/plots")

PLOT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# FEED UTILIZATION
# ==========================================================

def plot_feed_utilization(
    solution,
    prefix="scenario"
):

    df = pd.DataFrame(
        solution["feed_usage"]
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["feed"],
        df["flow"]
    )

    plt.title(
        f"{prefix.title()} Feed Utilization"
    )

    plt.xlabel("Feed")
    plt.ylabel("Flow")

    plt.tight_layout()

    filename = (
        PLOT_DIR /
        f"{prefix}_feed_utilization.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    return str(filename)


# ==========================================================
# TANK SULFUR
# ==========================================================

def plot_tank_sulfur(
    solution,
    prefix="scenario"
):

    df = pd.DataFrame(
        solution["tank_summary"]
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["tank"],
        df["sulfur"]
    )

    plt.title(
        f"{prefix.title()} Tank Sulfur"
    )

    plt.xlabel("Tank")
    plt.ylabel("Sulfur")

    plt.tight_layout()

    filename = (
        PLOT_DIR /
        f"{prefix}_tank_sulfur.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    return str(filename)


# ==========================================================
# TANK FLOWS
# ==========================================================

def plot_tank_flows(
    solution,
    prefix="scenario"
):

    df = pd.DataFrame(
        solution["tank_summary"]
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["tank"],
        df["flow"]
    )

    plt.title(
        f"{prefix.title()} Tank Flows"
    )

    plt.xlabel("Tank")
    plt.ylabel("Flow")

    plt.tight_layout()

    filename = (
        PLOT_DIR /
        f"{prefix}_tank_flows.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    return str(filename)


# ==========================================================
# NETWORK GRAPH
# ==========================================================

def plot_flow_network(
    solution,
    prefix="scenario"
):
    """
    Draw refinery flow network:

    Feeds  -> left
    Tanks  -> center
    CDU    -> right
    """

    graph = nx.DiGraph()

    for edge in solution["network_flows"]:

        graph.add_edge(
            edge["source"],
            edge["destination"],
            weight=edge["flow"]
        )

    # --------------------------------------------------
    # Identify node groups
    # --------------------------------------------------

    feed_nodes = sorted(
        [
            node
            for node in graph.nodes()
            if node.startswith("F")
        ]
    )

    tank_nodes = sorted(
        [
            node
            for node in graph.nodes()
            if node.startswith("T")
        ]
    )

    cdu_nodes = ["CDU"]

    # --------------------------------------------------
    # Manual coordinates
    # --------------------------------------------------

    pos = {}

    # Feeds on left

    n_feeds = len(feed_nodes)

    for i, feed in enumerate(feed_nodes):

        pos[feed] = (
            0,
            n_feeds - i
        )

    # Tanks in center

    n_tanks = len(tank_nodes)

    for i, tank in enumerate(tank_nodes):

        pos[tank] = (
            5,
            n_tanks - i + 1
        )

    # CDU on right

    pos["CDU"] = (
        10,
        (max(n_feeds, n_tanks) / 2)
    )

    # --------------------------------------------------
    # Plot
    # --------------------------------------------------

    plt.figure(
        figsize=(14, 8)
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=3000,
        node_color="lightblue"
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=12,
        font_weight="bold"
    )

    edge_widths = []

    for _, _, data in graph.edges(data=True):

        edge_widths.append(
            max(
                1,
                data["weight"] / 10
            )
        )

    nx.draw_networkx_edges(
        graph,
        pos,
        width=edge_widths,
        arrows=True,
        arrowsize=25,
        edge_color="gray"
    )

    edge_labels = {

        (u, v): round(
            data["weight"],
            1
        )

        for u, v, data

        in graph.edges(data=True)

    }

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=9
    )

    plt.title(
        f"{prefix.title()} Feed → Tank → CDU Network"
    )

    plt.axis("off")

    plt.tight_layout()

    filename = (
        PLOT_DIR /
        f"{prefix}_flow_network.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return str(filename)

# ==========================================================
# CONSTRAINT SLACKS
# ==========================================================

def plot_constraint_slacks(
    solution_report,
    prefix="scenario"
):

    slacks = {

        "Sulfur":
            solution_report["cdu"][
                "sulfur_slack"
            ],

        "CDU Min":
            solution_report["cdu"][
                "cdu_min_slack"
            ],

        "CDU Max":
            solution_report["cdu"][
                "cdu_max_slack"
            ]
    }

    plt.figure(figsize=(8, 5))

    plt.bar(
        list(slacks.keys()),
        list(slacks.values())
    )

    plt.title(
        f"{prefix.title()} Constraint Slacks"
    )

    plt.ylabel(
        "Slack"
    )

    plt.tight_layout()

    filename = (
        PLOT_DIR /
        f"{prefix}_constraint_slacks.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

    return str(filename)


# ==========================================================
# GENERATE ALL
# ==========================================================

def generate_all_plots(
    solution,
    solution_report,
    prefix="scenario"
):

    files = []

    files.append(
        plot_feed_utilization(
            solution,
            prefix
        )
    )

    files.append(
        plot_tank_sulfur(
            solution,
            prefix
        )
    )

    files.append(
        plot_tank_flows(
            solution,
            prefix
        )
    )

    files.append(
        plot_flow_network(
            solution,
            prefix
        )
    )

    files.append(
        plot_constraint_slacks(
            solution_report,
            prefix
        )
    )

    return files
