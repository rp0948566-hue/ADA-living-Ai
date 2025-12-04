"""
ADVANCED OBJECT DETECTION ENGINE
Detects objects in real-time from camera feed or images
Saves detection data, analyzes hand objects, and provides AI insights
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path
import threading
import queue
import time

try:
    import torch
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLOv8 not installed. Install with: pip install ultralytics torch")

class ObjectDetector:
    """Advanced object detection with caching and data persistence"""
    
    def __init__(self, model_size='n', save_data=True):
        """
        Initialize object detector
        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large), 'x' (xlarge)
            save_data: Save detection data to files
        """
        self.model_size = model_size
        self.save_data = save_data
        self.model = None
        self.detection_history = []
        self.hand_objects = {}
        self.confidence_threshold = 0.5
        self.data_dir = Path("detection_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Confidence cache for objects
        self.object_confidence_cache = {}
        
        if YOLO_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            print(f"📦 Loading YOLOv8-{self.model_size} model...")
            self.model = YOLO(f'yolov8{self.model_size}.pt')
            print("✅ YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            self.model = None
    
    def detect_objects(self, frame_or_path, return_annotated=True):
        """
        Detect objects in frame or image
        Args:
            frame_or_path: numpy array (frame) or path to image
            return_annotated: Return annotated image
        Returns:
            dict: Detection results with confidence levels
        """
        if self.model is None:
            return {"error": "Model not loaded", "objects": []}
        
        try:
            # Run detection
            results = self.model(frame_or_path, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            frame = frame_or_path if isinstance(frame_or_path, np.ndarray) else cv2.imread(frame_or_path)
            
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Get class name
                    class_name = result.names[cls_id]
                    
                    detection = {
                        "object": class_name,
                        "confidence": round(confidence * 100, 2),
                        "coords": {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)},
                        "width": int(x2 - x1),
                        "height": int(y2 - y1)
                    }
                    detections.append(detection)
                    
                    # Update confidence cache
                    if class_name not in self.object_confidence_cache:
                        self.object_confidence_cache[class_name] = []
                    self.object_confidence_cache[class_name].append(confidence)
                    
                    # Draw on frame if requested
                    if return_annotated and isinstance(frame_or_path, np.ndarray):
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                                   (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Store in history
            detection_entry = {
                "timestamp": datetime.now().isoformat(),
                "detections": detections,
                "frame_shape": frame.shape if isinstance(frame_or_path, np.ndarray) else None
            }
            self.detection_history.append(detection_entry)
            
            result_dict = {
                "success": True,
                "objects": detections,
                "total_objects": len(detections),
                "timestamp": detection_entry["timestamp"]
            }
            
            if return_annotated and isinstance(frame_or_path, np.ndarray):
                result_dict["annotated_frame"] = frame
            
            return result_dict
            
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return {"error": str(e), "objects": []}
    
    def detect_hand_objects(self, frame, hand_region=None):
        """
        Detect objects specifically in hand region
        Args:
            frame: Video frame
            hand_region: Optional (x1,y1,x2,y2) tuple for hand area
        Returns:
            dict: Objects detected in hand
        """
        if hand_region is None:
            # Default to lower portion of frame (where hands usually are)
            h, w = frame.shape[:2]
            hand_region = (0, h//2, w, h)
        
        x1, y1, x2, y2 = hand_region
        hand_frame = frame[y1:y2, x1:x2]
        
        detections = self.detect_objects(hand_frame, return_annotated=True)
        detections["region"] = hand_region
        
        if detections.get("objects"):
            # Adjust coordinates to full frame
            for obj in detections["objects"]:
                obj["coords"]["x1"] += x1
                obj["coords"]["y1"] += y1
                obj["coords"]["x2"] += x1
                obj["coords"]["y2"] += y1
            
            # Cache hand objects
            for obj in detections["objects"]:
                if obj["object"] not in self.hand_objects:
                    self.hand_objects[obj["object"]] = []
                self.hand_objects[obj["object"]].append({
                    "confidence": obj["confidence"],
                    "timestamp": datetime.now().isoformat()
                })
        
        return detections
    
    def identify_object_with_confidence(self, object_name):
        """
        Get average confidence for object type from cache
        Returns highest confidence seen for this object
        """
        if object_name not in self.object_confidence_cache:
            return None
        
        confidences = self.object_confidence_cache[object_name]
        return {
            "average": round(np.mean(confidences) * 100, 2),
            "max": round(np.max(confidences) * 100, 2),
            "detections": len(confidences)
        }
    
    def save_detection_data(self, filename=None):
        """Save all detection data to JSON file"""
        if not self.save_data:
            return None
        
        if filename is None:
            filename = f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.data_dir / filename
        
        data = {
            "detection_date": datetime.now().isoformat(),
            "total_frames_analyzed": len(self.detection_history),
            "hand_objects": self.hand_objects,
            "object_confidence_stats": {
                obj: self.identify_object_with_confidence(obj) 
                for obj in self.object_confidence_cache.keys()
            },
            "detection_history": self.detection_history[-100:]  # Last 100 detections
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Detection data saved to {filepath}")
        return str(filepath)
    
    def get_summary(self):
        """Get detection summary"""
        return {
            "total_detections": len(self.detection_history),
            "hand_objects": self.hand_objects,
            "object_types": list(self.object_confidence_cache.keys()),
            "most_detected": max(self.object_confidence_cache.items(), 
                                key=lambda x: len(x[1]))[0] if self.object_confidence_cache else None
        }


class ContinuousObjectDetector(threading.Thread):
    """Continuous object detection from camera feed"""
    
    def __init__(self, camera_source=0):
        super().__init__(daemon=True)
        self.camera_source = camera_source
        self.detector = ObjectDetector(model_size='n')  # Use nano for speed
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.detection_queue = queue.Queue()
        self.cap = None
    
    def run(self):
        """Continuous detection loop"""
        self.running = True
        self.cap = cv2.VideoCapture(self.camera_source)
        
        if not self.cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        print("🎥 Starting continuous object detection...")
        frame_count = 0
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.resize(frame, (640, 480))
                frame_count += 1
                
                # Detect every 3rd frame to save processing
                if frame_count % 3 == 0:
                    result = self.detector.detect_objects(frame, return_annotated=True)
                    
                    if result.get("objects"):
                        self.detection_queue.put(result)
                    
                    # Save annotated frame
                    if "annotated_frame" in result:
                        try:
                            self.frame_queue.put_nowait(result["annotated_frame"])
                        except queue.Full:
                            pass
                
                time.sleep(0.01)
        
        except Exception as e:
            print(f"❌ Detection thread error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop detection"""
        self.running = False
        if self.cap:
            self.cap.release()
        print("🛑 Object detection stopped")
    
    def get_latest_detections(self, timeout=0.1):
        """Get latest detections without blocking"""
        try:
            return self.detection_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_latest_frame(self, timeout=0.1):
        """Get latest annotated frame"""
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class ObjectAnalyzer:
    """Analyze detected objects for AI insights"""
    
    def __init__(self):
        self.analysis_history = []
    
    def analyze_hand_content(self, hand_detections):
        """Analyze what's in a hand"""
        if not hand_detections.get("objects"):
            return {"status": "empty", "message": "No objects detected in hand"}
        
        objects = hand_detections["objects"]
        analysis = {
            "object_count": len(objects),
            "objects": [o["object"] for o in objects],
            "confidence_scores": [o["confidence"] for o in objects],
            "analysis": []
        }
        
        # Generate analysis
        for obj in objects:
            analysis["analysis"].append({
                "item": obj["object"],
                "confidence": obj["confidence"],
                "identified": True,
                "confirmed": obj["confidence"] > 70  # High confidence = confirmed
            })
        
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        })
        
        return analysis
    
    def generate_ai_response(self, analysis):
        """Generate natural language response about detected objects"""
        if not analysis.get("objects"):
            return "I don't see anything in your hand."
        
        objects_str = ", ".join(analysis["objects"])
        confidence_avg = np.mean(analysis["confidence_scores"])
        
        if confidence_avg > 85:
            certainty = "I'm very confident"
        elif confidence_avg > 70:
            certainty = "I can see"
        else:
            certainty = "I think I can see"
        
        if len(analysis["objects"]) == 1:
            return f"{certainty} you're holding a {analysis['objects'][0]}."
        else:
            return f"{certainty} you have {objects_str} in your hand."


