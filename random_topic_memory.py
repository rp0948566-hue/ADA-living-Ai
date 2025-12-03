"""
Random Topic Memory System
- Generates random topics dynamically
- Stores topics in persistent JSON files
- Auto-updates and evolves memory
- Integrates with agent.py for continuous learning
"""

import json
import os
import random
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import time

# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory", "topics")
MEMORY_INDEX_FILE = os.path.join(MEMORY_DIR, "topics_index.json")
MEMORY_STATS_FILE = os.path.join(MEMORY_DIR, "topics_stats.json")
MEMORY_EVOLUTION_FILE = os.path.join(MEMORY_DIR, "evolution_history.json")

# Ensure memory directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)

# Topic categories for random generation
TOPIC_CATEGORIES = {
    "technology": [
        "artificial intelligence", "machine learning", "neural networks",
        "cloud computing", "cybersecurity", "blockchain", "quantum computing",
        "IoT devices", "robotics", "autonomous systems", "APIs", "databases",
        "data science", "distributed systems", "microservices"
    ],
    "science": [
        "physics", "chemistry", "biology", "astronomy", "genetics",
        "neuroscience", "environmental science", "quantum mechanics",
        "relativity", "thermodynamics", "molecular biology"
    ],
    "history": [
        "ancient civilizations", "medieval period", "renaissance", "industrial revolution",
        "world wars", "cold war", "space race", "cultural movements", "revolutions"
    ],
    "geography": [
        "mountains", "oceans", "deserts", "rainforests", "climate zones",
        "countries", "cities", "landmarks", "natural wonders"
    ],
    "business": [
        "startups", "marketing", "finance", "economics", "leadership",
        "entrepreneurship", "supply chain", "e-commerce", "cryptocurrency"
    ],
    "arts": [
        "painting", "sculpture", "music", "literature", "film",
        "architecture", "photography", "dance", "theater"
    ],
    "sports": [
        "football", "basketball", "tennis", "cricket", "Olympics",
        "martial arts", "esports", "extreme sports"
    ],
    "health": [
        "medicine", "nutrition", "fitness", "mental health", "vaccines",
        "disease prevention", "exercise", "sleep science"
    ],
    "philosophy": [
        "ethics", "metaphysics", "epistemology", "logic", "existentialism",
        "stoicism", "pragmatism"
    ],
    "education": [
        "learning methods", "pedagogy", "online education", "student success",
        "STEM education", "language learning"
    ]
}

# ═════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def _load_json_safe(filepath: str, default=None) -> Dict:
    """Safely load JSON file with fallback"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Could not load {filepath}: {e}")
    return default if default is not None else {}


def _save_json_safe(filepath: str, data: Dict) -> bool:
    """Safely save JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"❌ Failed to save {filepath}: {e}")
        return False


def generate_random_topic() -> str:
    """Generate a random topic from categories"""
    category = random.choice(list(TOPIC_CATEGORIES.keys()))
    topic = random.choice(TOPIC_CATEGORIES[category])
    return f"{topic} ({category})"


def generate_topic_hash(topic: str) -> str:
    """Generate unique hash for a topic"""
    return hashlib.md5(topic.encode()).hexdigest()[:8]


def save_topic_to_memory(topic: str, metadata: Optional[Dict] = None) -> Dict:
    """Save a random topic to persistent memory"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    
    topic_hash = generate_topic_hash(topic)
    timestamp = datetime.datetime.now().isoformat()
    
    topic_data = {
        "id": topic_hash,
        "topic": topic,
        "timestamp": timestamp,
        "created_date": datetime.date.today().isoformat(),
        "metadata": metadata or {},
        "interactions": 0,
        "relevance_score": 0.5
    }
    
    # Add to index if not exists
    if topic_hash not in index:
        index[topic_hash] = topic_data
        _save_json_safe(MEMORY_INDEX_FILE, index)
        _update_stats("topic_created")
        print(f"✅ Topic saved: {topic}")
    
    return topic_data


def get_random_saved_topic() -> Optional[Dict]:
    """Get a random topic from saved memory"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    
    if not index:
        return None
    
    # Select random topic and update interaction count
    topic_hash = random.choice(list(index.keys()))
    topic_data = index[topic_hash]
    topic_data["interactions"] += 1
    
    _save_json_safe(MEMORY_INDEX_FILE, index)
    return topic_data


def get_topics_by_count(limit: int = 10) -> List[Dict]:
    """Get topics sorted by interaction count"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    
    topics = sorted(
        index.values(),
        key=lambda x: x.get("interactions", 0),
        reverse=True
    )
    
    return topics[:limit]


def search_topics(keyword: str) -> List[Dict]:
    """Search topics by keyword"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    keyword_lower = keyword.lower()
    
    matching = [
        topic for topic in index.values()
        if keyword_lower in topic.get("topic", "").lower()
    ]
    
    return matching


