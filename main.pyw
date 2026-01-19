# REMO - Main Entry Point (Webhook Mode)
# Telegram Bot for Remote Laptop Control

import asyncio
import signal
import sys

from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from loguru import logger

import config
from utils.logger import setup_logger

# Setup file logging
setup_logger()

from bot.handlers import (
    start_command,
    help_command,
    lock_command,
    sleep_command,
    shutdown_command,
    restart_command,
    status_command,
    screenshot_command,
    brightness_command,
    volume_command,
    mute_command,
    unmute_command,
    confirmation_callback,
    error_handler,
)


# =============================================================================
# WEBHOOK HANDLERS
# =============================================================================

async def webhook_handler(request: web.Request) -> web.Response:
    """Handle incoming webhook requests from Telegram."""
    application: Application = request.app["bot_app"]
    
    try:
        # Verify secret token
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if token != config.WEBHOOK_SECRET:
            logger.warning(f"Invalid webhook secret token from {request.remote}")
            return web.Response(status=403, text="Forbidden")
        
        # Parse the update
        data = await request.json()
        update = Update.de_json(data, application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return web.Response(status=200, text="OK")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return web.Response(status=500, text=str(e))


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.Response(status=200, text="REMO Bot is running!")


async def info_handler(request: web.Request) -> web.Response:
    """Info endpoint showing webhook URL."""
    info = f"""
REMO Bot Webhook Server

Webhook Path: {config.WEBHOOK_PATH}
Full Webhook URL: {config.WEBHOOK_URL}

To set webhook manually, run:
curl -X POST "https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/setWebhook" \\
  -H "Content-Type: application/json" \\
  -d '{{"url": "{config.WEBHOOK_URL}", "secret_token": "{config.WEBHOOK_SECRET}"}}'

Or use Python script: set_webhook.py
"""
    return web.Response(status=200, text=info)


# =============================================================================
# APPLICATION SETUP
# =============================================================================

async def setup_application() -> Application:
    """Create and configure the Telegram bot application."""
    
    # Build application
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .updater(None)  # We'll handle updates manually via webhook
        .build()
    )
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Power commands
    application.add_handler(CommandHandler("lock", lock_command))
    application.add_handler(CommandHandler("sleep", sleep_command))
    application.add_handler(CommandHandler("shutdown", shutdown_command))
    application.add_handler(CommandHandler("restart", restart_command))
    
    # Status
    application.add_handler(CommandHandler("status", status_command))
    
    # Display
    application.add_handler(CommandHandler("screenshot", screenshot_command))
    application.add_handler(CommandHandler("brightness", brightness_command))
    
    # Audio
    application.add_handler(CommandHandler("volume", volume_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    
    # Callback handlers for confirmations
    application.add_handler(CallbackQueryHandler(confirmation_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application


# =============================================================================
# MAIN
# =============================================================================

async def main() -> None:
    """Main entry point."""
    
    # Check configuration
    if config.TELEGRAM_USER_ID == 0:
        logger.error("=" * 60)
        logger.error("TELEGRAM_USER_ID not set!")
        logger.error("Please get your Telegram User ID from @userinfobot")
        logger.error("and update config.py or set REMO_USER_ID environment variable")
        logger.error("=" * 60)
        return
    
    logger.info("=" * 70)
    logger.info("REMO - Remote Control Bot (WEBHOOK MODE)")
    logger.info("=" * 70)
    logger.info(f"Device: {config.DEVICE_NAME} ({config.DEVICE_ID})")
    logger.info(f"Authorized User ID: {config.TELEGRAM_USER_ID}")
    logger.info(f"Webhook Host: {config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}")
    logger.info(f"Webhook Path: {config.WEBHOOK_PATH}")
    logger.info("=" * 70)
    
    # Create application
    application = await setup_application()
    
    # Initialize the application
    await application.initialize()
    await application.start()
    
    logger.info("✅ Bot application initialized")
    
    # Create aiohttp web app
    webapp = web.Application()
    webapp["bot_app"] = application
    
    # Setup dashboard routes (includes /, /login, /dashboard, etc)
    from dashboard.routes import setup_routes
    setup_routes(webapp)
    
    # Telegram webhook route
    webapp.router.add_post(config.WEBHOOK_PATH, webhook_handler)
    
    # Health check
    webapp.router.add_get("/health", health_handler)
    
    
    # Start web server
    runner = web.AppRunner(webapp)
    await runner.setup()
    
    site = web.TCPSite(runner, config.WEBHOOK_HOST, config.WEBHOOK_PORT)
    await site.start()
    
    logger.info("=" * 70)
    logger.info(f"🚀 Webhook server running on http://{config.WEBHOOK_HOST}:{config.WEBHOOK_PORT}")
    logger.info(f"📡 Webhook endpoint: {config.WEBHOOK_PATH}")
    logger.info(f"🔗 Full webhook URL: {config.WEBHOOK_URL}")
    logger.info("=" * 70)
    logger.info("")
    logger.info("⚠️  NEXT STEPS:")
    logger.info("1. Setup Cloudflare Tunnel to expose this server")
    logger.info("2. Run: python set_webhook.py")
    logger.info("   (or visit http://localhost:8443/info for manual command)")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    # Keep running until interrupted
    stop_event = asyncio.Event()
    
    def handle_signal():
        logger.info("Received shutdown signal")
        stop_event.set()
    
    # Register signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass
    
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down...")
        
        # Cleanup
        await application.stop()
        await application.shutdown()
        await runner.cleanup()
        
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
