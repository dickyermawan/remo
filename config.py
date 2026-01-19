# REMO - Remote Control Bot Configuration

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# TELEGRAM SETTINGS
# =============================================================================

# Bot token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("REMO_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "REMO_BOT_TOKEN not set! "
        "Please create a .env file or set environment variable. "
        "See .env.example for reference."
    )

# Your Telegram User ID (numeric) - ONLY this user can control the bot
# Get your ID from @userinfobot on Telegram
TELEGRAM_USER_ID = int(os.getenv("REMO_USER_ID", "0"))
if TELEGRAM_USER_ID == 0:
    raise ValueError(
        "REMO_USER_ID not set! "
        "Get your Telegram User ID from @userinfobot and add to .env file. "
        "See .env.example for reference."
    )


# =============================================================================
# WEBHOOK SETTINGS
# =============================================================================

# Generate a static webhook secret (saved to file, won't change on restart)
_SECRET_FILE = Path(__file__).parent / ".webhook_secret"

def _get_or_create_webhook_secret() -> str:
    """Get existing webhook secret or create new one."""
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip()
    else:
        new_secret = secrets.token_urlsafe(32)
        _SECRET_FILE.write_text(new_secret)
        return new_secret

WEBHOOK_SECRET = os.getenv(
    "REMO_WEBHOOK_SECRET", 
    _get_or_create_webhook_secret()
)

# Cloudflare Tunnel domain
WEBHOOK_DOMAIN = os.getenv("REMO_WEBHOOK_DOMAIN")
if not WEBHOOK_DOMAIN:
    raise ValueError(
        "REMO_WEBHOOK_DOMAIN not set! "
        "Set your Cloudflare Tunnel domain in .env file. "
        "See .env.example for reference."
    )

# Local server settings
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = int(os.getenv("REMO_WEBHOOK_PORT", "8443"))
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

# Full webhook URL for Telegram
WEBHOOK_URL = f"https://{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

# =============================================================================
# COMMAND CONFIRMATION SETTINGS
# =============================================================================
# Set to True to require confirmation before executing
# Set to False to execute immediately

CONFIRM_COMMANDS = {
    "shutdown": True,
    "restart": True,
    "sleep": True,
    "lock": False,
    "screenshot": False,
    "volume": False,
    "mute": False,
    "unmute": False,
    "brightness": False,
    "status": False,
}

# =============================================================================
# DEVICE SETTINGS (for future multi-device support)
# =============================================================================

DEVICE_ID = os.getenv("REMO_DEVICE_ID", "main-laptop")
DEVICE_NAME = os.getenv("REMO_DEVICE_NAME", "Main Laptop")

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_LEVEL = os.getenv("REMO_LOG_LEVEL", "INFO")
LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "remo.log"

# =============================================================================
# RATE LIMITING
# =============================================================================

# Max commands per minute from the same user
RATE_LIMIT_COMMANDS = 30
RATE_LIMIT_WINDOW = 60  # seconds

# =============================================================================
# DASHBOARD AUTHENTICATION
# =============================================================================

# Dashboard admin credentials
DASHBOARD_USERNAME = os.getenv("REMO_DASHBOARD_USERNAME")
DASHBOARD_PASSWORD = os.getenv("REMO_DASHBOARD_PASSWORD")

if not DASHBOARD_USERNAME or not DASHBOARD_PASSWORD:
    raise ValueError(
        "Dashboard credentials not set! "
        "Please set REMO_DASHBOARD_USERNAME and REMO_DASHBOARD_PASSWORD in .env file. "
        "See .env.example for reference."
    )

# Session secret for signing cookies
DASHBOARD_SECRET_KEY = os.getenv("REMO_DASHBOARD_SECRET_KEY", secrets.token_hex(32))

# Session timeout (seconds)
DASHBOARD_SESSION_TIMEOUT = int(os.getenv("REMO_DASHBOARD_SESSION_TIMEOUT", "86400"))  # 24 hours

# Login rate limiting
DASHBOARD_MAX_LOGIN_ATTEMPTS = 5
DASHBOARD_LOGIN_WINDOW = 900  # 15 minutes
