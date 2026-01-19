# REMO - System Status Module
# Handles: CPU, RAM, Battery, Uptime

import asyncio
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

from loguru import logger

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, system status disabled")


class SystemStatus:
    """System information and status functions."""
    
    async def get_cpu_percent(self) -> float:
        """Get CPU usage percentage."""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: psutil.cpu_percent(interval=1)
        )
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage info."""
        if not PSUTIL_AVAILABLE:
            return {"percent": 0, "used_gb": 0, "total_gb": 0}
        
        mem = await asyncio.get_event_loop().run_in_executor(
            None,
            psutil.virtual_memory
        )
        
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024 ** 3), 1),
            "total_gb": round(mem.total / (1024 ** 3), 1),
        }
    
    async def get_battery_info(self) -> Dict[str, Any]:
        """Get battery info. Returns None if no battery."""
        if not PSUTIL_AVAILABLE:
            return None
        
        battery = await asyncio.get_event_loop().run_in_executor(
            None,
            psutil.sensors_battery
        )
        
        if battery is None:
            return None
        
        # Calculate time remaining
        if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            time_left = "Unknown"
        elif battery.secsleft == psutil.POWER_TIME_UNLIMITED:
            time_left = "Charging"
        else:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            time_left = f"{hours}h {minutes}m"
        
        return {
            "percent": battery.percent,
            "plugged": battery.power_plugged,
            "time_left": time_left,
        }
    
    async def get_uptime(self) -> str:
        """Get system uptime as formatted string."""
        if not PSUTIL_AVAILABLE:
            return "Unknown"
        
        boot_time = await asyncio.get_event_loop().run_in_executor(
            None,
            psutil.boot_time
        )
        
        uptime_seconds = datetime.now().timestamp() - boot_time
        uptime = timedelta(seconds=int(uptime_seconds))
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        
        return " ".join(parts)
    
    async def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage for system drive."""
        if not PSUTIL_AVAILABLE:
            return {"percent": 0, "used_gb": 0, "total_gb": 0}
        
        disk = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: psutil.disk_usage('C:\\')
        )
        
        return {
            "percent": disk.percent,
            "used_gb": round(disk.used / (1024 ** 3), 1),
            "total_gb": round(disk.total / (1024 ** 3), 1),
        }
    
    async def get_full_status(self) -> Tuple[bool, str]:
        """Get formatted full system status."""
        try:
            # Gather all stats concurrently
            cpu, memory, battery, uptime, disk = await asyncio.gather(
                self.get_cpu_percent(),
                self.get_memory_info(),
                self.get_battery_info(),
                self.get_uptime(),
                self.get_disk_info(),
            )
            
            # Build status message
            lines = [
                "📊 **System Status**",
                "",
                f"🖥️ **CPU:** {cpu}%",
                f"💾 **RAM:** {memory['used_gb']}GB / {memory['total_gb']}GB ({memory['percent']}%)",
                f"💿 **Disk:** {disk['used_gb']}GB / {disk['total_gb']}GB ({disk['percent']}%)",
                f"⏱️ **Uptime:** {uptime}",
            ]
            
            # Add battery if available
            if battery:
                battery_emoji = "🔌" if battery['plugged'] else "🔋"
                battery_line = f"{battery_emoji} **Battery:** {battery['percent']}%"
                if not battery['plugged']:
                    battery_line += f" ({battery['time_left']} left)"
                else:
                    battery_line += " (Charging)"
                lines.append(battery_line)
            
            status_message = "\n".join(lines)
            logger.info("System status retrieved")
            return True, status_message
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return False, f"❌ Failed to get system status: {e}"


# Singleton instance
status = SystemStatus()
