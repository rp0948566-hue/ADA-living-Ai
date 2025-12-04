import ctypes
import subprocess

def test_lock():
    """Test the lock function"""
    try:
        print("Testing ctypes method...")
        ctypes.windll.user32.LockWorkStation()
        print("✓ ctypes method worked")
    except Exception as e:
        print(f"❌ ctypes method failed: {e}")
        try:
            print("Testing subprocess method...")
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True, check=True)
            print("✓ subprocess method worked")
        except Exception as e2:
            print(f"❌ subprocess method failed: {e2}")

if __name__ == "__main__":
    test_lock()
