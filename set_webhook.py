#!/usr/bin/env python3
# REMO - Set Webhook Helper Script
# Run this AFTER Cloudflare Tunnel is setup

import sys
import asyncio
from telegram import Bot
from loguru import logger

import config


async def set_webhook():
    """Set the webhook URL in Telegram."""
    
    logger.info("=" * 60)
    logger.info("Setting Telegram Webhook")
    logger.info("=" * 60)
    logger.info(f"Webhook URL: {config.WEBHOOK_URL}")
    logger.info(f"Secret Token: {config.WEBHOOK_SECRET[:10]}...")
    logger.info("=" * 60)
    
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    try:
        # Delete existing webhook
        logger.info("Deleting existing webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Set new webhook
        logger.info("Setting new webhook...")
        result = await bot.set_webhook(
            url=config.WEBHOOK_URL,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        
        if result:
            logger.info("✅ Webhook set successfully!")
            
            # Verify
            webhook_info = await bot.get_webhook_info()
            logger.info("")
            logger.info("Webhook Info:")
            logger.info(f"  URL: {webhook_info.url}")
            logger.info(f"  Pending updates: {webhook_info.pending_update_count}")
            logger.info(f"  Max connections: {webhook_info.max_connections}")
            if webhook_info.last_error_message:
                logger.warning(f"  Last error: {webhook_info.last_error_message}")
        else:
            logger.error("❌ Failed to set webhook")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            await bot.close()
        except:
            pass


async def delete_webhook():
    """Delete the webhook (switch to polling)."""
    
    logger.info("Deleting webhook...")
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    try:
        result = await bot.delete_webhook(drop_pending_updates=True)
        if result:
            logger.info("✅ Webhook deleted successfully!")
        else:
            logger.error("❌ Failed to delete webhook")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        try:
            await bot.close()
        except:
            pass


async def get_webhook_info():
    """Get current webhook info."""
    
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    try:
        webhook_info = await bot.get_webhook_info()
        
        logger.info("=" * 60)
        logger.info("Current Webhook Info")
        logger.info("=" * 60)
        logger.info(f"URL: {webhook_info.url or '(not set)'}")
        logger.info(f"Pending updates: {webhook_info.pending_update_count}")
        logger.info(f"Max connections: {webhook_info.max_connections}")
        if webhook_info.last_error_date:
            logger.info(f"Last error date: {webhook_info.last_error_date}")
        if webhook_info.last_error_message:
            logger.warning(f"Last error: {webhook_info.last_error_message}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        try:
            await bot.close()
        except:
            pass


def main():
    """Main entry point."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "set":
            asyncio.run(set_webhook())
        elif command == "delete":
            asyncio.run(delete_webhook())
        elif command == "info":
            asyncio.run(get_webhook_info())
        else:
            print(f"Unknown command: {command}")
            print("Usage: python set_webhook.py [set|delete|info]")
            sys.exit(1)
    else:
        # Default: set webhook
        asyncio.run(set_webhook())


if __name__ == "__main__":
    main()
