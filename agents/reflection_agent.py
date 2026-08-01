"""
reflection_agent.py

Generate a business-friendly explanation
of scenario results.
"""

from llm_client import ask_llm


def reflection_agent(
    baseline_report,
    scenario_report,
    user_question,
):

    # --------------------------------------------------
    # Extract Metrics
    # --------------------------------------------------

    baseline_profit = (
        baseline_report["objective"]["profit"]
    )

    scenario_profit = (
        scenario_report["objective"]["profit"]
    )

    baseline_flow = (
        baseline_report["cdu"]["flow"]
    )

    scenario_flow = (
        scenario_report["cdu"]["flow"]
    )

    baseline_sulfur = (
        baseline_report["cdu"]["sulfur"]
    )

    scenario_sulfur = (
        scenario_report["cdu"]["sulfur"]
    )

    baseline_sulfur_slack = (
        baseline_report["cdu"]["sulfur_slack"]
    )

    scenario_sulfur_slack = (
        scenario_report["cdu"]["sulfur_slack"]
    )

    # --------------------------------------------------
    # Compute Deltas
    # --------------------------------------------------

    profit_change = (
        scenario_profit -
        baseline_profit
    )

    flow_change = (
        scenario_flow -
        baseline_flow
    )

    sulfur_change = (
        scenario_sulfur -
        baseline_sulfur
    )

    sulfur_slack_change = (
        scenario_sulfur_slack -
        baseline_sulfur_slack
    )

    # --------------------------------------------------
    # Compact Prompt
    # --------------------------------------------------

    prompt = f"""
You are a refinery optimization advisor.

User Question:
{user_question}

BASELINE

Profit:
{baseline_profit:.2f}

CDU Flow:
{baseline_flow:.2f}

CDU Sulfur:
{baseline_sulfur:.4f}

Sulfur Slack:
{baseline_sulfur_slack:.4f}

SCENARIO

Profit:
{scenario_profit:.2f}

CDU Flow:
{scenario_flow:.2f}

CDU Sulfur:
{scenario_sulfur:.4f}

Sulfur Slack:
{scenario_sulfur_slack:.4f}

CHANGES

Profit Change:
{profit_change:.2f}

Flow Change:
{flow_change:.2f}

Sulfur Change:
{sulfur_change:.4f}

Sulfur Slack Change:
{sulfur_slack_change:.4f}

Provide:

1. Feasibility Assessment
2. Economic Impact
3. Operational Impact
4. Recommendation

Limit response to 150 words.
Use short business language.
"""

    print(
        f"\nReflection prompt length = "
        f"{len(prompt):,} characters"
    )

    try:

        response = ask_llm(
            prompt
        )

        return response

    except Exception as e:

        return f"""
Reflection Agent Failed

Error:
{e}

Summary:

Profit Change:
{profit_change:.2f}

Flow Change:
{flow_change:.2f}

Sulfur Change:
{sulfur_change:.4f}
"""