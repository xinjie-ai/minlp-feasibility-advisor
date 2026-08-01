# MINLP Feasibility Advisor

A multi-agent optimization advisor for oil refinery blending and throughput planning.

This project combines mathematical optimization, scenario analysis, visualization, and LLM-powered explanations to answer operational what-if questions such as:

- Can sulfur specifications be tightened?
- What happens if throughput targets increase?
- Which constraints are limiting profitability?
- What operational tradeoffs should planners consider?

The system uses Pyomo and SCIP to solve optimization problems and a locally hosted Qwen3 model via Ollama to generate explainable recommendations.


---

# Architecture

```text
User Question
      |
      v
Scenario Agent
      |
      v
Optimization Engine
(Pyomo + SCIP)
      |
      v
Visualization Tool
      |
      v
Reflection Agent
(Qwen3 + Ollama)
      |
      v
Business Recommendation
```

---

# Example User Questions

```text
Can I tighten sulfur spec to 0.77?
```

```text
What if CDU throughput increases to 240?
```

```text
Why did profit decrease?
```

```text
Show me the flow network.
```

---

# Features

## Optimization

- Mixed Integer Nonlinear Programming (MINLP)
- Feed-to-tank blending optimization
- Sulfur quality constraints
- Throughput constraints
- Profit maximization

## Scenario Analysis

Converts business questions into optimization scenarios.

Example:

```json
{
  "cdu_sulfur_spec": 0.77
}
```

## Visualization

Automatically generates:

- Feed utilization charts
- Tank sulfur charts
- Constraint slack analysis
- Feed → Tank → CDU network diagrams

## Reflection Agent

Uses a local Qwen3 model to compare baseline and scenario results and provide business-oriented recommendations.

Example output:

```text
The tightened sulfur specification remains feasible.

Profit decreases by approximately 6.4%.

The sulfur constraint becomes binding and reduces operational flexibility.

Recommendation:
Consider a sulfur target of 0.80 wt% to balance profitability and product quality.
```

---

# Technology Stack

## Optimization

- Python
- Pyomo
- SCIP

## Analytics

- Pandas
- NumPy

## Visualization

- Matplotlib
- NetworkX

## AI

- Ollama
- Qwen3:8B

---

# Project Structure

```text
minlp-feasibility-advisor/

├── orchestrator.py
├── minlp_model.py
├── solve_model.py
├── visualization.py
├── llm_client.py
│
├── agents/
│   ├── scenario_agent.py
│   └── reflection_agent.py
│
├── outputs/
│   ├── plots/
│   ├── reports/
│   └── logs/
│
├── screenshots/
│
├── requirements.txt
└── README.md
```

---

# Running the Project

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Install Ollama

Download:

https://ollama.com

Pull Qwen:

```bash
ollama pull qwen3:8b
```

## Run

```bash
python orchestrator.py
```

---

# Example Workflow

Input:

```text
Can I tighten sulfur spec to 0.77?
```

Processing:

```text
Scenario Agent
      ↓
Optimization Run
      ↓
Visualization
      ↓
Reflection Agent
```

Output:

```text
Scenario remains feasible.

Profit decreases by 6.4%.

Sulfur constraint becomes binding.

Recommendation:
Consider a sulfur target of 0.80 wt%.
```

---

# Note on Scope

This repository is a simplified demonstration designed to showcase the architecture and engineering patterns behind AI-assisted optimization workflows.

In production environments, refinery and process-industry optimization systems typically involve:

- significantly larger optimization models with advanced solvers such as Gurobi
- real-time operational data integration
- enterprise data pipelines
- model governance and validation workflows
- human-in-the-loop review processes
- advanced LLM orchestration and monitoring with conversational memory


---

# Author

Xinjie Tong

Principal Data Scientist

Industrial AI | Optimization | Manufacturing & Supply Chain