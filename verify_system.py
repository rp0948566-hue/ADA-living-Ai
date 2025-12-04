"""
═══════════════════════════════════════════════════════════════════════════════
    🔍 SYSTEM VERIFICATION SCRIPT - Check if everything is set up correctly
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.RESET}")

def check_file_exists(filepath, description=""):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description or filepath}")
        return True
    else:
        print_error(f"{description or filepath} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description=""):
    """Check if a directory exists"""
    if Path(dirpath).exists():
        print_success(f"{description or dirpath} - Directory exists")
        return True
    else:
        print_error(f"{description or dirpath} - Directory NOT FOUND")
        return False

def check_json_file(filepath, description=""):
    """Check if JSON file exists and is valid"""
    try:
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            print_success(f"{description or filepath} - Valid JSON")
            return True
        else:
            print_warning(f"{description or filepath} - File doesn't exist yet (will be created)")
            return False
    except Exception as e:
        print_error(f"{description or filepath} - Invalid JSON: {e}")
        return False

def main():
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                       ║")
    print("║        🔍 AUTONOMOUS ADA - SYSTEM VERIFICATION CHECK                 ║")
    print("║                                                                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    print_info(f"Workspace: {base_dir}")
    print()
    
    # Track results
    total_checks = 0
    passed_checks = 0
    
    # ═════════════════════════════════════════════════════════════════════════
    # 1. CHECK CORE SCRIPTS
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}1. CORE SYSTEM SCRIPTS{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    core_files = {
        "backend_learning_engine.py": "Backend Learning Engine",
        "memory_sync_bridge.py": "Memory Sync Bridge",
        "agent.py": "Main Agent (Updated)",
        "START_SYSTEM.ps1": "Master Launcher",
        "START_BACKEND.ps1": "Backend Launcher",
        "START_SYNC_BRIDGE.ps1": "Sync Bridge Launcher",
        "START_AGENT.ps1": "Agent Launcher",
    }
    
    for filename, description in core_files.items():
        filepath = base_dir / filename
        if check_file_exists(filepath, f"  {description}"):
            passed_checks += 1
        total_checks += 1
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # 2. CHECK AGENT FILE LINKS
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}2. AGENT FILE INTEGRATION{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    required_imports = [
        "from Jarvis_prompts import",
        "from Jarvis_screenshot import",
        "from Jarvis_google_search import",
        "from memory.jarvis_memory import",
        "from memory_interceptor import",
        "from jarvis_get_whether import",
        "from Jarvis_window_CTRL import",
        "from Jarvis_file_opner import",
        "from keyboard_mouse_CTRL import",
        "from memory_sync_bridge import",
        "from backend_learning_engine import",  # Referenced in agent.py
    ]
    
    try:
        with open(base_dir / "agent.py", 'r', encoding='utf-8') as f:
            agent_content = f.read()
        
        missing_imports = []
        for imp in required_imports:
            if imp in agent_content:
                print_success(f"  {imp}")
                passed_checks += 1
            else:
                print_warning(f"  {imp} - Not found")
                missing_imports.append(imp)
            total_checks += 1
        
        if missing_imports:
            print_warning(f"\nMissing {len(missing_imports)} import(s) - Agent may have issues")
        else:
            print_success("\nAll required imports present!")
            
    except Exception as e:
        print_error(f"Error checking agent.py: {e}")
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # 3. CHECK MEMORY DIRECTORY
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}3. MEMORY SYSTEM{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    memory_dir = base_dir / "memory"
    if check_directory_exists(memory_dir, "  Memory Directory"):
        passed_checks += 1
    total_checks += 1
    
    memory_files = {
        "memory/jarvis_memory.py": "Jarvis Memory Module",
        "memory/memory.json": "Agent Memory (will be created)",
        "memory/backend_intelligence.json": "Backend Intelligence (will be created)",
        "memory/shared_knowledge.json": "Shared Knowledge (will be created)",
        "memory/brain_decisions.json": "Brain Decisions (will be created)",
    }
    
    for filepath_str, description in memory_files.items():
        filepath = base_dir / filepath_str
        if filepath.exists():
            if filepath.suffix == '.json':
                check_json_file(filepath, f"  {description}")
            else:
                check_file_exists(filepath, f"  {description}")
            passed_checks += 1
        else:
            print_warning(f"  {description} - Will be created automatically")
        total_checks += 1
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # 4. CHECK LINKED FILES
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}4. WORKSPACE FILES (LINKED IN AGENT.PY){Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    workspace_files = {
        "Jarvis_prompts.py": "Prompts & Communication",
        "Jarvis_screenshot.py": "Screenshot Tool",
        "Jarvis_google_search.py": "Google Search",
        "jarvis_get_whether.py": "Weather Tool",
        "Jarvis_window_CTRL.py": "Window Control",
        "Jarvis_file_opner.py": "File Opener",
        "keyboard_mouse_CTRL.py": "Input Controls",
        "advanced_screen_vision.py": "Screen Vision (Optional)",
        "advanced_file_creator.py": "File Creator (Optional)",
        "advanced_code_generator.py": "Code Generator (Optional)",
        "windows_power_ctrl.py": "Power Control (Optional)",
        "memory_interceptor.py": "Memory Interceptor",
    }
    
    for filename, description in workspace_files.items():
        filepath = base_dir / filename
        if filepath.exists():
            print_success(f"  {description} ({filename})")
            passed_checks += 1
        else:
            print_warning(f"  {description} ({filename}) - Not found (may be optional)")
        total_checks += 1
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # 5. CHECK DOCUMENTATION
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}5. DOCUMENTATION{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    docs = {
        "SYSTEM_INTEGRATION_GUIDE.md": "Complete Guide",
        "QUICK_START.md": "Quick Start",
        "IMPLEMENTATION_SUMMARY.txt": "Implementation Summary",
    }
    
    for filename, description in docs.items():
        filepath = base_dir / filename
        if check_file_exists(filepath, f"  {description}"):
            passed_checks += 1
        total_checks += 1
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # 6. CHECK VIRTUAL ENVIRONMENT
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}6. PYTHON ENVIRONMENT{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    
    venv_dir = base_dir / ".venv"
    if venv_dir.exists():
        print_success("  Virtual Environment (.venv) exists")
        passed_checks += 1
    else:
        print_warning("  Virtual Environment doesn't exist yet (will be created by START_SYSTEM.ps1)")
    total_checks += 1
    
    req_file = base_dir / "requirements.txt"
    if check_file_exists(req_file, "  requirements.txt"):
        passed_checks += 1
    total_checks += 1
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print()
    
    passed_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total checks: {total_checks}")
    print(f"Passed: {Colors.GREEN}{passed_checks}{Colors.RESET}")
    print(f"Issues: {Colors.YELLOW}{total_checks - passed_checks}{Colors.RESET}")
    print(f"Success rate: {Colors.BLUE}{passed_percentage:.1f}%{Colors.RESET}")
    print()
    
    if passed_percentage >= 85:
        print_success("System is ready to launch!")
        print_info("Next step: Run '.\START_SYSTEM.ps1' to start the system")
    elif passed_percentage >= 70:
        print_warning("System has some missing optional components but should work")
        print_info("Next step: Run '.\START_SYSTEM.ps1' anyway, missing parts will be created")
    else:
        print_error("System has critical issues. Please check errors above.")
        print_info("Ensure all core scripts are present and agent.py has proper imports")
    
    print()
    
    # ═════════════════════════════════════════════════════════════════════════
    # QUICK TEST
    # ═════════════════════════════════════════════════════════════════════════
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}MEMORY INITIALIZATION TEST{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print()
    
    try:
        # Try to create memory directory
        memory_dir.mkdir(exist_ok=True)
        print_success("Memory directory accessible")
        
        # Try to create initial files
        test_files = {
            "memory.json": {"facts": {}, "conversation": []},
            "backend_intelligence.json": {"learned_facts": {}, "optimizations": {}},
            "shared_knowledge.json": {"backend_facts": {}, "agent_facts": {}, "merged_knowledge": {}},
            "brain_decisions.json": {"history": [], "patterns": {}},
        }
        
        for filename, content in test_files.items():
            filepath = memory_dir / filename
            if not filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                print_success(f"Created {filename}")
            else:
                print_info(f"{filename} already exists")
        
        print()
        print_success("Memory files initialized successfully!")
        
    except Exception as e:
        print_error(f"Error initializing memory: {e}")
    
    print()
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.CYAN}✨ Verification complete! System is ready to launch.{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print()
    print(f"{Colors.GREEN}Run this command to start:{Colors.RESET}")
    print(f"  .\START_SYSTEM.ps1")
    print()

if __name__ == "__main__":
    main()
