from db.config import events_collection, services_status_history_collection
from datetime import datetime, timezone
from cache.main import PROBLEMS_PATH, SERVICES_DOWNTIMES_PATH, SERVICES_STATUS_PATH, load_json, save_json
from change_stream.constants import *


def add_problem(event: dict) -> None:
    """Add a new problem to the list of problems for a host."""
    event_id = event['eventid']
    severity = event['severity']
    trigger = event['name']
    host_name = event['hosts'][0]['host']
    new_entry = {"eventid": event_id, "trigger": trigger, "severity": severity}
    problems = load_json(PROBLEMS_PATH)
    problems.setdefault(host_name, []).append(new_entry)
    save_json(problems, PROBLEMS_PATH)
    print(f"Added new problem to {host_name}: {new_entry}")


def remove_problem(event: dict) -> None:
    """Remove a resolved problem from the list of problems."""
    p_eventid = event.get('p_eventid')
    if p_eventid:
        prev_event = events_collection.find_one({"eventid": p_eventid})
        if prev_event:
            host_name = prev_event['hosts'][0]['host']
            event_id = prev_event['eventid']
            problems = load_json(PROBLEMS_PATH)
            # Remove the resolved event
            problems[host_name] = [
                entry for entry in problems[host_name] if entry['eventid'] != event_id
            ]
            if not problems[host_name]:
                del problems[host_name]
                save_json(problems, PROBLEMS_PATH)
                print(f"All problems resolved for {host_name}, host entry removed.")
            else:
                save_json(problems, PROBLEMS_PATH)
                print(f"Resolved event {event_id} removed from {host_name}")

    
def check_problem(host: str, problem: str) -> int:
    """
    Check whether the host has a specific problem, and return the severity.
    If not found, return -1.
    """
    problems = load_json(PROBLEMS_PATH)
    host_problems = problems.get(host, [])
    for pr in host_problems:
        if pr["trigger"] == problem:
            return pr["severity"]
    return -1


def add_to_status_history(service: str) -> None:
    """Add the current service status to the status history."""
    services_status = load_json(SERVICES_STATUS_PATH)
    service_status = services_status.get(service, {"status": "UNKOWN", "timestamp": None})
    document = {
        "timestamp": service_status["timestamp"],
        "service": service,
        "status": service_status["status"]
    }
    
    result = services_status_history_collection.insert_one(document)
    if result.acknowledged:
        print("Document inserted successfully")


def update_service_status(service: str, status: str) -> None:
    """Update the service status and track downtimes."""
    services_status = load_json(SERVICES_STATUS_PATH)
    previous_status = services_status.get(service, {"status": "UNKNOWN", "timestamp": None})
    if status == previous_status["status"]:
        print(f"No update needed, Status for service: {service} is always {status}")
        return 
    
    timestamp = datetime.now(timezone.utc)
    # Track downtime if the service was previously down
    if previous_status["status"] == DOWN:
        services_downtimes = load_json(SERVICES_DOWNTIMES_PATH)
        downtime = timestamp - datetime.fromisoformat(previous_status["timestamp"])
        services_downtimes[service] = services_downtimes.get(service, 0) + downtime.total_seconds()
        save_json(data=services_downtimes, file_path=SERVICES_DOWNTIMES_PATH)
        print(f"Downtime updated for {service}: {services_downtimes}")
    services_status = load_json(SERVICES_STATUS_PATH)
    services_status[service] = {"status": status, "timestamp": timestamp}
    print(f"Status changed for {service}: {status}")
    save_json(data=services_status, file_path=SERVICES_STATUS_PATH)
    add_to_status_history(service=service)



def check_service_status(service: str) -> str:
    status = ""
    if service == SAAS:
        if check_problem(host=APPLICATION_HOST, problem=UNREACHABLE) == -1 and check_problem(host=DATABASE_HOST, problem=UNREACHABLE) == -1 and check_problem(host=WEBSERVER_HOST, problem=UNREACHABLE) == -1:
            status = UP
        else:
            status = DOWN
    elif service == IAAS:
        # .......
        pass
    elif service == PAAS:
        # .......
        pass
    elif service == BAAS:
        # .......
        pass
    return status


def get_service_current_status(service: str) -> dict:
    services_status = load_json(SERVICES_STATUS_PATH)
    service_status = services_status.get(service, {"status": "UNKOWN", "timestamp": None})
    return service_status



def empty_cache():
    save_json(data={}, file_path=PROBLEMS_PATH)
    save_json(data={}, file_path=SERVICES_STATUS_PATH)
    save_json(data={}, file_path=SERVICES_DOWNTIMES_PATH)