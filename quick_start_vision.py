"""
QUICK START - OBJECT DETECTION & ADVANCED VISION
Run this to start everything at once
"""

import subprocess
import sys
import os
import time

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🎯 JARVIS ADVANCED VISION SYSTEM - QUICK START             ║
║     Object Detection + Screen Sharing + Hand Recognition    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if setup has been run
    if not os.path.exists('detection_data'):
        print("⚠️ First time setup detected...")
        print("Running setup_object_detection.py\n")
        subprocess.run([sys.executable, 'setup_object_detection.py'])
        print("\n✅ Setup complete! Starting system...\n")
        time.sleep(2)
    
    # Show options
    print("""
Choose how to start:

1️⃣  Start Advanced Vision GUI only
   - Camera feed with object detection
   - Screen sharing/vision
   - Real-time data logging
   
2️⃣  Start Full AI Agent with GUI
   - Live AI agent on camera
   - Object detection tools
   - Voice interaction
   - Advanced Vision GUI
   
3️⃣  Run Setup & Diagnostics
   - Install/verify packages
   - Check all files
   - Create directories
   
4️⃣  View Detection Data
   - Open latest detection file
   - Show session summaries
   - Export options

5️⃣  Exit

    """)
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == '1':
        print("\n🖥️ Starting Advanced Vision GUI...\n")
        subprocess.Popen([sys.executable, 'jarvis_advanced_vision.py'])
        print("✅ GUI started in background")
    
    elif choice == '2':
        print("\n🚀 Starting Full JARVIS AI Agent with Advanced Vision...\n")
        subprocess.Popen([sys.executable, 'agent.py'])
        print("✅ Agent started in background")
    
    elif choice == '3':
        print("\n🔧 Running setup...\n")
        subprocess.run([sys.executable, 'setup_object_detection.py'])
    
    elif choice == '4':
        print("\n📊 Viewing detection data...\n")
        
        data_dir = 'detection_data'
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            if files:
                print(f"Found {len(files)} detection files:\n")
                for i, f in enumerate(files[-5:], 1):  # Last 5 files
                    print(f"  {i}. {f}")
                
                # Try to open latest
                latest = max([os.path.join(data_dir, f) for f in files], 
                           key=os.path.getmtime)
                print(f"\n📂 Latest: {latest}")
                
                try:
                    with open(latest, 'r') as f:
                        import json
                        data = json.load(f)
                        print(f"\n📈 Session Summary:")
                        print(f"   - Objects detected: {data.get('total_frames_analyzed', 'N/A')}")
                        print(f"   - Unique types: {len(data.get('object_confidence_stats', {}))}")
                        if data.get('hand_objects'):
                            print(f"   - Hand objects: {list(data['hand_objects'].keys())}")
                except:
                    print("Could not parse file")
            else:
                print("No detection data yet. Start detection to create data files.")
        else:
            print("No detection_data folder. Run setup first.")
    
    elif choice == '5':
        print("\n👋 Goodbye!\n")
        return
    
    else:
        print("\n❌ Invalid choice\n")
        return
    
    # Keep running
    try:
        print("\n⏳ System running. Press Ctrl+C to exit.\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
