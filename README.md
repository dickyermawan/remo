# REMO - Remote Control Bot

🤖 **Telegram bot untuk remote control laptop Windows via webhook**

Secure dashboard + Bot commands untuk:
- Power control (lock, sleep, shutdown, restart)
- System monitoring (CPU, RAM, disk, battery)
- Audio control (volume, mute)
- Screenshot capture
- Web dashboard dengan login authentication

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
# Copy template
copy .env.example .env

# Edit .env dengan:
# - Bot token dari @BotFather
# - User ID dari @userinfobot
# - Cloudflare domain
# - Dashboard credentials
```

### 3. Run Background (No Console)
```bash
# Simple double-click:
start.bat

# Or manual:
python main.pyw
```

Bot runs in background, no window!

### 4. Access Dashboard
```
http://localhost:8443/
```

Login dengan credentials dari `.env`

---

## 📦 Features

### 🤖 Telegram Bot Commands
- `/start` - Info bot dan authorized user
- `/status` - System stats (CPU, RAM, disk, battery, uptime)
- `/screenshot` - Capture & send screenshot
- `/lock` - Lock screen
- `/sleep` - Sleep mode
- `/shutdown` - Shutdown (dengan konfirmasi)
- `/restart` - Restart (dengan konfirmasi)
- `/volume <0-100>` - Set volume level
- `/mute` - Mute audio
- `/unmute` - Unmute audio

### 🌐 Web Dashboard
- ✅ Secure login (bcrypt password hashing)
- ✅ Real-time system stats (CPU, RAM, Disk, Uptime)
- ✅ Live logs viewer (auto-refresh)
- ✅ Bot status monitoring
- ✅ Mobile responsive
- ✅ Session management (24hr timeout)
- ✅ Rate limiting (5 login attempts / 15min)

### 🔒 Security
- User ID whitelist
- Webhook secret token
- Rate limiting (30 cmds/min)
- Bcrypt password hashing
- Signed session cookies (HttpOnly, SameSite)
- CSRF protection ready
- All secrets in `.env` (gitignored)

---

## 🎯 Background Mode

**Bot runs completely hidden (no console window):**

### Start Bot
```bash
start.bat          # Recommended
# or
python main.pyw    # Direct launch
```

### Stop Bot
```bash
stop.bat
```

### Auto-Start on Windows Boot
```bash
# Run as Administrator:
enable_autostart.bat

# To disable:
disable_autostart.bat
```

**Why it works:**
- Uses `main.pyw` (Windows background app)
- Logger auto-detects pythonw (skips console)
- Writes to `logs/remo.log` only

---

## 📁 Project Structure

```
remo/
├── main.py          # Main app (with console)
├── main.pyw         # Background mode (no console)
├── start.bat        # Start background
├── stop.bat         # Stop bot
├── enable_autostart.bat    # Setup auto-start
├── disable_autostart.bat   # Remove auto-start
├── config.py        # Configuration
├── .env             # Secrets (NOT committed)
├── .env.example     # Template
├── bot/
│   ├── handlers.py  # Telegram command handlers
│   └── middleware.py # Auth & rate limiting
├── system/
│   ├── power.py     # Power control
│   ├── audio.py     # Volume control
│   ├── display.py   # Screenshot & brightness
│   └── status.py    # System monitoring
├── dashboard/
│   ├── auth.py      # Authentication system
│   ├── routes.py    # Web routes & API
│   └── templates/   # HTML templates
├── utils/
│   └── logger.py    # Logging (file + console)
└── logs/
    └── remo.log     # Application logs
```

---

## 🔧 Configuration

All config in `.env` file:

```env
# Bot
REMO_BOT_TOKEN=your_bot_token
REMO_USER_ID=your_telegram_user_id

# Webhook
REMO_WEBHOOK_DOMAIN=your.domain.com
REMO_WEBHOOK_PORT=8443

# Dashboard
REMO_DASHBOARD_USERNAME=admin
REMO_DASHBOARD_PASSWORD=SecurePassword123!
REMO_DASHBOARD_SECRET_KEY=auto_generated

# Device (optional)
REMO_DEVICE_NAME=Main Laptop
REMO_DEVICE_ID=main-laptop
```

---

## 🌐 Webhook Setup

### Via Cloudflare Tunnel (Recommended)

1. **Install cloudflared**
   ```bash
   choco install cloudflared
   ```

2. **Configure tunnel** (see `cloudflared-config.yml`)

3. **Run tunnel**
   ```bash
   cloudflared tunnel run remo-bot
   ```

4. **Set webhook**
   ```bash
   python set_webhook.py set
   ```

---

## 📝 Logs

All logs in `logs/remo.log`:
- Rotation: 10 MB per file
- Retention: 7 days
- Compression: zip

View live logs dalam dashboard atau check file.

---

## 🛡️ Security Best Practices

✅ **Done:**
- All secrets in `.env` (gitignored)
- Bcrypt password hashing
- Session security (signed cookies)
- Rate limiting (bot & dashboard)
- User ID whitelist
- Webhook secret validation

⚠️ **Recommendations:**
- Use strong dashboard password
- Keep Cloudflare Tunnel running
- Update dependencies regularly
- Review `SECURITY.md` for audit details

---

## 📚 Documentation

- `QUICKSTART.md` - Simple start/stop guide
- `HOW_TO_RUN.md` - Detailed webhook setup
- `SECURITY.md` - Security audit & best practices
- `TROUBLESHOOTING.md` - Common issues
- `SERVICE_INSTALL.md` - Windows Service setup (optional)

---

## 🎉 Status

**PRODUCTION READY!**

✅ Bot working  
✅ Dashboard secure & responsive  
✅ Background mode stable  
✅ Auto-start ready  
✅ Open-source safe (no hardcoded secrets)

---

## 📜 License

MIT - Free to use & modify

---

**Made with ❤️ for remote laptop control**
