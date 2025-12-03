"""
ENHANCED JARVIS GUI WITH SCREEN SHARING & OBJECT DETECTION
Advanced camera with object detection, screen sharing, and data persistence
"""

import sys
import os
import cv2
import numpy as np
import threading
import queue
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject, QRect, QSize
from PySide6.QtGui import QPixmap, QImage, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QCheckBox, QComboBox,
    QSpinBox, QMessageBox, QFileDialog, QSplitter
)

from PySide6.QtCore import Qt

# Try to import PIL for screen capture
try:
    from PIL import ImageGrab, Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not installed. Screen sharing requires: pip install Pillow")

# Try to import object detection
try:
    from object_detection_engine import (
        ObjectDetector, ContinuousObjectDetector, ObjectAnalyzer,
        init_object_detection, start_continuous_detection, stop_continuous_detection,
        save_detection_data, YOLO_AVAILABLE
    )
except ImportError as e:
    print(f"⚠️ Object detection not available: {e}")
    YOLO_AVAILABLE = False
    ObjectDetector = None


class ScreenCaptureWorker(QObject):
    """Captures screen in background thread"""
    screen_updated = Signal(QPixmap)
    
    def __init__(self):
        super().__init__()
        self.running = False
    
    def run(self):
        """Continuous screen capture loop"""
        self.running = True
        print("🖥️ Screen capture started")
        
        while self.running:
            try:
                if PIL_AVAILABLE:
                    # Capture full screen
                    screenshot = ImageGrab.grab()
                    
                    # Convert PIL image to QPixmap
                    screenshot.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                    
                    # Convert to QImage then QPixmap
                    rgb_image = screenshot.convert('RGB')
                    data = rgb_image.tobytes()
                    width, height = rgb_image.size
                    
                    q_image = QImage(data, width, height, width * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    
                    self.screen_updated.emit(pixmap)
                
                # Update every 500ms for smooth but not CPU-heavy capture
                QThread.msleep(500)
            
            except Exception as e:
                print(f"❌ Screen capture error: {e}")
                QThread.msleep(1000)
    
    def stop(self):
        """Stop screen capture"""
        self.running = False


class EnhancedCameraWidget(QFrame):
    """Enhanced camera widget with object detection"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius: 8px; background: rgba(10,14,20,220); }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("📹 Live Camera + Object Detection")
        title.setStyleSheet("color: #CFE7FF; font-weight: bold; font-size: 11px;")
        layout.addWidget(title)
        
        # Video display
        self.video_label = QLabel("Camera: Offline")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumHeight(240)
        self.video_label.setStyleSheet("background: rgba(5,12,20,200);")
        layout.addWidget(self.video_label, 1)
        
        # Detection info
        info_layout = QHBoxLayout()
        self.detect_label = QLabel("Objects: 0")
        self.detect_label.setStyleSheet("color: #A0C0E0; font-size: 10px;")
        self.confidence_label = QLabel("Confidence: --")
        self.confidence_label.setStyleSheet("color: #A0C0E0; font-size: 10px;")
        info_layout.addWidget(self.detect_label)
        info_layout.addStretch()
        info_layout.addWidget(self.confidence_label)
        layout.addLayout(info_layout)
        
        # Initialize camera
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Object detection
        self.detector = None
        self.continuous_detector = None
        self.detection_enabled = False
    
    def start_camera(self):
        """Start camera feed"""
        try:
            if self.capture and self.capture.isOpened():
                return True
            
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.capture = None
                return False
            
            self.timer.start(33)  # ~30 FPS
            print("✅ Camera started")
            return True
        except Exception as e:
            print(f"❌ Camera start error: {e}")
            return False
    
    def enable_object_detection(self, enable=True):
        """Enable/disable object detection"""
        if not YOLO_AVAILABLE:
            QMessageBox.warning(None, "Object Detection", 
                              "YOLOv8 not installed. Install with:\npip install ultralytics torch")
            return
        
        if enable and not self.detection_enabled:
            try:
                if self.detector is None:
                    self.detector = ObjectDetector(model_size='n')
                self.detection_enabled = True
                print("🔍 Object detection enabled")
                self.detect_label.setText("Objects: Detecting...")
            except Exception as e:
                QMessageBox.warning(None, "Detection Error", f"Failed to enable detection: {e}")
        
        elif not enable:
            self.detection_enabled = False
            self.detect_label.setText("Objects: 0")
            print("❌ Object detection disabled")
    
    def update_frame(self):
        """Update camera frame with optional detection"""
        if not self.capture or not self.capture.isOpened():
            return
        
        ret, frame = self.capture.read()
        if not ret:
            return
        
        frame = cv2.resize(frame, (480, 360))
        display_frame = frame.copy()
        
        # Run object detection if enabled
        if self.detection_enabled and self.detector:
            try:
                results = self.detector.detect_objects(display_frame, return_annotated=True)
                
                if results.get("annotated_frame") is not None:
                    display_frame = results["annotated_frame"]
                    
                    # Update detection info
                    if results.get("objects"):
                        obj_count = len(results["objects"])
                        avg_conf = np.mean([o["confidence"] for o in results["objects"]])
                        self.detect_label.setText(f"Objects: {obj_count}")
                        self.confidence_label.setText(f"Confidence: {avg_conf:.1f}%")
                    else:
                        self.detect_label.setText("Objects: 0")
                        self.confidence_label.setText("Confidence: --")
                
            except Exception as e:
                print(f"⚠️ Detection frame error: {e}")
        
        # Convert to QPixmap
        h, w, ch = display_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(display_frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        
        self.video_label.setPixmap(pixmap.scaledToWidth(480, Qt.SmoothTransformation))
    
    def stop_camera(self):
        """Stop camera"""
        self.timer.stop()
        self.enable_object_detection(False)
        if self.capture:
            self.capture.release()
            self.capture = None
        self.video_label.setText("Camera: Offline")
        print("🛑 Camera stopped")
    
    def capture_snapshot(self):
        """Capture and save snapshot with detection data"""
        if not self.capture or not self.capture.isOpened():
            return None
        
        ret, frame = self.capture.read()
        if not ret:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.png"
        
        # Save original
        cv2.imwrite(filename, frame)
        
        # Save detection data if available
        if self.detection_enabled and self.detector:
            try:
                results = self.detector.detect_objects(frame)
                data_filename = f"detection_{timestamp}.json"
                
                import json
                with open(data_filename, 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"✅ Snapshot and detection data saved")
                return filename
            except:
                pass
        
        print(f"✅ Snapshot saved: {filename}")
        return filename


class ScreenShareWidget(QFrame):
    """Screen sharing / screen vision widget"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius: 8px; background: rgba(10,14,20,220); }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("🖥️ Screen Vision - Live Monitor")
        title.setStyleSheet("color: #CFE7FF; font-weight: bold; font-size: 11px;")
        layout.addWidget(title)
        
        # Screen display
        self.screen_label = QLabel("Screen: Offline")
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.screen_label.setMinimumHeight(240)
        self.screen_label.setStyleSheet("background: rgba(5,12,20,200);")
        layout.addWidget(self.screen_label, 1)
        
        # Status
        self.status_label = QLabel("Ready to start screen sharing")
        self.status_label.setStyleSheet("color: #A0C0E0; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # Screen capture worker
        self.screen_thread = QThread()
        self.screen_worker = ScreenCaptureWorker()
        self.screen_worker.moveToThread(self.screen_thread)
        self.screen_thread.started.connect(self.screen_worker.run)
        self.screen_worker.screen_updated.connect(self.update_screen)
        
        self.is_sharing = False
    
    def start_sharing(self):
        """Start screen sharing"""
        if not PIL_AVAILABLE:
            QMessageBox.warning(None, "Screen Sharing", 
                              "PIL not installed. Install with:\npip install Pillow")
            return
        
        if not self.is_sharing:
            self.screen_thread.start()
            self.is_sharing = True
            self.status_label.setText("🟢 Screen sharing active")
            print("🟢 Screen sharing started")
    
    def stop_sharing(self):
        """Stop screen sharing"""
        if self.is_sharing:
            self.screen_worker.stop()
            self.screen_thread.quit()
            self.screen_thread.wait()
            self.is_sharing = False
            self.screen_label.setText("Screen: Offline")
            self.status_label.setText("Screen sharing stopped")
            print("⛔ Screen sharing stopped")
    
    def update_screen(self, pixmap):
        """Update screen display"""
        self.screen_label.setPixmap(pixmap.scaledToWidth(640, Qt.SmoothTransformation))


class AdvancedJarvisGUI(QMainWindow):
    """Enhanced JARVIS GUI with object detection and screen sharing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS Advanced Vision System")
        self.resize(1400, 800)
        self.setStyleSheet("""
            QMainWindow { background: rgb(5,12,20); }
            QMainWindow::separator { width: 2px; background: rgba(60,200,255,50); }
        """)
        
        self.detector_active = False
        self.screen_sharing_active = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top Control Bar
        control_frame = QFrame()
        control_frame.setStyleSheet("background: rgba(10,20,35,180); border-radius: 6px;")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 8, 10, 8)
        
        # Camera controls
        self.btn_camera = QPushButton("📷 Start Camera")
        self.btn_camera.clicked.connect(self.toggle_camera)
        self.btn_camera.setFixedHeight(36)
        control_layout.addWidget(self.btn_camera)
        
        # Object detection toggle
        self.btn_detection = QPushButton("🔍 Enable Detection")
        self.btn_detection.clicked.connect(self.toggle_detection)
        self.btn_detection.setFixedHeight(36)
        control_layout.addWidget(self.btn_detection)
        
        # Screen sharing toggle
        self.btn_screen_share = QPushButton("🖥️ Start Screen Vision")
        self.btn_screen_share.clicked.connect(self.toggle_screen_share)
        self.btn_screen_share.setFixedHeight(36)
        control_layout.addWidget(self.btn_screen_share)
        
        # Snapshot button
        self.btn_snapshot = QPushButton("📸 Snapshot")
        self.btn_snapshot.clicked.connect(self.take_snapshot)
        self.btn_snapshot.setFixedHeight(36)
        control_layout.addWidget(self.btn_snapshot)
        
        # Save data button
        self.btn_save = QPushButton("💾 Save Data")
        self.btn_save.clicked.connect(self.save_detection_data)
        self.btn_save.setFixedHeight(36)
        control_layout.addWidget(self.btn_save)
        
        control_layout.addStretch()
        
        main_layout.addWidget(control_frame)
        
        # Main content - Splitter for camera and screen
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Camera with detection
        self.camera_widget = EnhancedCameraWidget()
        splitter.addWidget(self.camera_widget)
        
        # Right side - Screen sharing
        self.screen_widget = ScreenShareWidget()
        splitter.addWidget(self.screen_widget)
        
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter, 1)
        
        # Bottom console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(120)
        self.console.setStyleSheet("""
            QTextEdit {
                background: rgba(8,12,16,200);
                color: #A0D0FF;
                border: 1px solid rgba(60,200,255,50);
                border-radius: 4px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.console)
        
        # Initialize detection
        if YOLO_AVAILABLE:
            init_object_detection()
        
        self.log("🟢 JARVIS Advanced Vision System Ready")
    
    def toggle_camera(self):
        """Toggle camera"""
        if self.camera_widget.capture and self.camera_widget.capture.isOpened():
            self.camera_widget.stop_camera()
            self.btn_camera.setText("📷 Start Camera")
            self.log("Camera stopped")
        else:
            if self.camera_widget.start_camera():
                self.btn_camera.setText("📹 Stop Camera")
                self.log("Camera started")
            else:
                self.log("❌ Failed to start camera")
    
    def toggle_detection(self):
        """Toggle object detection"""
        if not YOLO_AVAILABLE:
            QMessageBox.warning(self, "Detection", "YOLOv8 not installed")
            return
        
        if self.detector_active:
            self.camera_widget.enable_object_detection(False)
            self.detector_active = False
            self.btn_detection.setText("🔍 Enable Detection")
            self.log("Object detection disabled")
        else:
            self.camera_widget.enable_object_detection(True)
            self.detector_active = True
            self.btn_detection.setText("🔍 Stop Detection")
            self.log("Object detection enabled - point camera at objects")
    
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not PIL_AVAILABLE:
            QMessageBox.warning(self, "Screen Sharing", "PIL not installed")
            return
        
        if self.screen_sharing_active:
            self.screen_widget.stop_sharing()
            self.screen_sharing_active = False
            self.btn_screen_share.setText("🖥️ Start Screen Vision")
            self.log("Screen sharing stopped")
        else:
            self.screen_widget.start_sharing()
            self.screen_sharing_active = True
            self.btn_screen_share.setText("🖥️ Stop Screen Vision")
            self.log("Screen sharing started")
    
    def take_snapshot(self):
        """Take snapshot"""
        if self.camera_widget.capture and self.camera_widget.capture.isOpened():
            filename = self.camera_widget.capture_snapshot()
            if filename:
                self.log(f"Snapshot saved: {filename}")
        else:
            self.log("❌ Camera not running")
    
    def save_detection_data(self):
        """Save detection data"""
        if self.camera_widget.detector:
            try:
                filepath = self.camera_widget.detector.save_detection_data()
                self.log(f"Data saved: {filepath}")
                QMessageBox.information(self, "Data Saved", f"Saved to {filepath}")
            except Exception as e:
                self.log(f"❌ Error saving data: {e}")
        else:
            self.log("No detection data to save")
    
    def log(self, message):
        """Add message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        self.camera_widget.stop_camera()
        self.screen_widget.stop_sharing()
        self.log("System shutdown")
        super().closeEvent(event)


def main():
    """Run the GUI"""
    app = QApplication(sys.argv)
    window = AdvancedJarvisGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
