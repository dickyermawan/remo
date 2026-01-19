# REMO - Display Control Module
# Handles: Screenshot, Brightness

import io
import asyncio
from typing import Tuple, Optional
from pathlib import Path

from loguru import logger

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not available, screenshot disabled")

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False
    logger.warning("screen_brightness_control not available, brightness control disabled")


class DisplayControl:
    """Windows display control functions."""
    
    async def take_screenshot(self) -> Tuple[bool, str, Optional[bytes]]:
        """Take a screenshot and return as bytes."""
        if not PYAUTOGUI_AVAILABLE:
            return False, "❌ Screenshot not available (pyautogui not installed)", None
        
        try:
            # Take screenshot in executor to avoid blocking
            screenshot = await asyncio.get_event_loop().run_in_executor(
                None,
                pyautogui.screenshot
            )
            
            # Convert to bytes
            buffer = io.BytesIO()
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: screenshot.save(buffer, format='PNG', optimize=True)
            )
            buffer.seek(0)
            
            logger.info("Screenshot taken successfully")
            return True, "📸 Screenshot captured!", buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False, f"❌ Failed to take screenshot: {e}", None
    
    async def get_brightness(self) -> Tuple[bool, str, int]:
        """Get current screen brightness (0-100)."""
        if not SBC_AVAILABLE:
            return False, "❌ Brightness control not available", 0
        
        try:
            brightness = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sbc.get_brightness()[0]  # Get first monitor
            )
            
            return True, f"☀️ Current brightness: {brightness}%", brightness
            
        except Exception as e:
            logger.error(f"Failed to get brightness: {e}")
            return False, f"❌ Failed to get brightness: {e}", 0
    
    async def set_brightness(self, level: int) -> Tuple[bool, str]:
        """Set screen brightness (0-100)."""
        if not SBC_AVAILABLE:
            return False, "❌ Brightness control not available"
        
        try:
            # Clamp value between 0 and 100
            level = max(0, min(100, level))
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sbc.set_brightness(level)
            )
            
            # Choose emoji based on level
            if level < 25:
                emoji = "🌑"
            elif level < 50:
                emoji = "🌓"
            elif level < 75:
                emoji = "🌔"
            else:
                emoji = "☀️"
            
            logger.info(f"Brightness set to {level}%")
            return True, f"{emoji} Brightness set to {level}%"
            
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return False, f"❌ Failed to set brightness: {e}"


# Singleton instance
display = DisplayControl()
