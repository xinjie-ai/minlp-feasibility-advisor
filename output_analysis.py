"""
output_analysis.py

Utilities for:

1. Extracting optimization results from Pyomo
2. Creating diagnostics
3. Creating solution reports
4. Saving solution reports
5. Generating LLM/Agent summaries
"""

import json
import pandas as pd

from pyomo.environ import value


# ==========================================================
# SOLUTION EXTRACTION
# ==========================================================

def extract_solution(model):
    """
    Extract optimization results from the solved Pyomo model.

    Returns
    -------
    solution : dict
    """

    solution = {}

    solution["profit"] = value(
        model.total_profit
    )

    solution["cdu_flow"] = value(
        model.cdu_flow
    )

    solution["cdu_sulfur"] = value(
        model.cdu_sulfur
    )

    # ------------------------------------------------------
    # Feed usage
    # ------------------------------------------------------

    solution["feed_usage"] = []

    for feed in model.FEEDS:

        total_flow = sum(
            value(
                model.feed_to_tank_flow[
                    feed,
                    tank
                ]
            )
            for tank in model.TANKS
        )

        solution["feed_usage"].append(
            {
                "feed": feed,
                "active": int(
                    round(
                        value(
                            model.feed_active[
                                feed
                            ]
                        )
                    )
                ),
                "flow": round(
                    total_flow,
                    4
                )
            }
        )

    # ------------------------------------------------------
    # Tank summary
    # ------------------------------------------------------

    solution["tank_summary"] = []

    for tank in model.TANKS:

        solution["tank_summary"].append(
            {
                "tank": tank,
                "flow": round(
                    value(
                        model.tank_to_cdu_flow[
                            tank
                        ]
                    ),
                    4
                ),
                "sulfur": round(
                    value(
                        model.tank_sulfur[
                            tank
                        ]
                    ),
                    6
                )
            }
        )

    # ------------------------------------------------------
    # Network flows
    # ------------------------------------------------------

    solution["network_flows"] = []

    for feed in model.FEEDS:

        for tank in model.TANKS:

            flow = value(
                model.feed_to_tank_flow[
                    feed,
                    tank
                ]
            )

            if flow > 1e-6:

                solution["network_flows"].append(
                    {
                        "source": feed,
                        "destination": tank,
                        "flow": round(
                            flow,
                            4
                        )
                    }
                )

    for tank in model.TANKS:

        flow = value(
            model.tank_to_cdu_flow[
                tank
            ]
        )

        if flow > 1e-6:

            solution["network_flows"].append(
                {
                    "source": tank,
                    "destination": "CDU",
                    "flow": round(
                        flow,
                        4
                    )
                }
            )

    return solution


# ==========================================================
# DATAFRAME HELPERS
# ==========================================================

def feed_dataframe(solution):

    return pd.DataFrame(
        solution["feed_usage"]
    )


def tank_dataframe(solution):

    return pd.DataFrame(
        solution["tank_summary"]
    )


def network_dataframe(solution):

    return pd.DataFrame(
        solution["network_flows"]
    )


# ==========================================================
# CONSTRAINT SLACKS
# ==========================================================

def calculate_constraint_slacks(
    solution,
    cdu_minimum,
    cdu_maximum,
    sulfur_spec
):
    """
    Calculate basic business-facing slacks.
    """

    return {

        "cdu_min_slack":
            solution["cdu_flow"]
            -
            cdu_minimum,

        "cdu_max_slack":
            cdu_maximum
            -
            solution["cdu_flow"],

        "sulfur_slack":
            sulfur_spec
            -
            solution["cdu_sulfur"]

    }


# ==========================================================
# PRINT REPORTS
# ==========================================================

def print_solution_summary(
    solution
):

    print("\n" + "=" * 60)
    print("OPTIMIZATION SUMMARY")
    print("=" * 60)

    print(
        f"Profit     : "
        f"{solution['profit']:,.2f}"
    )

    print(
        f"CDU Flow   : "
        f"{solution['cdu_flow']:.2f}"
    )

    print(
        f"CDU Sulfur : "
        f"{solution['cdu_sulfur']:.4f}"
    )


def print_feed_summary(
    solution
):

    print("\n" + "=" * 60)
    print("FEED UTILIZATION")
    print("=" * 60)

    print(
        feed_dataframe(
            solution
        ).to_string(
            index=False
        )
    )


def print_tank_summary(
    solution
):

    print("\n" + "=" * 60)
    print("TANK SUMMARY")
    print("=" * 60)

    print(
        tank_dataframe(
            solution
        ).to_string(
            index=False
        )
    )


def print_constraint_slacks(
    slacks
):

    print("\n" + "=" * 60)
    print("CONSTRAINT SLACKS")
    print("=" * 60)

    for key, val in slacks.items():

        print(
            f"{key:<20}: "
            f"{val:10.4f}"
        )


# ==========================================================
# SOLUTION REPORT
# ==========================================================

def create_solution_report(
    solution,
    cdu_minimum,
    cdu_maximum,
    sulfur_spec
):
    """
    Create a structured report that can
    be consumed by AI agents.
    """

    slacks = calculate_constraint_slacks(
        solution,
        cdu_minimum,
        cdu_maximum,
        sulfur_spec
    )

    solution_report = {

        "objective": {

            "profit":
                solution["profit"]

        },

        "cdu": {

            "flow":
                solution["cdu_flow"],

            "sulfur":
                solution["cdu_sulfur"],

            **slacks

        },

        "feeds":
            solution["feed_usage"],

        "tanks":
            solution["tank_summary"],

        "network":
            solution["network_flows"]

    }

    return solution_report


# ==========================================================
# SAVE REPORT
# ==========================================================

def save_solution_report(
    solution_report,
    filename="solution_report.json"
):

    with open(
        filename,
        "w"
    ) as f:

        json.dump(
            solution_report,
            f,
            indent=4
        )


# ==========================================================
# AGENT / LLM SUMMARY
# ==========================================================

def create_solution_summary(
    solution_report
):
    """
    Create text that can be fed
    directly to an LLM.
    """

    text = f"""
Optimization Solution Summary

Profit:
{solution_report['objective']['profit']:.2f}

CDU Flow:
{solution_report['cdu']['flow']:.2f}

CDU Sulfur:
{solution_report['cdu']['sulfur']:.4f}

Sulfur Slack:
{solution_report['cdu']['sulfur_slack']:.4f}

CDU Minimum Throughput Slack:
{solution_report['cdu']['cdu_min_slack']:.4f}

CDU Maximum Throughput Slack:
{solution_report['cdu']['cdu_max_slack']:.4f}

Feed Utilization:
"""

    for feed in solution_report["feeds"]:

        text += (
            f"\n"
            f"{feed['feed']} | "
            f"active={feed['active']} | "
            f"flow={feed['flow']:.2f}"
        )

    return text


# ==========================================================
# HIGH-LEVEL REPORT GENERATOR
# ==========================================================

def generate_report(
    solution,
    cdu_minimum,
    cdu_maximum,
    sulfur_spec
):
    """
    Print human-readable results and
    create the structured solution report.
    """

    print_solution_summary(
        solution
    )

    print_feed_summary(
        solution
    )

    print_tank_summary(
        solution
    )

    slacks = calculate_constraint_slacks(
        solution,
        cdu_minimum,
        cdu_maximum,
        sulfur_spec
    )

    print_constraint_slacks(
        slacks
    )

    solution_report = (
        create_solution_report(
            solution=solution,
            cdu_minimum=cdu_minimum,
            cdu_maximum=cdu_maximum,
            sulfur_spec=sulfur_spec
        )
    )

    return solution_report