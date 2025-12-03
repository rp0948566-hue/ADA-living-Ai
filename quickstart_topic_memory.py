"""
Quick Start - Random Topic Memory System
Run this to see the system in action
"""

import sys
from random_topic_memory import (
    generate_and_save_random_topic,
    get_random_topic_from_memory,
    search_topics_memory,
    get_memory_status,
    trigger_memory_auto_update
)


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


async def main():
    """Run quick start demo"""
    
    print_header("RANDOM TOPIC MEMORY - QUICK START")
    
    # 1. Generate topics
    print("\n1️⃣  GENERATING RANDOM TOPICS")
    print("-" * 70)
    for i in range(3):
        result = await generate_and_save_random_topic()
        print(f"   ✅ {result}")
    
    # 2. Get random topic
    print("\n2️⃣  GET RANDOM TOPIC FROM MEMORY")
    print("-" * 70)
    result = await get_random_topic_from_memory()
    print(f"   {result}")
    
    # 3. Search topics
    print("\n3️⃣  SEARCH TOPICS")
    print("-" * 70)
    result = await search_topics_memory("history")
    print(f"   {result}")
    
    # 4. Get status
    print("\n4️⃣  MEMORY STATUS")
    print("-" * 70)
    result = await get_memory_status()
    print(result)
    
    # 5. Auto-update
    print("5️⃣  PERFORM AUTO-UPDATE")
    print("-" * 70)
    result = await trigger_memory_auto_update()
    print(result)
    
    print_header("✅ QUICK START COMPLETE")
    
    print("""
NEXT STEPS:
    
1️⃣  Run with Agent:
    python agent.py console
    
2️⃣  Run Backend Service:
    python backend_topic_service.py
    
3️⃣  View Memory Files:
    memory/topics/topics_index.json
    memory/topics/topics_stats.json
    memory/topics/evolution_history.json
    
4️⃣  Read Full Guide:
    RANDOM_TOPIC_MEMORY_GUIDE.md

""")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
