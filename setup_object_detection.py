"""
SETUP SCRIPT FOR OBJECT DETECTION & ADVANCED VISION
Installs all required packages and validates setup
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_package(package_name, import_name=None):
    """Check if package is installed"""
    if import_name is None:
        import_name = package_name.lower().replace('-', '_')
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def main():
    print("\n" + "="*60)
    print("🎯 ADVANCED OBJECT DETECTION SETUP")
    print("="*60)
    
    # Packages to install
    packages = {
        'ultralytics': 'YOLOv8 Object Detection',
        'torch': 'PyTorch (AI Framework)',
        'torchvision': 'Computer Vision Utils',
        'Pillow': 'Image Processing',
        'opencv-python': 'OpenCV (optional, usually installed)',
        'PySide6': 'GUI Framework (optional)',
    }
    
    # Step 1: Check current installations
    print("\n📋 CHECKING CURRENT INSTALLATIONS...")
    print("-" * 60)
    
    missing = []
    for pkg, desc in packages.items():
        if not check_package(pkg):
            missing.append((pkg, desc))
    
    # Step 2: Install missing packages
    if missing:
        print("\n" + "="*60)
        print("📥 INSTALLING MISSING PACKAGES")
        print("="*60)
        
        for pkg, desc in missing:
            cmd = f"{sys.executable} -m pip install {pkg}"
            if not run_command(cmd, f"Installing {desc}"):
                print(f"⚠️ Warning: Failed to install {pkg}")
    else:
        print("\n✅ All packages already installed!")
    
    # Step 3: Verify installation
    print("\n" + "="*60)
    print("✔️ VERIFICATION")
    print("="*60)
    
    all_ok = True
    for pkg, desc in packages.items():
        if not check_package(pkg):
            all_ok = False
    
    # Step 4: Create directories
    print("\n" + "="*60)
    print("📁 CREATING DIRECTORIES")
    print("="*60)
    
    dirs = [
        'detection_data',
        'detection_data/cache'
    ]
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ {dir_name}/ ready")
    
    # Step 5: Summary
    print("\n" + "="*60)
    print("📊 SETUP SUMMARY")
    print("="*60)
    
    if all_ok:
        print("""
✅ SETUP COMPLETE!

Next steps:
1. Run the system:
   python agent.py
   
2. Or run GUI directly:
   python jarvis_advanced_vision.py

3. Click buttons in order:
   - 📷 Start Camera
   - 🔍 Enable Detection
   - 🖥️ Start Screen Vision
   
4. Test: Ask "What's in my hand?"

5. View data: Check detection_data/ folder

For detailed guide, see: OBJECT_DETECTION_GUIDE.md
        """)
    else:
        print("""
⚠️ SETUP INCOMPLETE

Some packages failed to install.
Please try:
1. pip install -r REQUIREMENTS_OBJECT_DETECTION.txt
2. Or manually install missing packages
3. Check your internet connection

For help: OBJECT_DETECTION_GUIDE.md
        """)
    
    # Step 6: File check
    print("\n" + "="*60)
    print("📄 FILE CHECK")
    print("="*60)
    
    required_files = [
        'object_detection_engine.py',
        'jarvis_advanced_vision.py',
        'object_detection_integration.py',
        'agent.py',
    ]
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - NOT FOUND")
    
    print("\n" + "="*60)
    print("🎉 Setup script completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
