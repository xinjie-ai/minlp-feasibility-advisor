"""
orchestrator.py

MINLP Feasibility Advisor

Workflow:

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

from agents.scenario_agent import (
    scenario_agent,
)

from agents.reflection_agent import (
    reflection_agent,
)

from visualization import (
    generate_all_plots,
)


def main():

    print("\n" + "=" * 70)
    print("MINLP FEASIBILITY ADVISOR")
    print("=" * 70)

    print("\nExample Questions:")
    print("  Can I tighten sulfur spec to 0.75?")
    print("  What if CDU minimum throughput is 240?")
    print("  What if CDU maximum throughput is 260?")

    user_question = input(
        "\nQuestion:\n> "
    )

    # ======================================================
    # BASELINE CASE
    # ======================================================

    print("\nRunning baseline optimization...")

    base_config = default_config()

    (
        _,
        _,
        baseline_solution,
        baseline_report,
    ) = solve_optimization(
        config=base_config,
        tee=False,
    )

    if baseline_report is None:

        print(
            "Baseline optimization failed."
        )

        return

    baseline_plot_files = generate_all_plots(
        baseline_solution,
        baseline_report,
        prefix="baseline",
    )

    # ======================================================
    # SCENARIO AGENT
    # ======================================================

    print("\nCalling Scenario Agent...")

    scenario_changes = scenario_agent(
        user_question
    )

    print("\nScenario Changes")
    print("-" * 50)

    print(scenario_changes)

    if not scenario_changes:

        print(
            "\nUnable to identify scenario changes."
        )

        return

    # ======================================================
    # CREATE SCENARIO CONFIG
    # ======================================================

    scenario_config = deepcopy(
        base_config
    )

    scenario_config.update(
        scenario_changes
    )

    print("\nScenario Configuration")
    print("-" * 50)

    for key, value in scenario_changes.items():

        print(
            f"{key}: {value}"
        )

    # ======================================================
    # SCENARIO CASE
    # ======================================================

    print("\nRunning scenario optimization...")

    (
        _,
        _,
        scenario_solution,
        scenario_report,
    ) = solve_optimization(
        config=scenario_config,
        tee=False,
    )

    if scenario_report is None:

        print(
            "Scenario optimization failed."
        )

        return

    scenario_plot_files = generate_all_plots(
        scenario_solution,
        scenario_report,
        prefix="scenario",
    )

    # ======================================================
    # REFLECTION AGENT
    # ======================================================

    print("\nCalling Reflection Agent...")

    recommendation = reflection_agent(
        baseline_report=baseline_report,
        scenario_report=scenario_report,
        user_question=user_question,
    )

    # ======================================================
    # RESULTS
    # ======================================================

    print("\n" + "=" * 70)
    print("OPTIMIZATION ADVISOR RESPONSE")
    print("=" * 70)

    print(recommendation)

    # ======================================================
    # GENERATED FILES
    # ======================================================

    print("\n" + "=" * 70)
    print("GENERATED PLOTS")
    print("=" * 70)

    for file in baseline_plot_files:

        print(file)

    for file in scenario_plot_files:

        print(file)


if __name__ == "__main__":
    main()