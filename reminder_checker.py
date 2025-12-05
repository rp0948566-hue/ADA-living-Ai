import time
from reminder_system import ReminderSystem
import ollama_integration

def main():
    reminder_system = ReminderSystem()
    while True:
        due_reminders = reminder_system.check_reminders()
        for reminder in due_reminders:
            response = ollama_integration.generate_response(f"Alert: Reminder for {reminder['message']}")
            print(response)
            reminder_system.remove_reminder(reminder['id'])
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()
