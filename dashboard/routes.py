# REMO - Dashboard Routes

import os
import re
from pathlib import Path
from datetime import datetime

from aiohttp import web
import aiohttp_jinja2
import jinja2
from loguru import logger

import config
from dashboard.auth import (
    login_required,
    validate_credentials,
    set_session_cookie,
    get_session,
    clear_session,
    login_rate_limiter,
    get_client_ip,
)
from system.status import status


# Templates directory
templates_dir = Path(__file__).parent / "templates"


# =============================================================================
# PUBLIC ROUTES
# =============================================================================

@aiohttp_jinja2.template("login.html")
async def login_page(request: web.Request) -> dict:
    """Show login page or redirect if already logged in."""
    session = get_session(request)
    
    if session:
        # Already logged in, redirect to dashboard
        return web.HTTPFound("/dashboard")
    
    return {"error": None}


async def login_handler(request: web.Request) -> web.Response:
    """Handle login form submission."""
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Rate limiting check
    if not login_rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Too many login attempts. Please try again in 15 minutes."}
        )
    
    # Get form data
    data = await request.post()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    # Validate credentials
    if validate_credentials(username, password):
        # Success!
        logger.info(f"Successful login from IP: {client_ip}")
        login_rate_limiter.reset(client_ip)
        
        # Create session
        response = web.HTTPFound("/dashboard")
        set_session_cookie(response, {"username": username})
        
        return response
    else:
        # Failed
        logger.warning(f"Failed login attempt from IP: {client_ip} (username: {username})")
        return aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Invalid username or password"}
        )


async def logout_handler(request: web.Request) -> web.Response:
    """Handle logout."""
    response = web.HTTPFound("/")
    clear_session(response)
    logger.info(f"User logged out from IP: {get_client_ip(request)}")
    return response


# =============================================================================
# PROTECTED ROUTES
# =============================================================================

@login_required
@aiohttp_jinja2.template("dashboard.html")
async def dashboard_page(request: web.Request) -> dict:
    """Show main dashboard."""
    session = request["session"]
    
    return {
        "username": session["username"],
        "user_id": config.TELEGRAM_USER_ID,
        "webhook": config.WEBHOOK_DOMAIN,
        "device": config.DEVICE_NAME,
    }


@login_required
async def api_stats(request: web.Request) -> web.Response:
    """API endpoint for system stats - returns clean JSON."""
    try:
        # Get individual stats directly instead of parsing markdown
        cpu = await status.get_cpu_percent()
        memory = await status.get_memory_info()
        disk = await status.get_disk_info()
        uptime_str = await status.get_uptime()
        battery = await status.get_battery_info()
        
        # Format clean values
        stats = {
            "cpu": f"{cpu:.1f}",
            "ram": f"{memory['used_gb']}GB / {memory['total_gb']}GB ({memory['percent']}%)",
            "disk": f"{disk['used_gb']}GB / {disk['total_gb']}GB ({disk['percent']}%)",
            "uptime": uptime_str,
        }
        
        # Add battery if available
        if battery:
            battery_icon = "🔌" if battery['plugged'] else "🔋"
            battery_status = f"{battery_icon} {battery['percent']}%"
            if not battery['plugged']:
                battery_status += f" ({battery['time_left']} left)"
            else:
                battery_status += " (Charging)"
            stats["battery"] = battery_status
        else:
            stats["battery"] = "N/A"
        
        return web.json_response(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return web.json_response({
            "cpu": "Error",
            "ram": "Error",
            "disk": "Error",
            "uptime": "Error",
            "battery": "Error",
        })


@login_required
async def api_logs(request: web.Request) -> web.Response:
    """API endpoint for logs."""
    try:
        log_file = config.LOG_FILE
        
        if not log_file.exists():
            return web.json_response({"logs": []})
        
        # Read last 20 lines
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            recent_lines = lines[-20:] if len(lines) > 20 else lines
        
        # Parse log lines
        logs = []
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse loguru format: "2026-01-19 08:30:33 | INFO     | module:func:line | message"
            # Note: Level field is padded with spaces, milliseconds may be present or absent
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)? \| (\w+)\s+\| (.+)', line)
            
            if match:
                time_str, level, rest = match.groups()
                
                # Extract message from "module:func:line | message"
                # Split by last | to get the actual message
                parts = rest.split(' | ', 1)
                message = parts[1] if len(parts) > 1 else rest
                
                logs.append({
                    "time": time_str,  # Already without milliseconds
                    "level": level.strip(),
                    "message": message[:200],  # Limit message length
                })
        
        # Reverse to show newest first
        logs.reverse()
        
        return web.json_response({"logs": logs})
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return web.json_response({"logs": []})


# =============================================================================
# ROUTE SETUP
# =============================================================================

def setup_routes(app: web.Application) -> None:
    """Setup dashboard routes on app."""
    # Setup Jinja2 with app
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(templates_dir))
    )
    
    # Public routes
    app.router.add_get("/", login_page)
    app.router.add_post("/login", login_handler)
    app.router.add_get("/logout", logout_handler)
    
    # Protected routes
    app.router.add_get("/dashboard", dashboard_page)
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/logs", api_logs)
