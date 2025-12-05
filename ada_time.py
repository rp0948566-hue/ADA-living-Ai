import json
import os
from datetime import datetime

# Backend file for storing time data
TIME_BACKEND_FILE = "time_backend.json"

def get_current_time():
    """Fetch the current time from the system (Windows laptop)."""
    return datetime.now()

def update_backend_time():
    """Update the backend file with the current time."""
    current_time = get_current_time()
    time_data = {
        "current_time": current_time.isoformat(),
        "timestamp": current_time.timestamp()
    }
    with open(TIME_BACKEND_FILE, 'w') as f:
        json.dump(time_data, f, indent=4)
    print(f"Backend time updated: {current_time}")

def get_time_greeting():
    """Get the time-based greeting in Hindi and English."""
    current_time = get_current_time()
    hour = current_time.hour

    # Update backend time
    update_backend_time()

    # Categorize time
    if 6 <= hour < 12:
        greeting = "Good morning! सुबह का समय है।"
    elif 12 <= hour < 17:
        greeting = "Good afternoon! दोपहर का समय है।"
    elif 17 <= hour < 21:
        greeting = "Good evening! शाम का समय है।"
    else:
        greeting = "Good night! रात का समय है।"

    return greeting

if __name__ == "__main__":
    print(get_time_greeting())
