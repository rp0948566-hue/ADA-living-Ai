import json
import time
from ada_time import get_current_time, TIME_BACKEND_FILE

def check_time_accuracy():
    """Cross-check time from ada_time.py with system time."""
    ada_time = get_current_time()
    system_time = time.time()

    # Load backend time
    try:
        with open(TIME_BACKEND_FILE, 'r') as f:
            backend_data = json.load(f)
        backend_timestamp = backend_data.get('timestamp', 0)
    except FileNotFoundError:
        backend_timestamp = 0

    # Check discrepancies
    ada_timestamp = ada_time.timestamp()
    discrepancy_ada_system = abs(ada_timestamp - system_time)
    discrepancy_backend_system = abs(backend_timestamp - system_time)

    print(f"ADA Time: {ada_time}")
    print(f"System Time: {time.ctime(system_time)}")
    print(f"Backend Time: {backend_timestamp}")

    if discrepancy_ada_system > 60:  # More than 1 minute
        print("⚠️ Alert: Significant discrepancy between ADA time and system time!")
    if discrepancy_backend_system > 60:
        print("⚠️ Alert: Significant discrepancy between backend time and system time!")

    return {
        'ada_time': ada_time,
        'system_time': system_time,
        'backend_time': backend_timestamp,
        'discrepancy_ada_system': discrepancy_ada_system,
        'discrepancy_backend_system': discrepancy_backend_system
    }

if __name__ == "__main__":
    check_time_accuracy()
