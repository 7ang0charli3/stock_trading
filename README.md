# Stock Trading Data Pipeline (Polygon → Snowflake)

This project automates the extraction of **stock ticker reference data** from the [Polygon.io](https://polygon.io/) API and loads it into a **Snowflake** table for centralized storage and analysis.

It runs automatically **once per day for 3 weeks** via **GitHub Actions**, and can also be triggered manually for testing.

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
- The GitHub workflow automatically terminates after **3 weeks**.  
- The workflow can also be triggered manually from the **Actions** tab.

---
