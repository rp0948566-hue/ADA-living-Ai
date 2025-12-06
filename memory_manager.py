import json
from typing import Dict, Any, List
from datetime import datetime

class MemoryManager:
    def __init__(self, storage_file: str = "ada_memory.json"):
        self.storage_file = storage_file
        self.user_data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}, "global_history": []}

    def _save(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.user_data, f, indent=2)

    def save_user_data(self, user_id: str, data: Dict):
        self.user_data.setdefault("users", {})[user_id] = {**data, "last_updated": datetime.now().isoformat()}
        self._save()

    def load_user_data(self, user_id: str = "default") -> Dict:
        return self.user_data.get("users", {}).get(user_id, {})

    def save_interaction(self, user_input: str, response: str, emotion: str, user_id: str = "default"):
        timestamp = datetime.now().isoformat()
        interaction = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": response,
            "emotion": emotion
        }
        self.user_data.setdefault("global_history", []).append(interaction)
        # Prune history to last 100 for efficiency
        if len(self.user_data["global_history"]) > 100:
            self.user_data["global_history"] = self.user_data["global_history"][-100:]
        self._save()

    def get_conversation_history(self, user_id: str = "default", limit: int = 20) -> List[Dict]:
        # Filter history by user if possible, else global
        history = self.user_data.get("global_history", [])
        return history[-limit:]
