"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║              🧠 BACKEND LEARNING ENGINE - AUTONOMOUS EVOLUTION                ║
║                                                                               ║
║         • Runs independently in background terminal                          ║
║         • Searches files randomly & collects important information           ║
║         • Self-learns, self-updates, self-improves continuously              ║
║         • Applies improvements automatically to permanent memory             ║
║         • Zero interference with agent.py operations                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import json
import time
import random
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import re

# Setup logging for backend
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [BACKEND_LEARNING] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memory/backend_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Memory paths
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

BACKEND_MEMORY = MEMORY_DIR / "backend_intelligence.json"
LEARNING_LOG = MEMORY_DIR / "learning_evolution.json"
APPLIED_IMPROVEMENTS = MEMORY_DIR / "applied_improvements.json"
BRAIN_DECISIONS = MEMORY_DIR / "brain_decisions.json"

# Configuration
SCAN_INTERVAL = 30  # Scan files every 30 seconds
MAX_FILES_PER_SCAN = 10  # Check up to 10 random files per scan
LEARNING_THRESHOLD = 0.7  # Confidence threshold for applying learning
MIN_INFO_LENGTH = 20  # Minimum characters to consider as important


class BrainEngine:
    """AI Brain for autonomous decision making and topic selection"""
    
    def __init__(self):
        self.decisions = self._load_decisions()
        self.preferences = {}
        self.learning_topics = set()
        
    def _load_decisions(self) -> Dict:
        """Load previous decision history"""
        if BRAIN_DECISIONS.exists():
            try:
                with open(BRAIN_DECISIONS, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"history": [], "patterns": {}}
        return {"history": [], "patterns": {}}
    
    def _save_decisions(self):
        """Save decision history"""
        with open(BRAIN_DECISIONS, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, indent=2, ensure_ascii=False)
    
    def choose_random_topic(self) -> str:
        """AI chooses random topic to learn about"""
        topics = [
            "system_optimization",
            "user_behavior",
            "code_patterns",
            "api_integration",
            "performance_metrics",
            "error_patterns",
            "learning_algorithms",
            "memory_optimization",
            "decision_patterns",
            "improvement_strategies",
            "automation_techniques",
            "knowledge_synthesis",
            "problem_solving",
            "pattern_recognition"
        ]
        
        selected = random.choice(topics)
        logger.info(f"🧠 BRAIN DECISION: Selected topic = {selected}")
        
        self.decisions["history"].append({
            "timestamp": datetime.now().isoformat(),
            "topic": selected,
            "status": "active"
        })
        self._save_decisions()
        
        return selected
    
    def analyze_learning_value(self, content: str, topic: str) -> float:
        """Analyze how valuable the content is for learning"""
        score = 0.0
        
        # Check for relevance
        if topic.lower() in content.lower():
            score += 0.3
        
        # Check for technical depth
        if any(keyword in content.lower() for keyword in 
               ['function', 'class', 'import', 'def', 'async', 'await', 'memory', 'data']):
            score += 0.2
        
        # Check for practical information
        if any(keyword in content.lower() for keyword in 
               ['configuration', 'setup', 'implement', 'error', 'fix', 'optimize']):
            score += 0.25
        
        # Length consideration
        if len(content) > 500:
            score += 0.15
        elif len(content) > 200:
            score += 0.1
        
        # Uniqueness (simplified)
        if len(set(content.split())) > 20:
            score += 0.1
        
        return min(score, 1.0)
    
    def should_apply_improvement(self, confidence: float) -> bool:
        """Decide if improvement should be applied permanently"""
        return confidence >= LEARNING_THRESHOLD


