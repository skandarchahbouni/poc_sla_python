from change_stream.common import update_service_status, check_service_status
from datetime import datetime

def enter_maintenance_mode(description: str, related_services: list, timestamp: datetime):
    print(f"Entering Maintenance mode: {description}")
    for service in related_services:
        update_service_status(service=service, status="MAINTENANCE")

def exist_maintenance_mode(description: str, related_services: list, timestamp: datetime):
    print(f"Exiting maintenance mode: {description}")
    for service in related_services:
        # Check the status of the service 
        status = check_service_status(service=service)
        update_service_status(service=service, status=status)

