"""
OBJECT DETECTION INTEGRATION FOR JARVIS AGENT
Provides AI tools for object detection and analysis
Integrates with agent.py for natural language responses
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from livekit import agents
    from livekit.agents import llm, function_tool
except ImportError:
    print("⚠️ LiveKit not available for this module")
    llm = None
    agents = None
    function_tool = None

from object_detection_engine import (
    ObjectDetector, ObjectAnalyzer, ContinuousObjectDetector,
    init_object_detection, start_continuous_detection, stop_continuous_detection,
    save_detection_data, YOLO_AVAILABLE
)


class ObjectDetectionTools:
    """AI tools for object detection and analysis"""
    
    def __init__(self):
        self.detector = None
        self.analyzer = ObjectAnalyzer()
        self.continuous_detector = None
        self.hand_detection_active = False
        self.detection_data_dir = Path("detection_data")
        self.detection_data_dir.mkdir(exist_ok=True)
        
        # Initialize if available
        if YOLO_AVAILABLE:
            init_object_detection()
            self.detector = ObjectDetector(model_size='n')
            print("✅ Object detection tools initialized")
    
    @staticmethod
    def analyze_hand_content(hand_detections: dict) -> dict:
        """
        Analyze what objects are in user's hand
        Returns: {"status": "success/empty", "objects": [...], "ai_response": "..."}
        """
        analyzer = ObjectAnalyzer()
        
        if not hand_detections or not hand_detections.get("objects"):
            return {
                "status": "empty",
                "objects": [],
                "ai_response": "I don't detect any objects in your hand."
            }
        
        # Analyze the detections
        analysis = analyzer.analyze_hand_content(hand_detections)
        ai_response = analyzer.generate_ai_response(analysis)
        
        return {
            "status": "success",
            "objects": analysis["objects"],
            "confidence_scores": analysis["confidence_scores"],
            "ai_response": ai_response,
            "confirmed": all(a["confirmed"] for a in analysis["analysis"])
        }
    
    def get_hand_analysis_prompt(self) -> str:
        """
        Generate prompt for AI to describe hand contents
        Used by agent for natural responses
        """
        return """When the user asks \"what's in my hand?\" or similar:
1. Wait for camera input showing the hand
2. Analyze detected objects using confidence scores
3. For objects with >85% confidence: say \"I can clearly see...\"
4. For objects with 70-85% confidence: say \"I can see...\"
5. For objects with <70% confidence: say \"That might be a...\"
6. Always give friendly, natural responses
7. If uncertain, ask the user to hold it closer/steadier"""
    
    def start_hand_detection(self, camera_source=0):
        """Start continuous hand detection"""
        try:
            start_continuous_detection(camera_source)
            self.continuous_detector = ContinuousObjectDetector(camera_source)
            self.hand_detection_active = True
            print("🖐️ Hand detection started")
            return True
        except Exception as e:
            print(f"❌ Hand detection error: {e}")
            return False
    
    def stop_hand_detection(self):
        """Stop hand detection"""
        try:
            stop_continuous_detection()
            self.hand_detection_active = False
            print("🛑 Hand detection stopped")
            return True
        except Exception as e:
            print(f"❌ Error stopping detection: {e}")
            return False
    
    def get_latest_hand_detection(self):
        """Get latest hand detection result"""
        if not self.continuous_detector:
            return None
        
        return self.continuous_detector.get_latest_detections()
    
    def save_all_detection_data(self, filename=None):
        """Save detection session data"""
        try:
            filepath = save_detection_data()
            print(f"✅ Detection data saved to {filepath}")
            return {"status": "success", "file": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_detection_summary(self):
        """Get summary of detections in this session"""
        if not self.detector:
            return {"status": "error", "message": "Detector not initialized"}
        
        summary = self.detector.get_summary()
        return {
            "status": "success",
            "total_detections": summary["total_detections"],
            "unique_objects": len(summary["object_types"]),
            "object_types": summary["object_types"],
            "hand_objects": summary["hand_objects"],
            "most_detected": summary["most_detected"]
        }


# Create global instance
detection_tools = ObjectDetectionTools()


# LiveKit Agent Tools (if available)
if agents and llm:
    @function_tool(description="Detect and identify objects in user's hand")
    async def detect_hand_objects() -> str:
        """
        Analyze what's currently in the user's hand
        Returns natural language description of detected objects
        """
        try:
            if not detection_tools.hand_detection_active:
                detection_tools.start_hand_detection()
                await asyncio.sleep(1)  # Wait for first detection
            
            # Get latest detections
            detections = detection_tools.get_latest_hand_detection()
            
            if not detections:
                return "I'm still analyzing your hand. Please hold it steady toward the camera."
            
            # Analyze and get AI response
            analysis = detection_tools.analyze_hand_content(detections)
            return analysis["ai_response"]
        
        except Exception as e:
            return f"I encountered an error analyzing your hand: {str(e)}"
    
    @function_tool(description="Start continuous object detection from camera")
    async def start_object_detection() -> str:
        """Start continuous background object detection"""
        try:
            if detection_tools.start_hand_detection():
                return "Object detection started. I can now see objects in your hand."
            else:
                return "Failed to start object detection."
        except Exception as e:
            return f"Error starting detection: {str(e)}"
    
    @function_tool(description="Stop object detection")
    async def stop_object_detection() -> str:
        """Stop object detection"""
        try:
            if detection_tools.stop_hand_detection():
                return "Object detection stopped."
            else:
                return "Detection was already stopped."
        except Exception as e:
            return f"Error stopping detection: {str(e)}"
    
    @function_tool(description="Get summary of detected objects in session")
    async def get_detection_summary() -> str:
        """Get a summary of all objects detected in this session"""
        try:
            summary = detection_tools.get_detection_summary()
            
            if summary["status"] == "error":
                return summary["message"]
            
            response = f"In this session, I've detected {summary['total_objects']} objects"
            if summary["object_types"]:
                response += f" including: {', '.join(summary['object_types'][:5])}"
            
            return response
        except Exception as e:
            return f"Error getting summary: {str(e)}"
    
    @function_tool(description="Save all detection data to file")
    async def save_detection_session() -> str:
        """Save all detection data from this session"""
        try:
            result = detection_tools.save_all_detection_data()
            
            if result["status"] == "success":
                return f"Detection data saved to {result['file']}"
            else:
                return f"Error saving data: {result['message']}"
        except Exception as e:
            return f"Error saving detection data: {str(e)}"


# Export tools for manual use
def get_detection_tools():
    """Get the object detection tools instance"""
    return detection_tools


def get_agent_tools():
    """Get LiveKit agent tools"""
    if agents and llm:
        return [
            detect_hand_objects,
            start_object_detection,
            stop_object_detection,
            get_detection_summary,
            save_detection_session
        ]
    else:
        print("⚠️ LiveKit not available, returning empty tool list")
        return []


if __name__ == "__main__":
    # Test the tools
    print("🧪 Testing object detection tools...")
    print(f"✅ Tools available: {len(get_agent_tools())}")
    
    tools = get_detection_tools()
    print(f"\n📊 Summary: {tools.get_detection_summary()}")