class IntelligenceEngine:
    """Backend intelligence system for continuous learning"""
    
    def __init__(self):
        self.memory = self._load_backend_memory()
        self.learning_log = self._load_learning_log()
        self.brain = BrainEngine()
        self.improvements_applied = 0
        self.files_scanned = 0
        
    def _load_backend_memory(self) -> Dict:
        """Load backend memory"""
        if BACKEND_MEMORY.exists():
            try:
                with open(BACKEND_MEMORY, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"learned_facts": {}, "patterns": {}, "optimizations": {}}
        return {"learned_facts": {}, "patterns": {}, "optimizations": {}}
    
    def _save_backend_memory(self):
        """Save backend memory"""
        with open(BACKEND_MEMORY, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _load_learning_log(self) -> List:
        """Load learning evolution log"""
        if LEARNING_LOG.exists():
            try:
                with open(LEARNING_LOG, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_learning_log(self):
        """Save learning log"""
        with open(LEARNING_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.learning_log, f, indent=2, ensure_ascii=False)
    
    def extract_important_info(self, content: str, topic: str) -> Dict[str, Any]:
        """Extract important information from file content"""
        important = {
            "definitions": [],
            "patterns": [],
            "configurations": [],
            "functions": [],
            "best_practices": []
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract definitions
            if line.startswith('def ') or line.startswith('class '):
                important["definitions"].append(line[:100])
            
            # Extract imports and configurations
            elif line.startswith('import ') or line.startswith('from '):
                important["configurations"].append(line[:100])
            
            # Extract comments with important info
            elif '#' in line and len(line) > MIN_INFO_LENGTH:
                important["best_practices"].append(line[line.index('#'):100])
            
            # Extract patterns
            elif '=' in line and len(line) > MIN_INFO_LENGTH:
                important["patterns"].append(line[:100])
        
        return important
    
    def get_random_files(self, max_files: int = MAX_FILES_PER_SCAN) -> List[Path]:
        """Get random Python files to scan"""
        workspace = Path(".")
        py_files = list(workspace.glob("**/*.py"))
        
        # Exclude venv, pycache, and certain files
        py_files = [f for f in py_files if not any(x in str(f) for x in 
                    ['.venv', '__pycache__', '.git', 'test_'])]
        
        return random.sample(py_files, min(max_files, len(py_files)))
    
    def scan_and_learn(self):
        """Main learning cycle - scans random files and learns"""
        logger.info("\n" + "="*80)
        logger.info("🧠 STARTING AUTONOMOUS LEARNING CYCLE")
        logger.info("="*80)
        
        # Brain chooses topic
        current_topic = self.brain.choose_random_topic()
        
        # Get random files
        files_to_scan = self.get_random_files()
        logger.info(f"📁 Scanning {len(files_to_scan)} random files for topic: {current_topic}")
        
        for file_path in files_to_scan:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Analyze learning value
                value_score = self.brain.analyze_learning_value(content, current_topic)
                
                if value_score > 0.3:
                    logger.info(f"✨ Found valuable content in {file_path.name} (score: {value_score:.2f})")
                    
                    # Extract important information
                    important_info = self.extract_important_info(content, current_topic)
                    
                    # Store in memory
                    key = f"{current_topic}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
                    self.memory["learned_facts"][key] = {
                        "source": str(file_path),
                        "topic": current_topic,
                        "timestamp": datetime.now().isoformat(),
                        "value_score": value_score,
                        "information": important_info,
                        "confidence": value_score
                    }
                    
                    # Log learning
                    self.learning_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "learned",
                        "source": str(file_path),
                        "topic": current_topic,
                        "value_score": value_score
                    })
                    
                    # Check if should apply improvement
                    if self.brain.should_apply_improvement(value_score):
                        self._apply_improvement(key, current_topic, important_info)
                
                self.files_scanned += 1
                
            except Exception as e:
                logger.warning(f"⚠️  Error scanning {file_path}: {e}")
        
        self._save_backend_memory()
        self._save_learning_log()
        
        logger.info(f"\n✅ Learning cycle complete!")
        logger.info(f"   Files scanned: {self.files_scanned}")
        logger.info(f"   Improvements applied: {self.improvements_applied}")
        logger.info("="*80 + "\n")
    
    def _apply_improvement(self, key: str, topic: str, information: Dict):
        """Apply learned improvement permanently to memory"""
        logger.info(f"🚀 APPLYING IMPROVEMENT: {key}")
        
        if "optimizations" not in self.memory:
            self.memory["optimizations"] = {}
        
        self.memory["optimizations"][key] = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "information": information,
            "applied": True,
            "status": "permanent"
        }
        
        # Log improvement
        self.learning_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "improvement_applied",
            "key": key,
            "topic": topic,
            "status": "permanent"
        })
        
        self.improvements_applied += 1
        logger.info(f"💾 Improvement saved to permanent memory")
    
    def self_improve(self):
        """Analyze patterns and suggest self-improvements"""
        logger.info("\n🔄 ANALYZING PATTERNS FOR SELF-IMPROVEMENT...")
        
        if not self.learning_log:
            logger.info("No learning data yet for improvement analysis")
            return
        
        # Analyze topics with highest learning frequency
        topic_counts = {}
        for entry in self.learning_log[-100:]:  # Last 100 entries
            topic = entry.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        if topic_counts:
            top_topic = max(topic_counts, key=topic_counts.get)
            logger.info(f"📊 Most learned topic: {top_topic} ({topic_counts[top_topic]} times)")
            
            if "patterns" not in self.memory:
                self.memory["patterns"] = {}
            
            self.memory["patterns"][top_topic] = {
                "frequency": topic_counts[top_topic],
                "last_updated": datetime.now().isoformat()
            }
        
        self._save_backend_memory()
    
    def update_system_knowledge(self):
        """Update system knowledge base based on learned information"""
        logger.info("\n🧬 UPDATING SYSTEM KNOWLEDGE BASE...")
        
        knowledge_updates = {
            "timestamp": datetime.now().isoformat(),
            "total_facts_learned": len(self.memory.get("learned_facts", {})),
            "total_optimizations": len(self.memory.get("optimizations", {})),
            "learning_cycles": len(self.learning_log),
            "status": "evolving"
        }
        
        # Save to permanent knowledge
        knowledge_file = MEMORY_DIR / "system_knowledge.json"
        try:
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_updates, f, indent=2, ensure_ascii=False)
            logger.info("✅ System knowledge updated")
        except Exception as e:
            logger.error(f"Error updating knowledge: {e}")


