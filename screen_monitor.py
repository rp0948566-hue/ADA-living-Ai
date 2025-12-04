import cv2
import numpy as np
import pyautogui
import time
import threading
import os
from datetime import datetime

class ScreenMonitor:
    def __init__(self):
        self.monitoring = False
        self.screenshot_interval = 5  # seconds
        self.monitor_thread = None
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def start_monitoring(self):
        """Start automatic screen monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🖥️ Screen monitoring started - capturing entire screen every 5 seconds")

    def stop_monitoring(self):
        """Stop screen monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("🖥️ Screen monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop that captures screenshots"""
        while self.monitoring:
            try:
                # Capture entire screen
                screenshot = pyautogui.screenshot()

                # Convert to numpy array for processing
                screen_array = np.array(screenshot)

                # Convert RGB to BGR for OpenCV
                screen_bgr = cv2.cvtColor(screen_array, cv2.COLOR_RGB2BGR)

                # Save screenshot with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.screenshots_dir}/screen_{timestamp}.png"
                cv2.imwrite(filename, screen_bgr)

                # Save latest screenshot reference
                with open(f"{self.screenshots_dir}/latest_screenshot.txt", "w") as f:
                    f.write(filename)

                print(f"📸 Screen captured: {filename}")

            except Exception as e:
                print(f"⚠️ Screen capture error: {e}")

            time.sleep(self.screenshot_interval)

    def get_current_screen(self):
        """Get current screen as image array"""
        try:
            screenshot = pyautogui.screenshot()
            return np.array(screenshot)
        except Exception as e:
            print(f"❌ Failed to get current screen: {e}")
            return None

    def get_screen_text(self, image=None):
        """Extract text from screen using OCR (placeholder for future OCR integration)"""
        if image is None:
            image = self.get_current_screen()

        if image is not None:
            # Placeholder - would need pytesseract or similar OCR library
            return "Screen text extraction not implemented yet"
        return "No screen image available"

# Global monitor instance
screen_monitor = ScreenMonitor()

def start_screen_monitoring():
    """Start the screen monitoring system"""
    screen_monitor.start_monitoring()
    return "🖥️ Screen monitoring started - capturing entire screen automatically"

def stop_screen_monitoring():
    """Stop the screen monitoring system"""
    screen_monitor.stop_monitoring()
    return "🖥️ Screen monitoring stopped"

def get_current_screen_info():
    """Get information about current screen"""
    try:
        screen_size = pyautogui.size()
        mouse_pos = pyautogui.position()
        return f"Screen size: {screen_size.width}x{screen_size.height}, Mouse position: {mouse_pos}"
    except Exception as e:
        return f"❌ Failed to get screen info: {e}"

if __name__ == "__main__":
    # Auto-start monitoring when script runs
    print("Starting screen monitor...")
    start_screen_monitoring()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_screen_monitoring()
        print("Screen monitor stopped by user")
