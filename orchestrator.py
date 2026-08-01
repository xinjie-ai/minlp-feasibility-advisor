"""
orchestrator.py

MINLP Feasibility Advisor

Workflow

User Question
      |
      v
Scenario Agent
      |
      v
Optimization Tool
      |
      v
Visualization Tool
      |
      v
Reflection Agent
      |
      v
Recommendation
"""

from copy import deepcopy

from minlp_model import default_config

from solve_model import solve_optimization

from visualization import generate_all_plots

from agents.scenario_agent import (
    scenario_agent
)

from agents.reflection_agent import (
    reflection_agent
)


# ==========================================================
# DISPLAY HELPERS
# ==========================================================

def print_banner(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_step(step_num, total_steps, step_name):

    print(
        f"\n[{step_num}/{total_steps}] {step_name}"
    )


def print_success(message):

    print(
        f"✓ {message}"
    )


# ==========================================================
# BASELINE RUN
# ==========================================================

def run_baseline(config):

    (
        _,
        _,
        baseline_solution,
        baseline_report
    ) = solve_optimization(
        config=config,
        tee=False
    )

    return (
        baseline_solution,
        baseline_report
    )


# ==========================================================
# SCENARIO RUN
# ==========================================================

def run_scenario(config):

    (
        _,
        _,
        scenario_solution,
        scenario_report
    ) = solve_optimization(
        config=config,
        tee=False
    )

    return (
        scenario_solution,
        scenario_report
    )


# ==========================================================
# KPI COMPARISON
# ==========================================================

def print_comparison(
    baseline_report,
    scenario_report
):

    print_banner(
        "SCENARIO COMPARISON"
    )

    print(
        f"{'Metric':<20}"
        f"{'Baseline':>15}"
        f"{'Scenario':>15}"
    )

    print("-" * 50)

    try:

        print(
            f"{'Profit':<20}"
            f"{baseline_report['objective']['profit']:>15.2f}"
            f"{scenario_report['objective']['profit']:>15.2f}"
        )

        print(
            f"{'CDU Flow':<20}"
            f"{baseline_report['cdu']['flow']:>15.2f}"
            f"{scenario_report['cdu']['flow']:>15.2f}"
        )

        print(
            f"{'CDU Sulfur':<20}"
            f"{baseline_report['cdu']['sulfur']:>15.4f}"
            f"{scenario_report['cdu']['sulfur']:>15.4f}"
        )

        print(
            f"{'Sulfur Slack':<20}"
            f"{baseline_report['cdu']['sulfur_slack']:>15.4f}"
            f"{scenario_report['cdu']['sulfur_slack']:>15.4f}"
        )

    except Exception:

        print(
            "Unable to print KPI comparison."
        )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print_banner(
        "MINLP FEASIBILITY ADVISOR"
    )

    print(
        "\nExample Questions:"
    )

    print(
        "  • Can I tighten sulfur spec to 0.77?"
    )

    print(
        "  • What if CDU minimum throughput is 240?"
    )

    print(
        "  • What if CDU maximum throughput is 260?"
    )

    user_question = input(
        "\nQuestion:\n> "
    )

    # ------------------------------------------------------
    # Baseline Case
    # ------------------------------------------------------

    print_step(
        1,
        5,
        "Baseline Optimization"
    )

    base_config = default_config()

    (
        baseline_solution,
        baseline_report
    ) = run_baseline(
        base_config
    )

    print_success(
        "Baseline solution completed"
    )

    generate_all_plots(
        baseline_solution,
        baseline_report,
        prefix="baseline"
    )

    print_success(
        "Baseline plots generated"
    )

    # ------------------------------------------------------
    # Scenario Agent
    # ------------------------------------------------------

    print_step(
        2,
        5,
        "Scenario Agent"
    )

    scenario_changes = scenario_agent(
        user_question
    )

    print_banner(
        "SCENARIO AGENT"
    )

    print("Input:\n")
    print(user_question)

    print("\nOutput:\n")

    if scenario_changes:

        for key, value in scenario_changes.items():

            print(
                f"  • {key} = {value}"
            )

    else:

        print(
            "No scenario changes identified."
        )

        return

    # ------------------------------------------------------
    # Scenario Config
    # ------------------------------------------------------

    scenario_config = deepcopy(
        base_config
    )

    scenario_config.update(
        scenario_changes
    )

    # ------------------------------------------------------
    # Scenario Optimization
    # ------------------------------------------------------

    print_step(
        3,
        5,
        "Scenario Optimization"
    )

    (
        scenario_solution,
        scenario_report
    ) = run_scenario(
        scenario_config
    )

    print_success(
        "Scenario solution completed"
    )

    # ------------------------------------------------------
    # Visualization
    # ------------------------------------------------------

    print_step(
        4,
        5,
        "Visualization Tool"
    )

    generated_files = (
        generate_all_plots(
            scenario_solution,
            scenario_report,
            prefix="scenario"
        )
    )

    print_success(
        f"{len(generated_files)} plots generated"
    )

    # ------------------------------------------------------
    # KPI Comparison
    # ------------------------------------------------------

    print_comparison(
        baseline_report,
        scenario_report
    )

    # ------------------------------------------------------
    # Reflection Agent
    # ------------------------------------------------------

    print_step(
        5,
        5,
        "Reflection Agent"
    )

    recommendation = reflection_agent(
        baseline_report=baseline_report,
        scenario_report=scenario_report,
        user_question=user_question
    )

    print_success(
        "Recommendation generated"
    )

    # ------------------------------------------------------
    # Final Answer
    # ------------------------------------------------------

    print_banner(
        "OPTIMIZATION ADVISOR"
    )

    print(
        recommendation
    )

    # ------------------------------------------------------
    # Plot Summary
    # ------------------------------------------------------

    print_banner(
        "GENERATED ARTIFACTS"
    )

    print("\nPlots:\n")

    for file in generated_files:

        print(
            f"  ✓ {file}"
        )

    # ------------------------------------------------------
    # Save Demo Session
    # ------------------------------------------------------

    try:

        with open(
            "demo_run.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"""
QUESTION
========

{user_question}


SCENARIO CHANGES
================

{scenario_changes}


RECOMMENDATION
==============

{recommendation}
"""
            )

        print(
            "\n✓ Saved demo_run.txt"
        )

    except Exception as e:

        print(
            f"\nUnable to save demo file: {e}"
        )


if __name__ == "__main__":
    main()