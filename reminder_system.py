import json
import os
from datetime import datetime
import dateparser

class ReminderSystem:
    def __init__(self, file_path='reminders.json'):
        self.file_path = file_path
        self.reminders = self.load_reminders()

    def add_reminder(self, message, time_str):
        due_time = dateparser.parse(time_str)
        if not due_time:
            return "Could not understand the time. Please try again."

        reminder = {
            'id': len(self.reminders) + 1,
            'message': message,
            'due_time': due_time.isoformat()
        }
        self.reminders.append(reminder)
        self.save_reminders()
        return f"Reminder set for {message} at {due_time.strftime('%Y-%m-%d %H:%M:%S')}"

    def check_reminders(self):
        now = datetime.now()
        due_reminders = []
        for reminder in self.reminders:
            due_time = datetime.fromisoformat(reminder['due_time'])
            if now >= due_time:
                due_reminders.append(reminder)
        return due_reminders

    def remove_reminder(self, reminder_id):
        self.reminders = [r for r in self.reminders if r['id'] != reminder_id]
        self.save_reminders()

    def save_reminders(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.reminders, f, indent=4)

    def load_reminders(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []
