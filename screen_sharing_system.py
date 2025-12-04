"""
Screen Sharing & Window Capture System
Captures and streams your screen with start/stop voice control
Provides visual feedback and screen sharing capabilities
"""

import threading
import time
import logging
import os
from typing import Optional, Dict, Callable
from datetime import datetime
import numpy as np
import cv2
from PIL import ImageGrab
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ScreenSharer:
    """Handles screen capture and sharing with start/stop control"""
    
    def __init__(self, output_dir: str = "screen_captures"):
        """
        Initialize screen sharer
        
        Args:
            output_dir: Directory to save screen captures
        """
        self.output_dir = output_dir
        self.is_sharing = False
        self.capture_thread = None
        self.frame_count = 0
        self.start_time = None
        self.fps = 10  # Frames per second
        self.screen_width = None
        self.screen_height = None
        self.current_frame = None
        self.recording = False
        self.logger = logger
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"Created output directory: {output_dir}")
    
    def get_screen_size(self) -> tuple:
        """
        Get screen resolution
        
        Returns:
            tuple: (width, height) of the screen
        """
        try:
            screenshot = ImageGrab.grab()
            width, height = screenshot.size
            self.screen_width = width
            self.screen_height = height
            self.logger.info(f"Screen size: {width}x{height}")
            return width, height
        except Exception as e:
            self.logger.error(f"Failed to get screen size: {e}")
            return 1920, 1080  # Default fallback
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the screen
        
        Returns:
            np.ndarray: Screen capture as numpy array, or None if failed
        """
        try:
            screenshot = ImageGrab.grab()
            frame = np.array(screenshot)
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        except Exception as e:
            self.logger.error(f"Failed to capture frame: {e}")
            return None
    
    def add_info_overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Add information overlay to frame (timestamp, FPS, status)
        
        Args:
            frame: Frame to add overlay to
            
        Returns:
            np.ndarray: Frame with overlay
        """
        try:
            if frame is None:
                return None
            
            # Create a copy to avoid modifying the original
            frame_copy = frame.copy()
            
            # Calculate elapsed time
            elapsed = time.time() - self.start_time if self.start_time else 0
            
            # Add information text
            info_text = [
                f"Screen Sharing - ACTIVE",
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Duration: {int(elapsed)}s",
                f"Frames: {self.frame_count}",
                f"FPS: {self.fps}",
                "Status: [RECORDING] Click STOP SCREEN SHARE to end"
            ]
            
            # Add semi-transparent background for text
            overlay = frame_copy.copy()
            cv2.rectangle(overlay, (10, 10), (500, 200), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, frame_copy, 0.7, 0, frame_copy)
            
            # Add text
            y_offset = 40
            for text in info_text:
                cv2.putText(
                    frame_copy,
                    text,
                    (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),  # Green text
                    2
                )
                y_offset += 30
            
            # Add border to indicate recording
            cv2.rectangle(frame_copy, (5, 5), (frame_copy.shape[1]-5, frame_copy.shape[0]-5), (0, 0, 255), 3)
            
            return frame_copy
        except Exception as e:
            self.logger.error(f"Failed to add overlay: {e}")
            return frame
    
    def save_frame(self, frame: np.ndarray, filename: str) -> bool:
        """
        Save a frame to disk
        
        Args:
            frame: Frame to save
            filename: Filename to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, frame)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save frame: {e}")
            return False
    
    def _capture_loop(self):
        """Internal method that runs in the capture thread"""
        try:
            self.logger.info("Starting screen capture loop")
            self.start_time = time.time()
            interval = 1.0 / self.fps
            
            while self.is_sharing:
                loop_start = time.time()
                
                # Capture frame
                frame = self.capture_frame()
                if frame is not None:
                    # Add overlay information
                    frame_with_overlay = self.add_info_overlay(frame)
                    self.current_frame = frame_with_overlay
                    
                    # Save frame periodically (every 5 frames)
                    if self.recording and self.frame_count % 5 == 0:
                        filename = f"screen_share_{self.frame_count:06d}.png"
                        self.save_frame(frame_with_overlay, filename)
                    
                    self.frame_count += 1
                
                # Maintain FPS
                elapsed = time.time() - loop_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except Exception as e:
            self.logger.error(f"Error in capture loop: {e}")
        finally:
            self.logger.info("Capture loop ended")
    
    def start_screen_share(self, enable_recording: bool = True) -> Dict:
        """
        Start screen sharing
        
        Args:
            enable_recording: Whether to save frames to disk
            
        Returns:
            dict: Status of the operation
        """
        try:
            if self.is_sharing:
                return {
                    "success": False,
                    "message": "Screen sharing already active",
                    "status": "already_sharing"
                }
            
            self.logger.info("Starting screen share")
            self.is_sharing = True
            self.recording = enable_recording
            self.frame_count = 0
            
            # Get screen size
            self.get_screen_size()
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            return {
                "success": True,
                "message": "Screen sharing started",
                "status": "sharing",
                "timestamp": datetime.now().isoformat(),
                "screen_size": f"{self.screen_width}x{self.screen_height}",
                "fps": self.fps,
                "recording": enable_recording
            }
        except Exception as e:
            self.logger.error(f"Failed to start screen share: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def stop_screen_share(self) -> Dict:
        """
        Stop screen sharing
        
        Returns:
            dict: Status and summary of the operation
        """
        try:
            if not self.is_sharing:
                return {
                    "success": False,
                    "message": "Screen sharing not active",
                    "status": "not_sharing"
                }
            
            self.logger.info("Stopping screen share")
            self.is_sharing = False
            
            # Wait for thread to finish
            if self.capture_thread:
                self.capture_thread.join(timeout=2)
            
            # Calculate statistics
            elapsed = time.time() - self.start_time if self.start_time else 0
            actual_fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            return {
                "success": True,
                "message": "Screen sharing stopped",
                "status": "stopped",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": int(elapsed),
                "total_frames": self.frame_count,
                "average_fps": round(actual_fps, 2),
                "frames_saved": os.path.join(self.output_dir, "screen_share_*.png")
            }
        except Exception as e:
            self.logger.error(f"Failed to stop screen share: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get the current captured frame
        
        Returns:
            np.ndarray: Current frame or None if not capturing
        """
        return self.current_frame
    
    def get_status(self) -> Dict:
        """
        Get current sharing status
        
        Returns:
            dict: Current status information
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            "is_sharing": self.is_sharing,
            "recording": self.recording,
            "frame_count": self.frame_count,
            "elapsed_seconds": int(elapsed),
            "fps": self.fps,
            "screen_size": f"{self.screen_width}x{self.screen_height}" if self.screen_width else "Unknown",
            "output_directory": self.output_dir
        }
    
    def create_summary_image(self) -> Optional[str]:
        """
        Create a summary image of the screen sharing session
        
        Returns:
            str: Path to the summary image, or None if failed
        """
        try:
            if self.current_frame is None:
                return None
            
            filename = f"screen_share_summary_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, self.current_frame)
            
            self.logger.info(f"Summary image saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to create summary image: {e}")
            return None


# Global instance for voice control
_screen_sharer_instance = None


def start_screen_share_voice(enable_recording: bool = True) -> Dict:
    """
    Start screen sharing (voice command wrapper)
    
    Args:
        enable_recording: Whether to record frames
        
    Returns:
        dict: Status of the operation
    """
    global _screen_sharer_instance
    
    if _screen_sharer_instance is None:
        _screen_sharer_instance = ScreenSharer()
    
    result = _screen_sharer_instance.start_screen_share(enable_recording)
    
    if result["success"]:
        logger.info("✅ Screen sharing started via voice command")
    else:
        logger.warning(f"❌ Failed to start screen sharing: {result.get('message', result.get('error'))}")
    
    return result


def stop_screen_share_voice() -> Dict:
    """
    Stop screen sharing (voice command wrapper)
    
    Returns:
        dict: Status and summary of the operation
    """
    global _screen_sharer_instance
    
    if _screen_sharer_instance is None:
        return {
            "success": False,
            "message": "Screen sharing not initialized",
            "status": "not_initialized"
        }
    
    result = _screen_sharer_instance.stop_screen_share()
    
    if result["success"]:
        logger.info("✅ Screen sharing stopped via voice command")
        logger.info(f"   Duration: {result['duration_seconds']}s")
        logger.info(f"   Frames captured: {result['total_frames']}")
        logger.info(f"   Average FPS: {result['average_fps']}")
    else:
        logger.warning(f"❌ Failed to stop screen sharing: {result.get('message', result.get('error'))}")
    
    return result


def get_screen_share_status() -> Dict:
    """
    Get current screen share status
    
    Returns:
        dict: Current status
    """
    global _screen_sharer_instance
    
    if _screen_sharer_instance is None:
        return {
            "is_sharing": False,
            "status": "not_initialized"
        }
    
    return _screen_sharer_instance.get_status()


def get_screen_share_summary() -> Dict:
    """
    Get screen share summary
    
    Returns:
        dict: Summary information
    """
    global _screen_sharer_instance
    
    if _screen_sharer_instance is None:
        return {
            "available": False,
            "message": "Screen sharer not initialized"
        }
    
    status = _screen_sharer_instance.get_status()
    summary_path = _screen_sharer_instance.create_summary_image()
    
    return {
        "available": True,
        "status": status,
        "summary_image": summary_path,
        "frames_directory": _screen_sharer_instance.output_dir
    }


if __name__ == "__main__":
    print("Screen Sharing System Test")
    print("=" * 50)
    
    sharer = ScreenSharer()
    
    print("\nStarting screen share...")
    result = sharer.start_screen_share(enable_recording=True)
    print(f"Start result: {result}")
    
    print("\nCapturing frames for 10 seconds...")
    time.sleep(10)
    
    print("\nStopping screen share...")
    stop_result = sharer.stop_screen_share()
    print(f"Stop result: {stop_result}")
    
    print("\nScreen share system ready!")