def update_topic_relevance(topic_hash: str, score: float) -> bool:
    """Update relevance score for a topic (0.0-1.0)"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    
    if topic_hash in index:
        index[topic_hash]["relevance_score"] = max(0.0, min(1.0, score))
        _save_json_safe(MEMORY_INDEX_FILE, index)
        return True
    
    return False


def _update_stats(action: str) -> None:
    """Update system statistics"""
    stats = _load_json_safe(MEMORY_STATS_FILE, {
        "total_topics": 0,
        "total_interactions": 0,
        "last_updated": None
    })
    
    stats["last_updated"] = datetime.datetime.now().isoformat()
    
    if action == "topic_created":
        stats["total_topics"] = stats.get("total_topics", 0) + 1
    elif action == "interaction":
        stats["total_interactions"] = stats.get("total_interactions", 0) + 1
    
    _save_json_safe(MEMORY_STATS_FILE, stats)


def auto_update_memory() -> Dict:
    """Auto-update memory with optimization and cleanup"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    
    update_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "topics_optimized": 0,
        "topics_pruned": 0,
        "duplicates_removed": 0
    }
    
    # Remove topics not accessed in 30 days (optional)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
    
    for topic_hash, topic_data in list(index.items()):
        try:
            created_date = datetime.datetime.fromisoformat(topic_data["timestamp"])
            
            # Auto-increase relevance based on interactions
            if topic_data.get("interactions", 0) > 5:
                topic_data["relevance_score"] = min(1.0, topic_data.get("relevance_score", 0.5) + 0.05)
                update_report["topics_optimized"] += 1
            
            # Optional: Remove stale topics
            if created_date < cutoff_date and topic_data.get("interactions", 0) == 0:
                del index[topic_hash]
                update_report["topics_pruned"] += 1
        
        except Exception as e:
            print(f"⚠️ Error updating topic {topic_hash}: {e}")
    
    _save_json_safe(MEMORY_INDEX_FILE, index)
    _save_json_safe(MEMORY_EVOLUTION_FILE, update_report)
    
    return update_report


def get_evolution_history() -> List[Dict]:
    """Get history of memory evolution and updates"""
    history = _load_json_safe(MEMORY_EVOLUTION_FILE, {})
    return history if isinstance(history, list) else [history]


def get_memory_stats() -> Dict:
    """Get current memory statistics"""
    index = _load_json_safe(MEMORY_INDEX_FILE, {})
    stats = _load_json_safe(MEMORY_STATS_FILE, {})
    
    return {
        "total_topics_stored": len(index),
        "total_interactions": sum(t.get("interactions", 0) for t in index.values()),
        "memory_file_path": MEMORY_INDEX_FILE,
        "last_updated": stats.get("last_updated"),
        "top_topics": get_topics_by_count(5)
    }


# ═════════════════════════════════════════════════════════════════════════════
# AUTO-UPGRADE & SELF-EVOLUTION SYSTEM
# ═════════════════════════════════════════════════════════════════════════════

class MemoryEvolutionEngine:
    """Continuously evolves and upgrades the memory system"""
    
    def __init__(self, auto_upgrade_interval: int = 3600):
        """
        Initialize evolution engine
        
        Args:
            auto_upgrade_interval: Seconds between auto-updates (default 1 hour)
        """
        self.auto_upgrade_interval = auto_upgrade_interval
        self.is_running = False
        self.evolution_thread = None
    
    def start_background_evolution(self) -> threading.Thread:
        """Start automatic memory evolution in background"""
        if self.is_running:
            print("⚠️ Evolution engine already running")
            return self.evolution_thread
        
        self.is_running = True
        self.evolution_thread = threading.Thread(
            target=self._evolution_loop,
            daemon=True
        )
        self.evolution_thread.start()
        print(f"✅ Memory evolution engine started (update every {self.auto_upgrade_interval}s)")
        
        return self.evolution_thread
    
    def stop_background_evolution(self) -> None:
        """Stop background evolution"""
        self.is_running = False
        print("🛑 Memory evolution engine stopped")
    
    def _evolution_loop(self) -> None:
        """Continuous evolution loop running in background"""
        while self.is_running:
            try:
                time.sleep(self.auto_upgrade_interval)
                
                if self.is_running:
                    print("\n🔄 Auto-updating memory system...")
                    report = auto_update_memory()
                    print(f"   ├─ Topics optimized: {report['topics_optimized']}")
                    print(f"   ├─ Topics pruned: {report['topics_pruned']}")
                    print(f"   └─ Timestamp: {report['timestamp']}")
                    
            except Exception as e:
                print(f"❌ Error in evolution loop: {e}")
    
    def manual_upgrade(self) -> Dict:
        """Perform manual memory upgrade"""
        print("⚙️ Performing manual memory upgrade...")
        report = auto_update_memory()
        print(f"✅ Memory upgraded successfully")
        return report


