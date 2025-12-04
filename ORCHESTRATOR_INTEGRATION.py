# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  AGENT.PY ORCHESTRATOR INTEGRATION                           ║
║              How to add orchestrator to your existing agent.py                ║
╚══════════════════════════════════════════════════════════════════════════════╝

INTEGRATION INSTRUCTIONS:
═════════════════════════

Copy this code and add to agent.py:


STEP 1: Add import at top of agent.py (with other imports)
─────────────────────────────────────────────────────────

from autonomous_orchestrator import run_orchestrator_async


STEP 2: Add to entrypoint() function
─────────────────────────────────────

async def entrypoint(ctx: agents.JobContext):
    max_retries = 5
    retry_count = 0
    base_wait_time = 3
    
    # ← ADD THIS: Start orchestrator
    orchestrator_thread, orchestrator = run_orchestrator_async(daemon=True)
    
    while retry_count < max_retries:
        try:
            print(f"\\n🚀 Starting agent session...")
            
            session = AgentSession(...)
            
            await session.start(...)
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            # ← ADD THIS: Save on shutdown
            try:
                from agent_learning import AgentLearningTools
                AgentLearningTools.save_learning_memory()
            except:
                pass


THAT'S IT! The orchestrator will:
  ✓ Run all learning files in endless loop
  ✓ Keep running while agent.py runs
  ✓ Stop when agent.py stops
  ✓ Auto-restart on errors
  ✓ Log all activity to autonomous_orchestrator.log


═════════════════════════════════════════════════════════════════════════════

WHAT THE ORCHESTRATOR DOES:
──────────────────────────

1. Starts when agent.py starts
2. Initializes learning tools
3. Starts background learning thread
4. Monitors learning progress every 30 seconds
5. Saves memory automatically
6. Keeps running in endless loop
7. Logs all activity to file
8. Stops gracefully when agent.py stops


MONITORING:
───────────

Check logs while running:
  tail -f autonomous_orchestrator.log  (Unix/Linux/Mac)
  Get-Content autonomous_orchestrator.log -Wait  (PowerShell)

Or check real-time output in agent.py console.


ERROR HANDLING:
───────────────

If orchestrator encounters error:
  • Logs the error
  • Increments error counter
  • Continues running
  • Auto-recovers

Only stops when:
  • agent.py stops
  • KeyboardInterrupt (Ctrl+C)
  • System signal


═════════════════════════════════════════════════════════════════════════════
"""

# Quick demo/test code
if __name__ == "__main__":
    from autonomous_orchestrator import run_orchestrator_async
    
    print(__doc__)
    print("\n" + "="*80)
    print("To test the orchestrator:")
    print("="*80)
    print()
    print("python autonomous_orchestrator.py")
    print()
    print("Then press Ctrl+C to stop")
    print()