class AutonomousBackend:
    """Main autonomous background process"""
    
    def __init__(self):
        self.engine = IntelligenceEngine()
        self.running = True
        self.iteration = 0
        
    def run_continuous_loop(self):
        """Run continuous learning loop"""
        logger.info("\n╔════════════════════════════════════════════════╗")
        logger.info("║  🤖 AUTONOMOUS BACKEND LEARNING ENGINE STARTED  ║")
        logger.info("║  Operating in separate terminal (independent)   ║")
        logger.info("║  Scan interval: %d seconds" % SCAN_INTERVAL)
        logger.info("║  Max files per scan: %d" % MAX_FILES_PER_SCAN)
        logger.info("╚════════════════════════════════════════════════╝\n")
        
        try:
            while self.running:
                self.iteration += 1
                logger.info(f"\n🔄 Learning Iteration #{self.iteration}")
                
                # Main learning cycle
                self.engine.scan_and_learn()
                
                # Self-improve analysis
                if self.iteration % 3 == 0:
                    self.engine.self_improve()
                
                # Update system knowledge
                if self.iteration % 5 == 0:
                    self.engine.update_system_knowledge()
                
                # Wait before next cycle
                logger.info(f"⏳ Waiting {SCAN_INTERVAL} seconds before next learning cycle...")
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Shutting down autonomous backend gracefully...")
            self.running = False
        except Exception as e:
            logger.error(f"\n❌ Fatal error in backend: {e}", exc_info=True)
            self.running = False
    
    def get_status(self) -> Dict:
        """Get backend status"""
        return {
            "running": self.running,
            "iteration": self.iteration,
            "files_scanned": self.engine.files_scanned,
            "improvements_applied": self.engine.improvements_applied,
            "memory_size": len(self.engine.memory.get("learned_facts", {})),
            "learning_log_entries": len(self.engine.learning_log)
        }


def main():
    """Entry point for backend learning engine"""
    logger.info("Initializing autonomous backend learning engine...")
    backend = AutonomousBackend()
    
    try:
        backend.run_continuous_loop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("\nBackend engine shutdown complete.")


if __name__ == "__main__":
    main()
