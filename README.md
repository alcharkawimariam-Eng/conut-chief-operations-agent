![Python](https://img.shields.io/badge/Python-3.11-blue)
![Status](https://img.shields.io/badge/Project-Completed-success)
![Architecture](https://img.shields.io/badge/Architecture-Modular-informational)
![Hackathon](https://img.shields.io/badge/Event-AI%20Engineering%20Hackathon-orange)

🚀 CONUT Chief Operations Agent
AI-Driven Multi-Branch Operational Intelligence System
🧠 Executive Summary

The CONUT Chief Operations Agent is an AI-powered operational intelligence system designed to support strategic and tactical decision-making across multiple F&B branches.

The system transforms structured operational data into:

📈 Revenue forecasting

🧩 Product combination insights

👥 Staffing pressure analysis

📍 Expansion feasibility evaluation

🗂 Unified branch-level intelligence export

This project was developed as part of an AI Engineering Hackathon to demonstrate end-to-end analytics design, from data preparation to decision-support modeling.

🎯 Problem Statement

Multi-branch food and beverage businesses generate large volumes of transactional and operational data. However, most organizations lack:

Structured forecasting tools

Data-driven combo optimization

Quantified staffing indicators

Objective expansion scoring

Unified branch-level intelligence

This leads to:

Reactive decision-making

Missed growth opportunities

Operational inefficiencies

Underutilized data assets

The goal of this project was to design a modular analytics engine that converts raw branch data into actionable operational intelligence.

🏗 System Architecture

The project follows a layered architecture:

Raw Data
   ↓
Data Cleaning & Feature Engineering
   ↓
Model-Ready Structured Data
   ↓
Analytics Layer (Forecast / Combo / Staffing / Expansion)
   ↓
Structured Decision Outputs (JSON)

Each analytics module operates independently but shares a common branch-centric design.

📂 Project Structure
conut-chief-operations-agent/
│
├── data/
│   ├── clean_raw_data_notebook/
│   ├── prepared data/
│   │   └── model_ready/
│
├── src/
│   ├── agent.py
│   ├── api.py
│   ├── beverage_strategy.py
│   ├── combo.py
│   ├── expansion.py
│   ├── forecast.py
│   ├── schema.py
│   ├── staffing.py
│   └── branch_json_export.py
│
└── README.md
📊 Data Pipeline
1️⃣ Data Cleaning

Raw Excel datasets were cleaned and standardized.
## 🧱 High-Level Architecture
            ┌────────────────────┐
            │   Raw Operational  │
            │       Data         │
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │ Data Cleaning &    │
            │ Feature Engineering│
            └─────────┬──────────┘
                      ↓
            ┌────────────────────┐
            │  Model-Ready Data  │
            └─────────┬──────────┘
                      ↓
      ┌───────────────┼────────────────┐
      ↓               ↓                ↓
 Forecast         Combo Engine     Staffing
      ↓               ↓                ↓
          ┌────────────────────┐
          │ Expansion Scoring  │
          └─────────┬──────────┘
                    ↓
          Structured JSON Output

2️⃣ Feature Engineering

Branch-level operational metrics were created including:

Daily revenue

Transaction counts

Product-level aggregation

Customer-level purchase grouping

3️⃣ Model-Ready Datasets

Final structured datasets stored in:

data/prepared data/model_ready/

These datasets are directly consumed by analytics modules.

🧠 Analytics Modules
📈 1. Revenue Forecasting (forecast.py)
Objective:

Predict short-term revenue for each branch.

Methodology:

Rolling 14-day mean baseline forecasting

Branch-level aggregation

Statistical summary reporting

Output Structure:
{
  "branch": "Conut - Tyre",
  "target_metric": "Total_Revenue",
  "horizon_days": 7,
  "method": "rolling_mean_14_days",
  "forecast": [...]
}
Value:

Provides short-term operational visibility for planning and resource allocation.

🧩 2. Combo Recommendation Engine (combo.py)
Objective:

Identify frequently co-purchased product pairs.

Methodology:

Customer-level grouping

Pairwise product combination analysis

Minimum support threshold filtering

Top-N selection

Example Output:
{
  "item_a": "CLASSIC CHIMNEY",
  "item_b": "NUTELLA SPREAD CHIMNEY.",
  "support_customers": 3
}
Value:

Supports:

Cross-selling

Bundling strategy

Menu engineering

Revenue optimization

👥 3. Staffing Analysis (staffing.py)
Objective:

Estimate branch workload pressure.

Methodology:

Revenue proxy for operational intensity

Branch comparison metrics

Performance variability indicators

Value:

Supports:

Staffing optimization

Shift planning

Labor cost control

📍 4. Expansion Feasibility Model (expansion.py)
Objective:

Evaluate which branches demonstrate expansion readiness.

Scoring Logic Includes:

Revenue consistency

Stability indicators

Performance thresholds

Operational patterns

Output:

Structured feasibility evaluation per branch.

Value:

Supports strategic expansion decisions based on measurable criteria.

🗂 5. Branch Intelligence Export (branch_json_export.py)
Objective:

Aggregate all branch-level analytics into one unified structured file.

Output file:

branches_full_data.json
Purpose:

API-ready format

LLM-ready structure

Unified branch intelligence repository

🧪 Engineering Design Principles

Modular architecture

Clear separation of concerns

Reproducible analytics

Branch-first data modeling

JSON structured outputs

Clean Git branch workflow

🔄 Git Workflow

Project developed using structured branching strategy:

data-foundation → data cleaning & feature engineering

analytics-models → modeling & analytics layer

main → stable integrated version

All modules were merged cleanly into main after validation.

⚙️ Installation & Execution
Clone
git clone https://github.com/alcharkawimariam-Eng/conut-chief-operations-agent.git
cd conut-chief-operations-agent
Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate
Run Modules
python src/forecast.py
python src/combo.py
python src/staffing.py
python src/expansion.py
python src/branch_json_export.py
📈 Business Impact

This system enables:

Data-driven branch management

Predictive operational planning

Structured expansion evaluation

Revenue optimization via combo intelligence

Consolidated branch analytics

It transforms raw operational data into actionable intelligence.

🚀 Future Enhancements

Machine Learning time-series forecasting (ARIMA, Prophet)

Real market basket mining (Apriori / FP-Growth)

Automated model retraining

REST API deployment

Dashboard integration (Streamlit / FastAPI frontend)

Advanced staffing optimization model
# 🏆 Key Achievements

- Designed modular analytics architecture
- Implemented multi-branch forecasting engine
- Built combo intelligence logic from customer transactions
- Created structured expansion feasibility scoring
- Delivered unified branch intelligence JSON export
- Implemented clean Git branching workflow
- Integrated all modules into production-ready main branch

🏁 Conclusion

The CONUT Chief Operations Agent demonstrates a full-stack analytics workflow:

From raw operational data
→ to structured modeling
→ to decision-support outputs

It showcases modular AI engineering, structured analytics thinking, and scalable branch-level intelligence design.# conut-chief-operations-agent
