# Enterprise Data Observability & Quality Engine

[![Production Build](https://github.com/lohotshreya/enterprise-data-observability/actions/workflows/pipeline_ci.yml/badge.svg)](https://github.com/lohotshreya/enterprise-data-observability/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![ML-Framework](https://img.shields.io/badge/MLOPS-Scikit--Learn%20%7C%20Great%20Expectations-orange)](https://scikit-learn.org/)

## 1. Project Introduction

In large-scale corporate data architectures, upstream data sources can silently break format, corrupt structural schemas, or introduce statistical data drift. If left undetected, these anomalies cascade into production databases, breaking machine learning models and data pipelines.

The **Enterprise Data Observability & Quality Engine** acts as an automated, real-time guardian for streaming data batches. Built as an asynchronous file system background daemon, the system catches incoming files the millisecond they are uploaded, evaluates them against declarative enterprise constraints, applies non-parametric statistical tracking to flag distribution drift, and strips out outlier rows via unsupervised machine learning models before data hits your clean cloud storage zones.

---

## 2. Core Libraries & Dependencies

The system utilizes the following tech stack to process high-throughput production files:

* **Engine Layer:** `Python 3.11+` handles core asynchronous processing.
* **Data Validation Engine:** `Great Expectations` applies declarative profiling to catch structural data faults.
* **Statistical Inference Engine:** `SciPy Stats` runs two-sample Kolmogorov-Smirnov ($KS$) tests to evaluate distribution shifts.
* **Machine Learning Engine:** `Scikit-Learn` utilizes an unsupervised `Isolation Forest` ensemble model to extract individual row anomalies.
* **Event Architecture Daemon:** `Watchdog` tracks multi-threaded OS file-system level write locks.
* **Infrastructure Layer:** `Docker Engine` ensures reproducible cloud deployments; `GitHub Actions` manages automated testing.

---

## 3. Data Ingestion Architectural Workflow

The processing framework runs incoming payloads through a fully decoupled validation matrix:

```text
Incoming Payload (.csv)
       │
       ▼
┌──────────────┐      Fail (Nulls / Type Mismatch / Invalid Ranges)
│  Ingestion   │───────────────────────────────────────────────────┐
│  & Schema    │                                                   │
└──────────────┘                                                   │
       │ Pass                                                      │
       ▼                                                           ▼
┌──────────────┐      Drift Triggered (p-value < alpha)     ┌─────────────┐
│ Statistical  │───────────────────────────────────────────>│ Enterprise  │
│ Data Drift   │                                            │  Alerting   │
└──────────────┘                                            │   Engine    │
       │ Continue                                           │  (Discord / │
       ▼                                                    │   Slack /   │
┌──────────────┐      Anomalies Tagged (Isolation Forest)   │   Local)    │
│ ML Anomaly   │───────────────────────────────────────────>└─────────────┘
│  Detection   │                                                   ▲
└──────────────┘                                                   │
       │ Output Clean Vector Batch                                 │
       ▼                                                           │
┌──────────────┐                                                   │
│ Data Lake    │───────────────────────────────────────────────────┘
│ (Clean Sync) │   Pipeline Execution Metrics & Status Transmitted
└──────────────┘

---
```
## 4. Setup Instructions (How to Clone and Install)

Follow these exact steps to clone this project, configure dependencies, and stand up a local instance of the background observability engine.

### Prerequisites
Ensure your development machine has the following software installed:
* **Git** installed on your local system.
* **Python 3.11** or higher.
* **Docker Desktop** (Optional, required only for container testing).

### Step 1: Clone the Repository
Open your terminal or command prompt, navigate to your working directory, and pull down the project source files:
```bash
git clone [https://github.com/lohotshreya/enterprise-data-observability.git](https://github.com/ylohotshreya/enterprise-data-observability.git)
cd enterprise-data-observability


### Step 2: Establish an Isolated Virtual Environment
Create a clean virtual layer to keep your project packages separated from your global computer environment:

# Initialize the virtual environment directory
python -m venv venv

# Activate the environment (Mac/Linux)
source venv/bin/activate

# Activate the environment (Windows Command Prompt)
# .\venv\Scripts\activate.bat

# Activate the environment (Windows PowerShell)
# .\venv\Scripts\Activate.ps1


### Step 3: Install Required Dependencies
Upgrade your base Python package manager and compile all the system framework requirements pinned in the manifesto:

pip install --upgrade pip
pip install -r requirements.txt
