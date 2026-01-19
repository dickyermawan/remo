# REMO - Power Control Module
# Handles: Lock, Sleep, Shutdown, Restart

import ctypes
import subprocess
import asyncio
from typing import Tuple

from loguru import logger


class PowerControl:
    """Windows power control functions."""
    
    @staticmethod
    async def lock_screen() -> Tuple[bool, str]:
        """Lock the Windows screen."""
        try:
            # Use ctypes to call Windows API
            ctypes.windll.user32.LockWorkStation()
            logger.info("Screen locked successfully")
            return True, "🔒 Screen locked successfully!"
        except Exception as e:
            logger.error(f"Failed to lock screen: {e}")
            return False, f"❌ Failed to lock screen: {e}"
    
    @staticmethod
    async def sleep() -> Tuple[bool, str]:
        """Put the computer to sleep."""
        try:
            # Run in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ["powercfg", "-hibernate", "off"],
                    capture_output=True,
                    check=False
                )
            )
            
            # SetSuspendState: Hibernate=False, ForceCritical=False, DisableWakeEvent=False
            result = ctypes.windll.powrprof.SetSuspendState(0, 0, 0)
            
            if result:
                logger.info("Computer going to sleep")
                return True, "😴 Going to sleep..."
            else:
                raise Exception("SetSuspendState returned False")
                
        except Exception as e:
            logger.error(f"Failed to sleep: {e}")
            return False, f"❌ Failed to sleep: {e}"
    
    @staticmethod
    async def shutdown(delay: int = 5) -> Tuple[bool, str]:
        """Shutdown the computer with delay."""
        try:
            cmd = ["shutdown", "/s", "/t", str(delay)]
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, check=True)
            )
            logger.info(f"Shutdown scheduled in {delay} seconds")
            return True, f"🔴 Shutting down in {delay} seconds..."
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to shutdown: {e}")
            return False, f"❌ Failed to shutdown: {e}"
        except Exception as e:
            logger.error(f"Failed to shutdown: {e}")
            return False, f"❌ Failed to shutdown: {e}"
    
    @staticmethod
    async def restart(delay: int = 5) -> Tuple[bool, str]:
        """Restart the computer with delay."""
        try:
            cmd = ["shutdown", "/r", "/t", str(delay)]
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, check=True)
            )
            logger.info(f"Restart scheduled in {delay} seconds")
            return True, f"🔄 Restarting in {delay} seconds..."
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart: {e}")
            return False, f"❌ Failed to restart: {e}"
        except Exception as e:
            logger.error(f"Failed to restart: {e}")
            return False, f"❌ Failed to restart: {e}"
    
    @staticmethod
    async def cancel_shutdown() -> Tuple[bool, str]:
        """Cancel a scheduled shutdown/restart."""
        try:
            cmd = ["shutdown", "/a"]
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, check=True)
            )
            logger.info("Shutdown/restart cancelled")
            return True, "✅ Shutdown/restart cancelled!"
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to cancel: {e}")
            return False, f"❌ No scheduled shutdown to cancel"
        except Exception as e:
            logger.error(f"Failed to cancel: {e}")
            return False, f"❌ Failed to cancel: {e}"


# Singleton instance
power = PowerControl()
