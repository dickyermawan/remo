# REMO - Simple Start/Stop Guide

## 🚀 Quick Start

### Start Bot (Background)
```batch
start.bat
```

Bot runs in background, no window.

### Stop Bot
```batch
stop.bat
```

Stops all REMO processes.

---

## ⚙️ Auto-Start on Boot (Optional)

### Enable Auto-Start
```batch
enable_autostart.bat
```

**Run as Administrator**

Bot will auto-start when you log in to Windows.

### Disable Auto-Start
```batch
disable_autostart.bat
```

**Run as Administrator**

---

## 📋 Available Scripts

| Script | Function |
|--------|----------|
| `start.bat` | Start bot in background |
| `stop.bat` | Stop bot |
| `enable_autostart.bat` | Enable auto-start on boot |
| `disable_autostart.bat` | Disable auto-start |

---

## 🔍 Check if Running

Open Task Manager → Look for `pythonw.exe` process

Or check:
```
http://localhost:8443/
```

If dashboard loads → Bot is running! ✅

---

## 📝 Logs

Check `logs\remo.log` for activity and errors.

---

## ⚠️ Troubleshooting

**Bot tidak start?**
- Check `.env` file exists and configured
- Check `logs\remo.log` for errors
- Run `python main.py` directly to see errors

**Port 8443 already in use?**
- Stop other instances: `stop.bat`
- Or kill manually: `taskkill /F /IM pythonw.exe`

**Auto-start not working?**
- Run `enable_autostart.bat` as Administrator
- Check Task Scheduler: "REMO Bot Auto-Start" task exists

---

Super simple! No NSSM, no Windows Service complexity! 🎉
