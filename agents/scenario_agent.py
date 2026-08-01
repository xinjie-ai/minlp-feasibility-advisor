"""
scenario_agent.py

Purpose:
    Interpret user questions and translate them
    into optimization scenario modifications.

Examples
--------
User:
    "Can I tighten sulfur spec to 0.75?"

Returns:
    {
        "cdu_sulfur_spec": 0.75
    }

User:
    "What if minimum CDU throughput is 240?"

Returns:
    {
        "cdu_min_throughput": 240
    }
"""

import json
import re

from llm_client import ask_llm


def scenario_agent(user_question):
    """
    Convert natural-language questions into
    optimization parameter changes.

    Parameters
    ----------
    user_question : str

    Returns
    -------
    dict
    """

    prompt = f"""
You are an optimization scenario planner.

Respond with ONLY JSON.

Do NOT explain.
Do NOT reason.
Do NOT think step-by-step.

Allowed parameters:

1. cdu_sulfur_spec
2. cdu_min_throughput
3. cdu_max_throughput

Examples:

Question:
Can I tighten sulfur spec to 0.75?

Response:
{{
    "cdu_sulfur_spec": 0.75
}}

Question:
What if CDU minimum throughput is 240?

Response:
{{
    "cdu_min_throughput": 240
}}

Question:
What if CDU maximum throughput is 260?

Response:
{{
    "cdu_max_throughput": 260
}}

User Question:

{user_question}

Return ONLY JSON.
"""

    response = ask_llm(prompt)

    print("\nScenario Agent Raw Response:")
    print(repr(response))


    try:

        json_match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if json_match is None:
            return {}

        return json.loads(
            json_match.group()
        )

    except Exception as e:

        print(
            f"Scenario agent parsing error: {e}"
        )

        return {}


if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk a scenario question:\n"
        )

        changes = scenario_agent(
            question
        )

        print("\nParsed Changes:")

        print(
            json.dumps(
                changes,
                indent=4
            )
        )