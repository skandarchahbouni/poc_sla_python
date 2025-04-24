# TODO


# Reset the cache from: 
    # All the events collection (zabbix, prometheus, .....)
    # maintennace_history collection


from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone 
import os


load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

db = client["poc"]
collection = db["services_status_history"]

# Load and sort the data
pipeline = [
    {"$sort": {"service": 1, "timestamp": 1}}
]
records = list(collection.aggregate(pipeline))

# Track downtime
downtime_per_service = {}
down_start_time = {}

for doc in records:
    service = doc["service"]
    status = doc["status"]
    timestamp = doc["timestamp"]

    if status == "DOWN":
        # If not already tracking downtime, mark the start
        if service not in down_start_time:
            down_start_time[service] = timestamp
    else:
        # If we were in a DOWN period, calculate its duration
        if service in down_start_time:
            duration = (timestamp - down_start_time[service]).total_seconds()
            downtime_per_service[service] = downtime_per_service.get(service, 0) + duration
            del down_start_time[service]


# Handle services still down at the end
now = datetime.now(timezone.utc)
for service, start_time in down_start_time.items():
    duration = (now - start_time).total_seconds()
    downtime_per_service[service] = downtime_per_service.get(service, 0) + duration

for service, seconds in downtime_per_service.items():
    print(f"{service}: {seconds} seconds")