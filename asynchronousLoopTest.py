import asyncio
from datetime import datetime
import pandas as pd
import os

FILENAME = './log.xlsx'
INTERVAL = 5

# Define a function that prints the current time
def print_time():
    print(f"Current time: {datetime.now().isoformat()}")

# Define another async function that runs print_time every 10 seconds
async def run_periodically():
    while True:
        # Call print_time
        # print_time()
        log = {
            # "tanggal": datetime.now().strftime("%d/%m/%Y"),
            "tanggal": datetime.now().isoformat(),
        }

        newLog = pd.DataFrame(data=log, columns=log.keys(), index=[0])
        print(newLog)            
        
        if (not os.path.exists(FILENAME)):
            newLog.to_excel(FILENAME, index=False)
        else:
            logFile = pd.read_excel(FILENAME)
            newLogFile = pd.concat([logFile, newLog]).reset_index(drop=True)
            newLogFile.to_excel(FILENAME, index=False)

        # Sleep for 10 seconds
        await asyncio.sleep(INTERVAL)

# Create an event loop
loop = asyncio.get_event_loop()
# Run the wrapper function until it completes or is cancelled
loop.run_until_complete(run_periodically())