# ═════════════════════════════════════════════════════════════════════════════
# LIVEKIT AGENT TOOLS INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════

try:
    from livekit.agents import function_tool
    
    # Generate a random topic and save it to memory
    @function_tool
    async def generate_and_save_random_topic() -> str:
        """Generate a random topic and save to persistent memory"""
        topic = generate_random_topic()
        save_topic_to_memory(topic)
        return f"Generated and saved topic: {topic}"
    
    
    # Get a random topic from memory
    @function_tool
    async def get_random_topic_from_memory() -> str:
        """Retrieve a random topic from saved memory"""
        topic_data = get_random_saved_topic()
        
        if topic_data:
            return f"Random topic: {topic_data['topic']} (stored on {topic_data['timestamp']})"
        else:
            return "No topics in memory yet. Generate one first!"
    
    
    # Search for topics by keyword
    @function_tool
    async def search_topics_memory(keyword: str) -> str:
        """Search for topics by keyword in memory"""
        results = search_topics(keyword)
        
        if results:
            topics_str = "\n".join([f"• {t['topic']}" for t in results[:5]])
            return f"Found {len(results)} topics:\n{topics_str}"
        else:
            return f"No topics found matching '{keyword}'"
    
    
    # Get memory statistics and status
    @function_tool
    async def get_memory_status() -> str:
        """Get current memory statistics"""
        stats = get_memory_stats()
        
        return f"""📊 Memory Status:
• Total topics stored: {stats['total_topics_stored']}
• Total interactions: {stats['total_interactions']}
• Last updated: {stats['last_updated']}
• Memory location: {stats['memory_file_path']}
"""
    
    
    # Perform auto-update on memory system
    @function_tool
    async def trigger_memory_auto_update() -> str:
        """Trigger auto-update of memory system"""
        report = auto_update_memory()
        
        return f"""Memory Auto-Update Complete:
• Topics optimized: {report['topics_optimized']}
• Topics pruned: {report['topics_pruned']}
• Duplicates removed: {report['duplicates_removed']}
• Time: {report['timestamp']}"""
    
    
    # Create tool list for agent
    TOPIC_MEMORY_TOOLS = [
        generate_and_save_random_topic,
        get_random_topic_from_memory,
        search_topics_memory,
        get_memory_status,
        trigger_memory_auto_update
    ]

except ImportError:
    print("⚠️ LiveKit agents not available - tools registration skipped")
    TOPIC_MEMORY_TOOLS = []


# ═════════════════════════════════════════════════════════════════════════════
# DEMONSTRATION & TESTING
# ═════════════════════════════════════════════════════════════════════════════

def demo_random_topic_system():
    """Demonstrate the random topic memory system"""
    print("\n" + "="*70)
    print("🧠 RANDOM TOPIC MEMORY SYSTEM DEMO")
    print("="*70 + "\n")
    
    # 1. Generate and save topics
    print("1️⃣  GENERATING RANDOM TOPICS")
    print("-" * 70)
    for i in range(5):
        topic = generate_random_topic()
        save_topic_to_memory(topic, metadata={"source": "demo", "batch": 1})
        print(f"   {i+1}. {topic}")
    
    # 2. Get memory stats
    print("\n2️⃣  MEMORY STATISTICS")
    print("-" * 70)
    stats = get_memory_stats()
    print(f"   Total topics: {stats['total_topics_stored']}")
    print(f"   Total interactions: {stats['total_interactions']}")
    print(f"   Storage location: {stats['memory_file_path']}")
    
    # 3. Search topics
    print("\n3️⃣  SEARCHING TOPICS")
    print("-" * 70)
    results = search_topics("technology")
    print(f"   Found {len(results)} topics containing 'technology':")
    for topic in results[:3]:
        print(f"   • {topic['topic']}")
    
    # 4. Get top topics
    print("\n4️⃣  TOP TOPICS BY INTERACTION")
    print("-" * 70)
    top = get_topics_by_count(3)
    for topic in top:
        print(f"   • {topic['topic']} (interactions: {topic['interactions']})")
    
    # 5. Auto-update
    print("\n5️⃣  MEMORY AUTO-UPDATE")
    print("-" * 70)
    report = auto_update_memory()
    print(f"   Topics optimized: {report['topics_optimized']}")
    print(f"   Topics pruned: {report['topics_pruned']}")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run demo
    demo_random_topic_system()
    
    # Start evolution engine for 10 seconds (demo)
    print("\n⏱️  Starting evolution engine (will run in background)...")
    engine = MemoryEvolutionEngine(auto_upgrade_interval=10)
    engine.start_background_evolution()
    
    print("Waiting 15 seconds to see auto-update in action...")
    time.sleep(15)
    
    engine.stop_background_evolution()
    print("\n✅ Demo complete!")
