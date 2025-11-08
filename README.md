# Stock Trading Data Pipeline (Polygon → Snowflake)

This project automates the extraction of **stock ticker reference data** from the [Polygon.io](https://polygon.io/) API and loads it into a **Snowflake** table for centralized storage and analysis.

It runs automatically **once per day for 7 days** via **GitHub Actions**, and can also be triggered manually for testing.

---

## Features

- Extracts all **active stock tickers** from Polygon.io  
- Handles **API pagination** with rate-limit safety  
- Loads data into **Snowflake** with auto table creation  
- Adds a **daily partition column (`ds`)** for tracking  
- Supports both **manual** and **scheduled** GitHub Action runs  

---

## Architecture Overview

```
Polygon API → Python ETL Script → Snowflake Table → GitHub Actions (Scheduler)
```

The ETL pipeline retrieves stock tickers from Polygon, processes them with Python, and loads them into Snowflake, orchestrated via GitHub Actions.

---

## Repository Structure

```
stock_trading/
├── .github/
│   └── workflows/
│       └── run_7_days.yml       # GitHub Actions workflow
├── script.py                    # Main ETL script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Ignore virtual env and secrets
├── .env                         # Local environment variables (not committed)
└── tickers_data.csv             # Optional local export
```

---

## Local Setup

### Prerequisites

- Python 3.11+  
- A Snowflake account  
- A Polygon.io API key  

### 1. Clone the repository
```bash
git clone https://github.com/7ang0charli3/stock_trading.git
cd stock_trading
```

### 2. Create a virtual environment
```bash
python3 -m venv myenv
source myenv/bin/activate        # On Windows: myenv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your `.env` file
Create a `.env` file in the root folder:

```
POLYGON_API_KEY="your_polygon_api_key"
SNOWFLAKE_USER="your_snowflake_username"
SNOWFLAKE_PASSWORD="your_snowflake_password"
SNOWFLAKE_ACCOUNT="your_snowflake_account_id"
SNOWFLAKE_WAREHOUSE="your_warehouse_name"
SNOWFLAKE_DATABASE="your_database_name"
SNOWFLAKE_SCHEMA="your_schema_name"
SNOWFLAKE_ROLE="your_role_name"
```

### 5. Run manually
```bash
python3 script.py
```

---

## GitHub Actions Automation

The repository includes a **GitHub Actions workflow** that runs automatically to load data daily.

- Runs automatically at **11:00 UTC (4:30 PM IST)**  
- Executes for **7 consecutive days** starting from 2025-11-08  
- Loads the latest tickers into Snowflake  
- Uses repository secrets for credentials  

You can manually trigger the workflow anytime from **Actions → Run Stock Job for 7 Days → Run workflow**.

### Workflow file: `.github/workflows/run_7_days.yml`
Key features:
- Checks if the date is within the 7-day window  
- Installs dependencies  
- Runs the ETL script  
- Uses environment variables securely from GitHub Secrets  

---

## Required GitHub Secrets

These secrets store sensitive credentials securely and are used by the GitHub Actions workflow.

Go to **Settings → Secrets and variables → Actions → New repository secret**,  
and add each of these exactly as shown (case-sensitive):

| Secret Name | Example Value |
|--------------|----------------|
| `POLYGON_API_KEY` | `your_polygon_api_key_here` |
| `SNOWFLAKE_USER` | `your_snowflake_username` |
| `SNOWFLAKE_PASSWORD` | `your_snowflake_password` |
| `SNOWFLAKE_ACCOUNT` | `your_snowflake_account_id` |
| `SNOWFLAKE_WAREHOUSE` | `your_snowflake_warehouse` |
| `SNOWFLAKE_DATABASE` | `your_snowflake_database` |
| `SNOWFLAKE_SCHEMA` | `your_snowflake_schema` |
| `SNOWFLAKE_ROLE` | `your_snowflake_role` |

---

## Tech Stack

| Tool | Purpose |
|------|----------|
| **Python 3.11** | Core ETL development |
| **Requests** | API calls to Polygon.io |
| **Snowflake Connector** | Load data to Snowflake |
| **python-dotenv** | Local environment management |
| **schedule** | Task scheduling (optional local runs) |
| **GitHub Actions** | CI/CD automation |

---

## Snowflake Table Schema (Example)

| Column | Type | Description |
|---------|------|-------------|
| `TICKER` | VARCHAR | Stock symbol |
| `NAME` | VARCHAR | Company name |
| `MARKET` | VARCHAR | Market type |
| `LOCALE` | VARCHAR | Locale or region |
| `PRIMARY_EXCHANGE` | VARCHAR | Exchange identifier |
| `TYPE` | VARCHAR | Security type (e.g., CS, ETF) |
| `ACTIVE` | BOOLEAN | Whether the stock is active |
| `CURRENCY_NAME` | VARCHAR | Currency in which the stock trades |
| `CIK` | VARCHAR | Company identifier |
| `COMPOSITE_FIGI` | VARCHAR | FIGI code for the company |
| `SHARE_CLASS_FIGI` | VARCHAR | FIGI code for the share class |
| `LAST_UPDATED_UTC` | TIMESTAMP | Last update timestamp (UTC) |
| `DS` | VARCHAR | Data load date (partition column) |

*Note: The table is automatically created if it does not exist.*

---

## Notes

- Polygon’s free API plan allows **5 calls per minute**; the script uses a `time.sleep(15)` delay to stay within limits.  
- The GitHub workflow automatically terminates after **7 consecutive days**.  
- The workflow can also be triggered manually from the **Actions** tab.

---
