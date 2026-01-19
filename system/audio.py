# REMO - Audio Control Module
# Handles: Volume, Mute, Unmute

import asyncio
from typing import Tuple, Optional

from loguru import logger

try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    logger.warning("pycaw not available, audio control disabled")


class AudioControl:
    """Windows audio control using pycaw."""
    
    def __init__(self):
        self._volume_interface = None
    
    def _get_volume_interface(self):
        """Get the audio endpoint volume interface."""
        if not PYCAW_AVAILABLE:
            return None
            
        try:
            if self._volume_interface is None:
                devices = AudioUtilities.GetSpeakers()
                # pycaw 20251023+ uses AudioDevice with EndpointVolume property
                self._volume_interface = devices.EndpointVolume
            return self._volume_interface
        except Exception as e:
            logger.error(f"Failed to get audio interface: {e}")
            return None
    
    async def get_volume(self) -> Tuple[bool, str, int]:
        """Get current volume level (0-100)."""
        try:
            interface = self._get_volume_interface()
            if interface is None:
                return False, "❌ Audio control not available", 0
            
            # Get scalar volume (0.0 - 1.0)
            volume = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: interface.GetMasterVolumeLevelScalar()
            )
            volume_percent = int(volume * 100)
            
            return True, f"🔊 Current volume: {volume_percent}%", volume_percent
            
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return False, f"❌ Failed to get volume: {e}", 0
    
    async def set_volume(self, level: int) -> Tuple[bool, str]:
        """Set volume level (0-100)."""
        try:
            # Clamp value between 0 and 100
            level = max(0, min(100, level))
            
            interface = self._get_volume_interface()
            if interface is None:
                return False, "❌ Audio control not available"
            
            # Set scalar volume (0.0 - 1.0)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: interface.SetMasterVolumeLevelScalar(level / 100.0, None)
            )
            
            # Choose emoji based on level
            if level == 0:
                emoji = "🔇"
            elif level < 33:
                emoji = "🔈"
            elif level < 66:
                emoji = "🔉"
            else:
                emoji = "🔊"
            
            logger.info(f"Volume set to {level}%")
            return True, f"{emoji} Volume set to {level}%"
            
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False, f"❌ Failed to set volume: {e}"
    
    async def mute(self) -> Tuple[bool, str]:
        """Mute audio."""
        try:
            interface = self._get_volume_interface()
            if interface is None:
                return False, "❌ Audio control not available"
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: interface.SetMute(1, None)
            )
            
            logger.info("Audio muted")
            return True, "🔇 Audio muted"
            
        except Exception as e:
            logger.error(f"Failed to mute: {e}")
            return False, f"❌ Failed to mute: {e}"
    
    async def unmute(self) -> Tuple[bool, str]:
        """Unmute audio."""
        try:
            interface = self._get_volume_interface()
            if interface is None:
                return False, "❌ Audio control not available"
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: interface.SetMute(0, None)
            )
            
            logger.info("Audio unmuted")
            return True, "🔊 Audio unmuted"
            
        except Exception as e:
            logger.error(f"Failed to unmute: {e}")
            return False, f"❌ Failed to unmute: {e}"
    
    async def is_muted(self) -> Tuple[bool, bool]:
        """Check if audio is muted. Returns (success, is_muted)."""
        try:
            interface = self._get_volume_interface()
            if interface is None:
                return False, False
            
            muted = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: interface.GetMute()
            )
            
            return True, bool(muted)
            
        except Exception as e:
            logger.error(f"Failed to check mute status: {e}")
            return False, False


# Singleton instance
audio = AudioControl()
