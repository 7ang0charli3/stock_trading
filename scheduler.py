import schedule
import time
from script import run_stock_job
from datetime import datetime

def basic_job():
    print("Job started at : ", datetime.now())

# Run every 10 minutes
schedule.every(10).minutes.do(basic_job)
# Run 1 minute after basic_job
schedule.every().minutes.do(run_stock_job)

while True:
    schedule.run_pending()
    time.sleep(1)