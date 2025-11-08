import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime
import snowflake.connector
import schedule

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# API request URL
LIMIT = 1000


def run_stock_job():
    DS = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={POLYGON_API_KEY}"

    # Make the request
    response = requests.get(url)
    data = response.json()

    # Extract tickers
    tickers = []
    for ticker in data.get("results", []):
        ticker["ds"] = DS
        tickers.append(ticker)

    page_count = 1
    while "next_url" in data:
        print(f"requesting page {page_count} : {data['next_url']}")
        page_count += 1
        time.sleep(15)
        response = requests.get(data["next_url"] + f"&apiKey={POLYGON_API_KEY}")
        data = response.json()
        # Extract tickers
        for ticker in data.get("results", []):
            ticker["ds"] = DS
            tickers.append(ticker)

    # Output number of tickers retrieved
    print(f"Number of tickers retrieved: {len(tickers)}")

    # Reference example_data for fieldnames (keeps order)
    example_ticker = {
        "ticker": "A",
        "name": "Agilent Technologies Inc.",
        "market": "stocks",
        "locale": "us",
        "primary_exchange": "XNYS",
        "type": "CS",
        "active": True,
        "currency_name": "usd",
        "cik": "0001090872",
        "composite_figi": "BBG000C2V3D6",
        "share_class_figi": "BBG001SCTQY4",
        "last_updated_utc": "2025-10-15T06:05:51.037116752Z",
        "ds": "DATE",
    }

    fieldnames = list(example_ticker.keys())

    # Load to Snowflake instead of CSV
    load_to_snowflake(tickers, fieldnames)
    print(f"Loaded {len(tickers)} rows to Snowflake")


def load_to_snowflake(rows, fieldnames):
    # Build connection kwargs from environment variables
    connect_kwargs = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
    }
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    if account:
        connect_kwargs["account"] = account

    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_SCHEMA")
    role = os.getenv("SNOWFLAKE_ROLE")
    if warehouse:
        connect_kwargs["warehouse"] = warehouse
    if database:
        connect_kwargs["database"] = database
    if schema:
        connect_kwargs["schema"] = schema
    if role:
        connect_kwargs["role"] = role

    print(connect_kwargs)
    conn = snowflake.connector.connect(
        user=connect_kwargs["user"],
        password=connect_kwargs["password"],
        account=connect_kwargs["account"],
        database=connect_kwargs["database"],
        schema=connect_kwargs["schema"],
        role=connect_kwargs["role"],
        session_parameters={
            "CLIENT_TELEMETRY_ENABLED": False,
        },
    )
    try:
        cs = conn.cursor()
        try:
            table_name = os.getenv("SNOWFLAKE_TABLE", "stock_tickers")

            # Define typed schema based on example_ticker
            type_overrides = {
                "ticker": "VARCHAR",
                "name": "VARCHAR",
                "market": "VARCHAR",
                "locale": "VARCHAR",
                "primary_exchange": "VARCHAR",
                "type": "VARCHAR",
                "active": "BOOLEAN",
                "currency_name": "VARCHAR",
                "cik": "VARCHAR",
                "composite_figi": "VARCHAR",
                "share_class_figi": "VARCHAR",
                "last_updated_utc": "TIMESTAMP_NTZ",
                "ds": "VARCHAR",
            }
            columns_sql_parts = []
            for col in fieldnames:
                col_type = type_overrides.get(col, "VARCHAR")
                columns_sql_parts.append(f'"{col.upper()}" {col_type}')

            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS {table_name} ( "
                + ", ".join(columns_sql_parts)
                + " )"
            )
            cs.execute(create_table_sql)

            column_list = ", ".join([f'"{c.upper()}"' for c in fieldnames])
            placeholders = ", ".join([f"%({c})s" for c in fieldnames])
            insert_sql = (
                f"INSERT INTO {table_name} ( {column_list} ) VALUES ( {placeholders} )"
            )

            # Conform rows to fieldnames
            transformed = []
            for t in rows:
                row = {}
                for k in fieldnames:
                    row[k] = t.get(k, None)
                print(row)
                transformed.append(row)

            if transformed:
                cs.executemany(insert_sql, transformed)
        finally:
            cs.close()
    finally:
        conn.close()


if __name__ == "__main__":
    # Run immediately once, then schedule daily
    run_stock_job()

    # When to run daily: read from env var DAILY_RUN_TIME in HH:MM (24-hour) format.
    # Default: midnight
    run_time = os.getenv("DAILY_RUN_TIME", "00:00")
    print(f"Scheduling job to run once a day at {run_time} (local time)...")
    try:
        schedule.every().day.at(run_time).do(run_stock_job)
    except Exception as e:
        print(f"Invalid DAILY_RUN_TIME='{run_time}', falling back to once-per-day without specific time. Error: {e}")
        schedule.every().day.do(run_stock_job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting scheduler")
