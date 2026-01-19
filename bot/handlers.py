# REMO - Telegram Bot Command Handlers

import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

import config
from bot.middleware import authorized_only, log_callback
from system.power import power
from system.audio import audio
from system.display import display
from system.status import status


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def needs_confirmation(command: str) -> bool:
    """Check if command needs confirmation."""
    return config.CONFIRM_COMMANDS.get(command, False)


async def send_confirmation(
    update: Update, 
    command: str, 
    action_description: str
) -> None:
    """Send confirmation buttons for dangerous commands."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, do it", callback_data=f"confirm_{command}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ **Confirmation Required**\n\n"
        f"Are you sure you want to {action_description}?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# =============================================================================
# BASIC COMMANDS
# =============================================================================

@authorized_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    
    welcome_message = f"""
👋 **Welcome to REMO, {user.first_name}!**

🖥️ Remote Control for your laptop.

**Available Commands:**

🔐 **Power Controls**
├ /lock - Lock screen
├ /sleep - Sleep mode
├ /shutdown - Shutdown PC
└ /restart - Restart PC

📊 **Status**
└ /status - CPU, RAM, Battery info

📸 **Display**
├ /screenshot - Capture screen
└ /brightness `[0-100]` - Set brightness

🔊 **Audio**
├ /volume `[0-100]` - Set volume
├ /mute - Mute audio
└ /unmute - Unmute audio

ℹ️ /help - Show this message

🛡️ Device: `{config.DEVICE_NAME}`
"""
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


@authorized_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await start_command(update, context)


# =============================================================================
# POWER COMMANDS
# =============================================================================

@authorized_only
async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /lock command."""
    if needs_confirmation("lock"):
        await send_confirmation(update, "lock", "lock the screen")
        return
    
    success, message = await power.lock_screen()
    await update.message.reply_text(message)


@authorized_only
async def sleep_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sleep command."""
    if needs_confirmation("sleep"):
        await send_confirmation(update, "sleep", "put the computer to sleep")
        return
    
    success, message = await power.sleep()
    await update.message.reply_text(message)


@authorized_only
async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shutdown command."""
    if needs_confirmation("shutdown"):
        await send_confirmation(update, "shutdown", "shutdown the computer")
        return
    
    success, message = await power.shutdown()
    await update.message.reply_text(message)


@authorized_only
async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /restart command."""
    if needs_confirmation("restart"):
        await send_confirmation(update, "restart", "restart the computer")
        return
    
    success, message = await power.restart()
    await update.message.reply_text(message)


# =============================================================================
# STATUS COMMANDS
# =============================================================================

@authorized_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    await update.message.reply_text("⏳ Getting system status...")
    
    success, message = await status.get_full_status()
    await update.message.reply_text(message, parse_mode="Markdown")


# =============================================================================
# DISPLAY COMMANDS
# =============================================================================

@authorized_only
async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /screenshot command."""
    await update.message.reply_text("📸 Capturing screenshot...")
    
    success, message, image_bytes = await display.take_screenshot()
    
    if success and image_bytes:
        await update.message.reply_photo(
            photo=io.BytesIO(image_bytes),
            caption="🖥️ Screenshot captured"
        )
    else:
        await update.message.reply_text(message)


@authorized_only
async def brightness_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /brightness command."""
    args = context.args
    
    if not args:
        # Show current brightness
        success, message, level = await display.get_brightness()
        await update.message.reply_text(message)
        return
    
    try:
        level = int(args[0])
        success, message = await display.set_brightness(level)
        await update.message.reply_text(message)
    except ValueError:
        await update.message.reply_text("❌ Please provide a number between 0-100")


# =============================================================================
# AUDIO COMMANDS
# =============================================================================

@authorized_only
async def volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /volume command."""
    args = context.args
    
    if not args:
        # Show current volume
        success, message, level = await audio.get_volume()
        await update.message.reply_text(message)
        return
    
    try:
        level = int(args[0])
        success, message = await audio.set_volume(level)
        await update.message.reply_text(message)
    except ValueError:
        await update.message.reply_text("❌ Please provide a number between 0-100")


@authorized_only
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mute command."""
    success, message = await audio.mute()
    await update.message.reply_text(message)


@authorized_only
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unmute command."""
    success, message = await audio.unmute()
    await update.message.reply_text(message)


# =============================================================================
# CALLBACK HANDLERS
# =============================================================================

@log_callback
async def confirmation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirmation button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "cancel":
        await query.edit_message_text("❌ Operation cancelled.")
        return
    
    # Parse confirmation action
    if data.startswith("confirm_"):
        action = data.replace("confirm_", "")
        
        if action == "lock":
            success, message = await power.lock_screen()
        elif action == "sleep":
            success, message = await power.sleep()
        elif action == "shutdown":
            success, message = await power.shutdown()
        elif action == "restart":
            success, message = await power.restart()
        else:
            message = "❌ Unknown action"
        
        await query.edit_message_text(message)


# =============================================================================
# ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            f"❌ An error occurred: {context.error}"
        )
