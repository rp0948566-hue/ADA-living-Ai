import json
import os
from datetime import datetime

LOG_FILE = 'conversation_history.json'

def initialize_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

def log_conversation(user_message, ai_response=None, metadata={}):
    initialize_log()
    
    conversation = {
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'ai_response': ai_response,
        'metadata': metadata
    }
    
    with open(LOG_FILE, 'r+') as f:
        data = json.load(f)
        data.append(conversation)
        f.seek(0)
        json.dump(data, f, indent=4)

def update_last_entry(ai_response):
    if not os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, 'r+') as f:
        data = json.load(f)
        if data:
            data[-1]['ai_response'] = ai_response
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

def get_conversation_history(limit=None):
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, 'r') as f:
        data = json.load(f)
    
    if limit:
        return data[-limit:]
    return data
