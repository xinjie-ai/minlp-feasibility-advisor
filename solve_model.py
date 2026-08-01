"""
solve_model.py

Build and solve the crude scheduling MINLP.

Outputs:
    - solution
    - solution_report
    - solution_report.json

Visualization is handled separately.
"""
from pyomo.environ import value
from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus
from pyomo.opt import TerminationCondition

from minlp_model import build_model

from output_analysis import (
    extract_solution,
    generate_report,
    create_solution_summary,
    save_solution_report,
)


def solve_optimization(
    config=None,
    solver_name="scip",
    tee=True,
):
    """
    Build and solve the optimization model.

    Parameters
    ----------
    config : dict, optional
        Model configuration dictionary.

    solver_name : str
        Solver name.

    tee : bool
        Print solver log.

    Returns
    -------
    model
    results
    solution
    solution_report
    """

    # ------------------------------------------------------
    # Build model
    # ------------------------------------------------------

    model = build_model(config)

    print("\n" + "=" * 60)
    print("MODEL INFORMATION")
    print("=" * 60)

    print(f"Feeds       : {len(model.FEEDS)}")
    print(f"Tanks       : {len(model.TANKS)}")
    print(f"Variables   : {model.nvariables()}")
    print(f"Constraints : {model.nconstraints()}")

    # ------------------------------------------------------
    # Create solver
    # ------------------------------------------------------

    solver = SolverFactory(solver_name)


    print(f"Using solver: {solver_name}")

    # ------------------------------------------------------
    # Solve model
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("STARTING OPTIMIZATION")
    print("=" * 60)

    results = solver.solve(
        model,
        tee=tee
    )

    # ------------------------------------------------------
    # Solver status
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("SOLVER STATUS")
    print("=" * 60)

    print(f"Status      : {results.solver.status}")
    print(
        f"Termination : "
        f"{results.solver.termination_condition}"
    )

    # ------------------------------------------------------
    # Check successful solve
    # ------------------------------------------------------

    successful_solve = (

        results.solver.status == SolverStatus.ok

        and

        results.solver.termination_condition
        in [
            TerminationCondition.optimal,
            TerminationCondition.locallyOptimal,
        ]

    )

    if not successful_solve:

        print(
            "\nOptimization did not return "
            "an optimal solution."
        )

        return (
            model,
            results,
            None,
            None,
        )

    # ------------------------------------------------------
    # Extract solution
    # ------------------------------------------------------

    solution = extract_solution(model)

    # ------------------------------------------------------
    # Create report
    # ------------------------------------------------------

    solution_report = generate_report(
        solution=solution,
        cdu_minimum=model.config[
            "cdu_min_throughput"
        ],
        cdu_maximum=model.config[
            "cdu_max_throughput"
        ],
        sulfur_spec=model.config[
            "cdu_sulfur_spec"
        ],
    )

    # ------------------------------------------------------
    # Save report
    # ------------------------------------------------------

    save_solution_report(
        solution_report,
        filename="solution_report.json"
    )

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("SOLUTION SUMMARY")
    print("=" * 60)

    print(
        create_solution_summary(
            solution_report
        )
    )

    return (
        model,
        results,
        solution,
        solution_report,
    )


if __name__ == "__main__":

    (
        model,
        results,
        solution,
        solution_report,
    ) = solve_optimization(
        solver_name="scip",
        tee=True,
    )

    if solution is not None:

        print("\n" + "=" * 60)
        print("KEY RESULTS")
        print("=" * 60)

        print(
            f"Profit     : "
            f"{value(model.total_profit):,.2f}"
        )

        print(
            f"CDU Flow   : "
            f"{value(model.cdu_flow):.2f}"
        )

        print(
            f"CDU Sulfur : "
            f"{value(model.cdu_sulfur):.4f}"
        )

        print("\nSolution report saved to:")
        print("solution_report.json")