# from change_stream.db import events_collection
from db.config import events_collection
from change_stream.common import remove_problem, add_problem, check_service_status, update_service_status, empty_cache, get_service_current_status
from change_stream.constants import *


empty_cache()

services = [SAAS]

def handle_event_change(change: dict) -> None:
    """Handle changes in event stream."""
    event = change['fullDocument']
    if event['value'] == 0:
        remove_problem(event)
    elif event["value"] == 1:
        add_problem(event)

    for service in services:
        service_status = get_service_current_status(service=service)
        if service_status["status"] == MAINTENANCE:
            print(f"Skipping updates .... service: {service} in {MAINTENANCE} mode.")
            continue
        # TODO: Add condition here, only recheck the new status and trigger the update if the event may change it
        if True:
            status = check_service_status(service=SAAS)
            update_service_status(service=SAAS, status=status)



# Watch the events collection for changes
with events_collection.watch() as stream:
    print('Watching for streams...')
    for change in stream:
        if change['operationType'] == 'insert':
            handle_event_change(change)