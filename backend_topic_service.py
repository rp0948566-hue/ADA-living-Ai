"""
Backend Topic Memory Service
- Runs continuously in background
- Auto-generates and manages random topics
- Performs periodic upgrades and evolution
- Syncs with agent.py when needed
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from random_topic_memory import (
    generate_random_topic, save_topic_to_memory, get_memory_stats,
    auto_update_memory, MemoryEvolutionEngine
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════════════════════
# BACKEND SERVICE CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

class BackendTopicService:
    """Continuous backend service for topic memory management"""
    
    def __init__(
        self,
        topic_generation_interval: int = 300,  # Generate new topic every 5 minutes
        auto_update_interval: int = 1800,       # Auto-update every 30 minutes
        evolution_enabled: bool = True
    ):
        """
        Initialize backend service
        
        Args:
            topic_generation_interval: Seconds between topic generation
            auto_update_interval: Seconds between auto-updates
            evolution_enabled: Enable memory evolution engine
        """
        self.topic_generation_interval = topic_generation_interval
        self.auto_update_interval = auto_update_interval
        self.evolution_enabled = evolution_enabled
        self.is_running = False
        self.evolution_engine = None
        self.stats_cycle = 0
    
    async def start_service(self):
        """Start the backend service (runs continuously)"""
        self.is_running = True
        logger.info("🚀 Backend Topic Memory Service starting...")
        
        # Start evolution engine if enabled
        if self.evolution_enabled:
            self.evolution_engine = MemoryEvolutionEngine(
                auto_upgrade_interval=self.auto_update_interval
            )
            self.evolution_engine.start_background_evolution()
            logger.info("✓ Memory evolution engine active")
        
        try:
            await self._service_loop()
        except KeyboardInterrupt:
            logger.info("⛔ Service interrupted by user")
            self.stop_service()
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
            self.stop_service()
    
    async def _service_loop(self):
        """Main service loop - runs endless"""
        last_stats_report = time.time()
        stats_report_interval = 600  # Report stats every 10 minutes
        
        logger.info("📋 Service loop started - Beginning topic generation cycle")
        logger.info(f"   ├─ Topic generation every {self.topic_generation_interval}s")
        logger.info(f"   └─ Auto-update every {self.auto_update_interval}s\n")
        
        while self.is_running:
            try:
                # Generate random topic
                current_time = time.time()
                if current_time - last_stats_report > stats_report_interval:
                    # Report stats periodically
                    self._report_stats()
                    last_stats_report = current_time
                
                # Generate and save new topic
                await self._generate_topic_cycle()
                
                # Wait for next generation
                await asyncio.sleep(self.topic_generation_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in service loop: {e}")
                await asyncio.sleep(5)  # Short pause before retry
    
    async def _generate_topic_cycle(self):
        """Generate and save a new topic"""
        try:
            topic = generate_random_topic()
            save_topic_to_memory(
                topic,
                metadata={
                    "source": "backend_service",
                    "auto_generated": True,
                    "service_cycle": self.stats_cycle
                }
            )
            logger.info(f"✅ Generated: {topic}")
            self.stats_cycle += 1
            
        except Exception as e:
            logger.error(f"Failed to generate topic: {e}")
    
    def _report_stats(self):
        """Report memory statistics"""
        try:
            stats = get_memory_stats()
            logger.info("\n📊 MEMORY STATISTICS REPORT")
            logger.info(f"   ├─ Total topics stored: {stats['total_topics_stored']}")
            logger.info(f"   ├─ Total interactions: {stats['total_interactions']}")
            logger.info(f"   ├─ Service cycles: {self.stats_cycle}")
            logger.info(f"   └─ Last updated: {stats['last_updated']}\n")
            
        except Exception as e:
            logger.error(f"Could not report stats: {e}")
    
    def stop_service(self):
        """Stop the backend service gracefully"""
        logger.info("\n🛑 Stopping Backend Topic Memory Service...")
        self.is_running = False
        
        if self.evolution_engine:
            self.evolution_engine.stop_background_evolution()
        
        # Final stats report
        try:
            stats = get_memory_stats()
            logger.info("\n📊 FINAL STATISTICS")
            logger.info(f"   ├─ Total topics stored: {stats['total_topics_stored']}")
            logger.info(f"   ├─ Total interactions: {stats['total_interactions']}")
            logger.info(f"   └─ Service cycles completed: {self.stats_cycle}\n")
        except Exception as e:
            logger.error(f"Could not report final stats: {e}")
        
        logger.info("✅ Backend service stopped successfully")


# ═════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

async def run_backend_service(
    topic_interval: int = 300,
    update_interval: int = 1800,
    evolution_enabled: bool = True
):
    """
    Run the backend service with specified parameters
    
    Args:
        topic_interval: Seconds between topic generation
        update_interval: Seconds between auto-updates
        evolution_enabled: Enable memory evolution
    """
    service = BackendTopicService(
        topic_generation_interval=topic_interval,
        auto_update_interval=update_interval,
        evolution_enabled=evolution_enabled
    )
    
    await service.start_service()


def run_backend_service_sync(
    topic_interval: int = 300,
    update_interval: int = 1800,
    evolution_enabled: bool = True
):
    """Run backend service synchronously (blocking)"""
    asyncio.run(
        run_backend_service(
            topic_interval=topic_interval,
            update_interval=update_interval,
            evolution_enabled=evolution_enabled
        )
    )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧠 BACKEND TOPIC MEMORY SERVICE")
    print("="*70)
    print("\nConfiguration:")
    print("  • Topic generation interval: 5 minutes")
    print("  • Auto-update interval: 30 minutes")
    print("  • Evolution engine: ENABLED")
    print("\nPress Ctrl+C to stop the service\n")
    
    try:
        run_backend_service_sync(
            topic_interval=300,          # Generate topic every 5 minutes
            update_interval=1800,        # Auto-update every 30 minutes
            evolution_enabled=True       # Enable evolution engine
        )
    except KeyboardInterrupt:
        print("\n✅ Service terminated")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
