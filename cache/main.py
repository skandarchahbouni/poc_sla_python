import json
import os

CACHE_DIR = os.getenv("CACHE_DIR")
PROBLEMS_PATH = CACHE_DIR + "/data/problems.json"
SERVICES_STATUS_PATH = CACHE_DIR + "/data/services_status.json"
SERVICES_DOWNTIMES_PATH = CACHE_DIR + "/data/services_downtimes.json"


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    return {}


def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, default=str, indent=2)


def empty_cache():
    save_json(data={}, file_path=PROBLEMS_PATH)
    save_json(data={}, file_path=SERVICES_STATUS_PATH)
    save_json(data={}, file_path=SERVICES_DOWNTIMES_PATH)