# Global detector instance
global_detector = None
continuous_detector_thread = None

def init_object_detection():
    """Initialize global object detector"""
    global global_detector, continuous_detector_thread
    
    if YOLO_AVAILABLE:
        global_detector = ObjectDetector(model_size='n', save_data=True)
        print("✅ Object detection engine initialized")
        return True
    else:
        print("❌ Object detection requires YOLOv8. Install with: pip install ultralytics torch")
        return False

def start_continuous_detection(camera_source=0):
    """Start continuous background detection"""
    global continuous_detector_thread
    
    if continuous_detector_thread is None:
        continuous_detector_thread = ContinuousObjectDetector(camera_source)
        continuous_detector_thread.start()
        print("🚀 Continuous detection started")

def stop_continuous_detection():
    """Stop continuous detection"""
    global continuous_detector_thread
    
    if continuous_detector_thread:
        continuous_detector_thread.stop()
        continuous_detector_thread = None
        print("⛔ Continuous detection stopped")

def save_detection_data():
    """Save all detection data"""
    global global_detector
    
    if global_detector:
        return global_detector.save_detection_data()
    return None


if __name__ == "__main__":
    # Test the detection engine
    if init_object_detection():
        print("\n🧪 Testing object detection...")
        start_continuous_detection()
        
        try:
            for _ in range(30):
                detections = continuous_detector_thread.get_latest_detections()
                if detections:
                    print(f"📊 Detected {detections['total_objects']} objects")
                    for obj in detections["objects"][:3]:
                        print(f"   • {obj['object']}: {obj['confidence']}% confidence")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n⛔ Test interrupted")
        finally:
            stop_continuous_detection()
            data_file = save_detection_data()
            print(f"✅ Data saved to: {data_file}")
