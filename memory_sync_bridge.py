"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                    🔗 MEMORY SYNC BRIDGE - INTEGRATION LAYER                  ║
║                                                                               ║
║         • Syncs backend learning with agent.py                               ║
║         • Thread-safe memory access across terminals                         ║
║         • Auto-updates agent with new knowledge                              ║
║         • Maintains memory consistency                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MEMORY_BRIDGE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memory/memory_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Memory paths
MEMORY_DIR = Path("memory")
BACKEND_MEMORY = MEMORY_DIR / "backend_intelligence.json"
AGENT_MEMORY = MEMORY_DIR / "memory.json"
SHARED_KNOWLEDGE = MEMORY_DIR / "shared_knowledge.json"
SYNC_STATUS = MEMORY_DIR / "sync_status.json"

# Thread safety
memory_lock = threading.RLock()


class MemorySyncBridge:
    """Synchronizes memory between backend and agent"""
    
    def __init__(self):
        self.sync_count = 0
        self.last_sync = None
        self.agent_updated = False
        self._initialize_shared_knowledge()
        
    def _initialize_shared_knowledge(self):
        """Initialize shared knowledge file"""
        if not SHARED_KNOWLEDGE.exists():
            initial_data = {
                "created": datetime.now().isoformat(),
                "last_sync": None,
                "backend_facts": {},
                "agent_facts": {},
                "merged_knowledge": {},
                "sync_history": []
            }
            with open(SHARED_KNOWLEDGE, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def _load_json_safe(self, file_path: Path) -> Dict:
        """Safely load JSON with lock"""
        with memory_lock:
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        return {}
    
    def _save_json_safe(self, file_path: Path, data: Dict):
        """Safely save JSON with lock"""
        with memory_lock:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error saving {file_path}: {e}")
    
    def sync_backend_to_shared(self):
        """Sync backend learning to shared knowledge"""
        logger.info("🔄 Syncing backend intelligence to shared knowledge...")
        
        backend_memory = self._load_json_safe(BACKEND_MEMORY)
        shared_knowledge = self._load_json_safe(SHARED_KNOWLEDGE)
        
        if backend_memory and backend_memory.get("learned_facts"):
            shared_knowledge["backend_facts"] = backend_memory.get("learned_facts", {})
            shared_knowledge["backend_optimizations"] = backend_memory.get("optimizations", {})
            
            logger.info(f"✅ Synced {len(backend_memory.get('learned_facts', {}))} learned facts")
        
        shared_knowledge["last_sync"] = datetime.now().isoformat()
        self._save_json_safe(SHARED_KNOWLEDGE, shared_knowledge)
        self.last_sync = datetime.now()
    
    def sync_agent_to_shared(self):
        """Sync agent memory to shared knowledge"""
        logger.info("🔄 Syncing agent memory to shared knowledge...")
        
        agent_memory = self._load_json_safe(AGENT_MEMORY)
        shared_knowledge = self._load_json_safe(SHARED_KNOWLEDGE)
        
        if agent_memory and agent_memory.get("facts"):
            shared_knowledge["agent_facts"] = agent_memory.get("facts", {})
            
            logger.info(f"✅ Synced {len(agent_memory.get('facts', {}))} agent facts")
        
        shared_knowledge["last_sync"] = datetime.now().isoformat()
        self._save_json_safe(SHARED_KNOWLEDGE, shared_knowledge)
    
    def merge_knowledge(self):
        """Merge backend and agent knowledge"""
        logger.info("🧠 Merging backend and agent knowledge...")
        
        shared_knowledge = self._load_json_safe(SHARED_KNOWLEDGE)
        
        merged = {}
        
        # Add backend facts
        backend_facts = shared_knowledge.get("backend_facts", {})
        for key, value in backend_facts.items():
            merged[key] = {
                "source": "backend",
                "data": value,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add agent facts
        agent_facts = shared_knowledge.get("agent_facts", {})
        for key, value in agent_facts.items():
            if key not in merged:
                merged[key] = {
                    "source": "agent",
                    "data": value,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                merged[key]["sources"] = ["backend", "agent"]
        
        shared_knowledge["merged_knowledge"] = merged
        logger.info(f"✅ Merged {len(merged)} total knowledge entries")
        
        self._save_json_safe(SHARED_KNOWLEDGE, shared_knowledge)
    
    def update_agent_with_knowledge(self):
        """Update agent memory with shared knowledge"""
        logger.info("🚀 Updating agent with backend knowledge...")
        
        shared_knowledge = self._load_json_safe(SHARED_KNOWLEDGE)
        agent_memory = self._load_json_safe(AGENT_MEMORY)
        
        merged_knowledge = shared_knowledge.get("merged_knowledge", {})
        
        if not agent_memory:
            agent_memory = {"facts": {}, "conversation": []}
        
        # Add merged knowledge to agent
        added = 0
        for key, value in merged_knowledge.items():
            if key not in agent_memory.get("facts", {}):
                agent_memory["facts"][key] = value
                added += 1
        
        # Update timestamp
        agent_memory["last_backend_sync"] = datetime.now().isoformat()
        agent_memory["knowledge_sources"] = "merged_backend_agent"
        
        self._save_json_safe(AGENT_MEMORY, agent_memory)
        logger.info(f"✅ Agent updated with {added} new knowledge entries")
        self.agent_updated = True
    
    def get_backend_improvements(self) -> Dict:
        """Get improvements that should be applied to agent"""
        backend_memory = self._load_json_safe(BACKEND_MEMORY)
        optimizations = backend_memory.get("optimizations", {})
        
        logger.info(f"📊 Retrieved {len(optimizations)} improvements from backend")
        return optimizations
    
    def apply_backend_improvements(self, improvements: Dict):
        """Apply backend improvements to agent's decision making"""
        logger.info("⚙️  Applying backend improvements to agent...")
        
        agent_memory = self._load_json_safe(AGENT_MEMORY)
        
        if "applied_improvements" not in agent_memory:
            agent_memory["applied_improvements"] = []
        
        for key, improvement in improvements.items():
            agent_memory["applied_improvements"].append({
                "improvement_id": key,
                "topic": improvement.get("topic"),
                "applied_at": datetime.now().isoformat(),
                "source": "backend_learning"
            })
        
        self._save_json_safe(AGENT_MEMORY, agent_memory)
        logger.info(f"✅ Applied {len(improvements)} improvements to agent")
    
    def save_sync_status(self, status: str, details: str = ""):
        """Save sync status"""
        sync_data = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "details": details,
            "sync_count": self.sync_count,
            "agent_updated": self.agent_updated
        }
        
        status_data = self._load_json_safe(SYNC_STATUS)
        if "syncs" not in status_data:
            status_data["syncs"] = []
        
        status_data["syncs"].append(sync_data)
        status_data["last_sync"] = sync_data
        
        self._save_json_safe(SYNC_STATUS, status_data)
    
    def run_continuous_sync(self, interval: int = 15):
        """Run continuous synchronization"""
        logger.info(f"\n╔════════════════════════════════════════════════╗")
        logger.info(f"║  🔗 MEMORY SYNC BRIDGE STARTED                  ║")
        logger.info(f"║  Sync interval: {interval} seconds")
        logger.info(f"╚════════════════════════════════════════════════╝\n")
        
        try:
            while True:
                try:
                    # Sync both directions
                    self.sync_backend_to_shared()
                    self.sync_agent_to_shared()
                    
                    # Merge knowledge
                    self.merge_knowledge()
                    
                    # Update agent with knowledge
                    self.update_agent_with_knowledge()
                    
                    # Apply improvements
                    improvements = self.get_backend_improvements()
                    if improvements:
                        self.apply_backend_improvements(improvements)
                    
                    # Save status
                    self.sync_count += 1
                    self.save_sync_status("success", 
                        f"Synced {len(improvements)} improvements, merged knowledge from both sources")
                    
                    logger.info(f"\n✨ Sync cycle #{self.sync_count} complete!")
                    logger.info(f"   Agent updated: {self.agent_updated}")
                    logger.info(f"   Improvements applied: {len(improvements)}\n")
                    
                except Exception as e:
                    logger.error(f"Error in sync cycle: {e}", exc_info=True)
                    self.save_sync_status("error", str(e))
                
                # Wait before next sync
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Memory sync bridge shutting down...")
            self.save_sync_status("shutdown", "Graceful shutdown")


def get_shared_knowledge() -> Dict:
    """Get current shared knowledge (for agent.py use)"""
    bridge = MemorySyncBridge()
    return bridge._load_json_safe(SHARED_KNOWLEDGE)


def get_backend_facts() -> Dict:
    """Get only backend learned facts (for agent.py use)"""
    knowledge = get_shared_knowledge()
    return knowledge.get("backend_facts", {})


def get_merged_knowledge() -> Dict:
    """Get merged knowledge from both sources (for agent.py use)"""
    knowledge = get_shared_knowledge()
    return knowledge.get("merged_knowledge", {})


def apply_improvements_to_agent(improvements: Dict) -> bool:
    """Helper function for agent.py to apply improvements"""
    try:
        bridge = MemorySyncBridge()
        bridge.apply_backend_improvements(improvements)
        return True
    except Exception as e:
        logger.error(f"Error applying improvements: {e}")
        return False


# LiveKit function tools for agent integration
from livekit.agents import function_tool


@function_tool
async def get_backend_knowledge() -> str:
    """Get latest backend learned knowledge"""
    facts = get_backend_facts()
    if facts:
        summary = "Backend has learned:\n"
        for key, value in list(facts.items())[:5]:
            summary += f"- {key}\n"
        return summary
    return "No backend knowledge available yet."


@function_tool
async def get_merged_intelligence() -> str:
    """Get merged knowledge from backend and agent"""
    merged = get_merged_knowledge()
    if merged:
        return f"Available knowledge sources: {len(merged)} entries from backend and agent combined."
    return "Knowledge merge in progress..."


def main():
    """Entry point for memory sync bridge"""
    logger.info("Initializing memory sync bridge...")
    bridge = MemorySyncBridge()
    
    try:
        bridge.run_continuous_sync(interval=15)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("\nMemory sync bridge shutdown complete.")


if __name__ == "__main__":
    main()
