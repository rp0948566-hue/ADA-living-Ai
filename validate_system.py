"""
SYSTEM VALIDATION & TESTING
Verify all object detection components are working
"""

import os
import sys
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_file(filename):
    """Check if file exists"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_import(module_name, package_name=None):
    """Check if package can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🧪 OBJECT DETECTION SYSTEM VALIDATION                      ║
║     Verify all components are properly installed            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    all_ok = True
    
    # Check Python files
    print_header("1️⃣ REQUIRED FILES")
    required_files = [
        'object_detection_engine.py',
        'jarvis_advanced_vision.py',
        'object_detection_integration.py',
        'agent.py',
        'setup_object_detection.py',
        'quick_start_vision.py',
    ]
    
    for f in required_files:
        if not check_file(f):
            all_ok = False
    
    # Check documentation
    print_header("2️⃣ DOCUMENTATION FILES")
    doc_files = [
        'OBJECT_DETECTION_GUIDE.md',
        'IMPLEMENTATION_OBJECT_DETECTION.md',
        'REQUIREMENTS_OBJECT_DETECTION.txt',
    ]
    
    for f in doc_files:
        check_file(f)
    
    # Check dependencies
    print_header("3️⃣ PYTHON PACKAGES (REQUIRED)")
    required_packages = [
        ('ultralytics', 'YOLOv8'),
        ('torch', 'PyTorch'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
    ]
    
    for module, name in required_packages:
        if not check_import(module, name):
            all_ok = False
    
    # Check optional packages
    print_header("4️⃣ PYTHON PACKAGES (OPTIONAL)")
    optional_packages = [
        ('PySide6', 'PySide6'),
        ('livekit', 'LiveKit'),
        ('numpy', 'NumPy'),
    ]
    
    for module, name in optional_packages:
        check_import(module, name)
    
    # Check directories
    print_header("5️⃣ DIRECTORIES")
    dirs = [
        'detection_data',
    ]
    
    for d in dirs:
        exists = os.path.exists(d)
        status = "✅" if exists else "⚠️ (will be created)"
        print(f"{status} {d}/")
        if not exists:
            try:
                os.makedirs(d, exist_ok=True)
                print("   → Created")
            except Exception as e:
                print(f"   → Error: {e}")
                all_ok = False
    
    # Check agent.py modifications
    print_header("6️⃣ AGENT.PY INTEGRATION")
    
    try:
        with open('agent.py', 'r') as f:
            content = f.read()
            
        checks = [
            ('object_detection_integration' in content, "Detection import"),
            ('detect_hand_objects' in content, "Hand detection tool"),
            ('DETECTION_TOOLS_AVAILABLE' in content, "Detection flag"),
            ('jarvis_advanced_vision' in content, "Advanced GUI launch"),
        ]
        
        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"{status} {desc}")
            if not check:
                all_ok = False
    
    except Exception as e:
        print(f"❌ Error reading agent.py: {e}")
        all_ok = False
    
    # Test imports
    print_header("7️⃣ MODULE IMPORTS")
    
    test_modules = [
        'object_detection_engine',
        'object_detection_integration',
    ]
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            all_ok = False
    
    # Check detection_data structure
    print_header("8️⃣ DATA STRUCTURE")
    
    if os.path.exists('detection_data'):
        files = os.listdir('detection_data')
        if files:
            print(f"✅ {len(files)} detection files found")
            
            # Try to parse latest JSON
            json_files = [f for f in files if f.endswith('.json')]
            if json_files:
                latest = json_files[-1]
                try:
                    with open(f'detection_data/{latest}', 'r') as f:
                        data = json.load(f)
                    print(f"✅ Valid JSON format: {latest}")
                    if 'detection_date' in data:
                        print(f"   Date: {data['detection_date']}")
                    if 'total_frames_analyzed' in data:
                        print(f"   Frames: {data['total_frames_analyzed']}")
                except Exception as e:
                    print(f"⚠️ Could not parse JSON: {e}")
        else:
            print("ℹ️ No detection data yet (will be created on first run)")
    else:
        print("ℹ️ detection_data folder not yet created")
    
    # Summary
    print_header("📊 VALIDATION SUMMARY")
    
    if all_ok:
        print("""
✅ ALL CHECKS PASSED!

System is ready to use. Next steps:

1. Run setup (first time only):
   python setup_object_detection.py

2. Start the system:
   python agent.py
   
   OR
   
   python jarvis_advanced_vision.py

3. Check the GUI buttons:
   - 📷 Start Camera
   - 🔍 Enable Detection
   - 🖥️ Start Screen Vision
   - 💾 Save Data

4. Test voice commands:
   "What's in my hand?"
   "Start object detection"
   "Save detection data"

For help: OBJECT_DETECTION_GUIDE.md
        """)
    else:
        print("""
⚠️ SOME CHECKS FAILED

Please fix the following:

1. Install missing packages:
   pip install -r REQUIREMENTS_OBJECT_DETECTION.txt

2. Ensure all files are present:
   object_detection_engine.py
   jarvis_advanced_vision.py
   object_detection_integration.py

3. Run setup:
   python setup_object_detection.py

4. Verify permissions:
   - Can write to detection_data/
   - Can access camera
   - Can access screen

For detailed help: OBJECT_DETECTION_GUIDE.md
        """)
    
    print(f"{'='*60}\n")
    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
