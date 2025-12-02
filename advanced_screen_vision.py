"""
Advanced Screen Vision Module
Real-time screen analysis, OCR, and content recognition
Uses Tesseract OCR for text recognition
"""

import os
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from livekit.agents import function_tool
import pyautogui
import pytesseract
from pathlib import Path

# Try to import Pillow for image processing
try:
    from PIL import Image, ImageDraw, ImageFont
except:
    Image = None

# Screenshots directory
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


class ScreenVisionAnalyzer:
    """Advanced screen vision and OCR analysis"""
    
    @staticmethod
    def take_screenshot(save: bool = True) -> Dict:
        """Capture screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(SCREENSHOTS_DIR, f"screen_{timestamp}.png")
                screenshot.save(filepath)
                
                return {
                    "success": True,
                    "path": filepath,
                    "timestamp": timestamp,
                    "width": screenshot.width,
                    "height": screenshot.height
                }
            
            return {
                "success": True,
                "data": screenshot,
                "width": screenshot.width,
                "height": screenshot.height
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to capture screenshot"
            }
    
    @staticmethod
    def extract_text_from_screen() -> Dict:
        """Extract all text from current screen using OCR"""
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Resize for better OCR
            resized = cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(resized)
            
            # Extract text with position information
            data = pytesseract.image_to_data(resized, output_type='dict')
            
            return {
                "success": True,
                "text": text,
                "raw_data": data,
                "confidence": np.mean([int(conf) for conf in data['conf'] if int(conf) != -1]),
                "length": len(text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to extract text from screen"
            }
    
    @staticmethod
    def analyze_screen_colors() -> Dict:
        """Analyze dominant colors in screen"""
        try:
            screenshot = pyautogui.screenshot()
            img_array = np.array(screenshot)
            
            # Reshape to 2D array
            pixels = img_array.reshape(-1, 3)
            
            # Find unique colors and their frequencies
            colors, counts = np.unique(pixels.reshape(-1, pixels.shape[-1]), 
                                      axis=0, return_counts=True)
            
            # Get top 10 colors
            top_indices = np.argsort(counts)[-10:][::-1]
            top_colors = colors[top_indices]
            
            color_info = []
            for color in top_colors:
                color_info.append({
                    "rgb": tuple(color),
                    "hex": '#{:02x}{:02x}{:02x}'.format(int(color[0]), int(color[1]), int(color[2]))
                })
            
            return {
                "success": True,
                "top_colors": color_info,
                "screen_width": screenshot.width,
                "screen_height": screenshot.height
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def detect_ui_elements() -> Dict:
        """Detect UI elements (buttons, text boxes, etc.)"""
        try:
            screenshot = pyautogui.screenshot()
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and analyze contours
            elements = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum size filter
                    x, y, w, h = cv2.boundingRect(contour)
                    elements.append({
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": int(area)
                    })
            
            return {
                "success": True,
                "elements_detected": len(elements),
                "elements": sorted(elements, key=lambda e: e['area'], reverse=True)[:20]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_screen_info() -> Dict:
        """Get detailed screen information"""
        try:
            screenshot = pyautogui.screenshot()
            
            # Get screen resolution
            screen_width = screenshot.width
            screen_height = screenshot.height
            
            # Analyze image
            img_array = np.array(screenshot)
            
            # Calculate average color
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Calculate brightness
            brightness = np.mean(cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY))
            
            return {
                "success": True,
                "resolution": {
                    "width": screen_width,
                    "height": screen_height
                },
                "average_color": {
                    "r": int(avg_color[0]),
                    "g": int(avg_color[1]),
                    "b": int(avg_color[2])
                },
                "brightness": float(brightness),
                "pixel_count": screen_width * screen_height
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def search_text_on_screen(search_text: str, case_sensitive: bool = False) -> Dict:
        """Search for text on screen"""
        try:
            # Extract all text from screen
            result = ScreenVisionAnalyzer.extract_text_from_screen()
            
            if not result.get("success"):
                return result
            
            screen_text = result.get("text", "")
            
            # Perform search
            if case_sensitive:
                found = search_text in screen_text
                occurrences = screen_text.count(search_text)
            else:
                found = search_text.lower() in screen_text.lower()
                occurrences = screen_text.lower().count(search_text.lower())
            
            return {
                "success": True,
                "found": found,
                "occurrences": occurrences,
                "search_text": search_text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def compare_screenshots(path1: str, path2: str) -> Dict:
        """Compare two screenshots"""
        try:
            img1 = cv2.imread(path1)
            img2 = cv2.imread(path2)
            
            if img1 is None or img2 is None:
                return {"success": False, "error": "Could not read images"}
            
            # Calculate difference
            diff = cv2.absdiff(img1, img2)
            
            # Count non-zero pixels
            non_zero = np.count_nonzero(diff)
            total_pixels = diff.shape[0] * diff.shape[1] * diff.shape[2]
            
            similarity = 1 - (non_zero / total_pixels)
            
            return {
                "success": True,
                "similarity": float(similarity),
                "difference_pixels": int(non_zero),
                "total_pixels": int(total_pixels)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# LiveKit Function Tools
@function_tool
async def take_screenshot_tool(save: bool = True) -> dict:
    """
    Capture current screen
    
    Args:
        save: Save screenshot to file
    
    Returns:
        Screenshot information
    """
    return ScreenVisionAnalyzer.take_screenshot(save)


@function_tool
async def extract_screen_text_tool() -> dict:
    """
    Extract all text visible on screen using OCR
    
    Returns:
        Extracted text and OCR data
    """
    return ScreenVisionAnalyzer.extract_text_from_screen()


@function_tool
async def analyze_screen_tool() -> dict:
    """
    Comprehensive screen analysis including text, colors, and UI elements
    
    Returns:
        Complete screen analysis
    """
    text_result = ScreenVisionAnalyzer.extract_text_from_screen()
    colors_result = ScreenVisionAnalyzer.analyze_screen_colors()
    elements_result = ScreenVisionAnalyzer.detect_ui_elements()
    info_result = ScreenVisionAnalyzer.get_screen_info()
    
    return {
        "success": all([
            text_result.get("success"),
            colors_result.get("success"),
            elements_result.get("success"),
            info_result.get("success")
        ]),
        "text": text_result.get("text", ""),
        "colors": colors_result.get("top_colors", []),
        "ui_elements": elements_result.get("elements", []),
        "screen_info": info_result,
        "timestamp": datetime.now().isoformat()
    }


@function_tool
async def search_screen_text_tool(search_text: str) -> dict:
    """
    Search for specific text on current screen
    
    Args:
        search_text: Text to search for
    
    Returns:
        Search results
    """
    return ScreenVisionAnalyzer.search_text_on_screen(search_text)


@function_tool
async def get_screen_info_tool() -> dict:
    """Get detailed screen information"""
    return ScreenVisionAnalyzer.get_screen_info()


@function_tool
async def analyze_colors_tool() -> dict:
    """Analyze dominant colors on screen"""
    return ScreenVisionAnalyzer.analyze_screen_colors()


@function_tool
async def detect_ui_elements_tool() -> dict:
    """Detect UI elements on screen"""
    return ScreenVisionAnalyzer.detect_ui_elements()
