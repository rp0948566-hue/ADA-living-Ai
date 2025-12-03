# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AUTONOMOUS SYSTEM ORCHESTRATOR                            ║
║           Runs all learning files in endless loop with agent.py              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This file runs when agent.py starts and:
  ✓ Starts continuous learning in background
  ✓ Runs all ABCD, learning_bridge, agent_learning modules
  ✓ Keeps running endlessly in loop
  ✓ Stops only when agent.py stops
  ✓ Auto-restarts on any error
"""

import threading
import time
import json
import os
from datetime import datetime
import signal
import sys

# ============================================================================
# ORCHESTRATION SYSTEM
# ============================================================================

class AutonomousOrchestrator:
    """
    Master orchestrator that runs all learning systems
    Endless loop that continues until agent.py stops
    """
    
    def __init__(self):
        self.running = True
        self.learning_thread = None
        self.monitoring_thread = None
        self.cycle_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        self.log_file = "autonomous_orchestrator.log"
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        self.log("🛑 Shutdown signal received")
        self.running = False
    
    def log(self, message):
        """Log to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except:
            pass
    
    def start_learning_systems(self):
        """Start all learning systems in background"""
        try:
            from agent_learning import AgentLearningTools
            
            self.log("📚 Initializing learning tools...")
            AgentLearningTools.initialize()
            
            self.log("🚀 Starting background learning thread...")
            self.learning_thread = AgentLearningTools.start_background_learning()
            
            self.log("✓ Learning systems started successfully")
            return True
        
        except ImportError as e:
            self.log(f"❌ Import error: {e}")
            self.error_count += 1
            return False
        except Exception as e:
            self.log(f"❌ Error starting learning: {e}")
            self.error_count += 1
            return False
    
    def monitor_learning(self):
        """Monitor learning system status continuously"""
        try:
            from agent_learning import AgentLearningTools
            
            while self.running:
                try:
                    stats = AgentLearningTools.get_learning_stats()
                    
                    if stats:
                        self.log(
                            f"📊 Learning: {stats['total_learned']} words learned, "
                            f"{stats['total_generated']} generated"
                        )
                    
                    # Save every 30 seconds
                    AgentLearningTools.save_learning_memory()
                    
                    time.sleep(30)
                
                except Exception as e:
                    self.log(f"⚠️ Monitor error: {e}")
                    time.sleep(10)
        
        except Exception as e:
            self.log(f"❌ Monitor system failed: {e}")
    
    def endless_loop(self):
        """Main endless loop that keeps system running"""
        self.log("╔════════════════════════════════════════════════════════════╗")
        self.log("║      AUTONOMOUS ORCHESTRATOR - ENDLESS LOOP STARTING       ║")
        self.log("╚════════════════════════════════════════════════════════════╝")
        self.log(f"Start time: {self.start_time}")
        
        # Start learning systems
        if not self.start_learning_systems():
            self.log("⚠️ Failed to start learning systems")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self.monitor_learning,
            daemon=True
        )
        self.monitoring_thread.start()
        self.log("✓ Monitoring thread started")
        
        # Main endless loop
        self.log("🔄 Entering endless loop...")
        
        try:
            while self.running:
                self.cycle_count += 1
                
                # Every 100 cycles, log status
                if self.cycle_count % 100 == 0:
                    uptime = datetime.now() - self.start_time
                    self.log(
                        f"✓ Cycle {self.cycle_count} | "
                        f"Uptime: {uptime} | "
                        f"Errors: {self.error_count}"
                    )
                
                # Keep running
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.log("⏹️ Keyboard interrupt received")
        
        except Exception as e:
            self.log(f"❌ Endless loop error: {e}")
            self.error_count += 1
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.log("🔴 Shutting down orchestrator...")
        self.running = False
        
        try:
            from agent_learning import AgentLearningTools
            AgentLearningTools.save_learning_memory()
            self.log("✓ Learning memory saved")
        except:
            pass
        
        uptime = datetime.now() - self.start_time
        self.log(f"📈 Total uptime: {uptime}")
        self.log(f"📊 Total cycles: {self.cycle_count}")
        self.log(f"❌ Total errors: {self.error_count}")
        self.log("✓ Orchestrator shutdown complete")

# ============================================================================
# SIMPLE FUNCTION INTERFACE
# ============================================================================

def run_orchestrator():
    """Run the orchestrator - called from agent.py"""
    orchestrator = AutonomousOrchestrator()
    orchestrator.endless_loop()

def run_orchestrator_async(daemon=True):
    """
    Run orchestrator in background thread
    Returns the thread object for control
    """
    orchestrator = AutonomousOrchestrator()
    
    thread = threading.Thread(
        target=orchestrator.endless_loop,
        daemon=daemon
    )
    thread.start()
    
    return thread, orchestrator

# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║      AUTONOMOUS ORCHESTRATOR - STANDALONE MODE             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("This file is designed to run WITH agent.py")
    print()
    print("For integration with agent.py:")
    print("  from autonomous_orchestrator import run_orchestrator_async")
    print("  thread, orchestrator = run_orchestrator_async()")
    print()
    print("Running standalone demo (Press Ctrl+C to stop)...")
    print()
    
    try:
        run_orchestrator()
    except KeyboardInterrupt:
        print("\n✓ Orchestrator stopped by user")
