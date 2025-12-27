import schedule
import time
import subprocess
import datetime

def run_processor():
    print(f"[{datetime.datetime.now()}] Running Boleto Processor...")
    # Running as a subprocess ensures isolation
    subprocess.run(["python", "process_boletos.py"])

def run_notifier():
    print(f"[{datetime.datetime.now()}] Checking Deadlines...")
    subprocess.run(["python", "check_deadlines.py"])

# Schedule Configuration
# 1. Process new files every 10 minutes (or 1 hour, etc.)
schedule.every(10).minutes.do(run_processor)

# 2. Check for upcoming deadlines once a day (e.g., at 09:00 AM)
schedule.every().day.at("09:00").do(run_notifier)

print("--- Production Scheduler Started ---")
print("Press Ctrl+C to stop.")

# Run once at startup to ensure everything is working
run_processor()
run_notifier()

while True:
    schedule.run_pending()
    time.sleep(1)
