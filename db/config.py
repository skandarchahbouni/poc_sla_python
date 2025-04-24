from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
import os


# Load environment variables
load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

# Initialize the database and collections
db = client["poc"]
events_collection = db["events"]
services_status_history_collection = db["services_status_history"]
maintenance_history_collection = db["maintenance_history"]
