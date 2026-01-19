# REMO - Service Installation

## ✅ One-Click Install (Recommended)

**Simply run:**
```batch
install_service.bat
```

**As Administrator** (Right-click → "Run as Administrator")

The script will:
1. ✅ Auto-download NSSM (from GitHub)
2. ✅ Install Windows Service
3. ✅ Configure auto-start
4. ✅ Start the service

**That's it!** Service akan running dan auto-start setiap boot.

---

## 📋 Requirements

- Windows 10/11
- Python 3.9+ installed
- `.env` file configured (copy from `.env.example`)
- Run as Administrator

---

## ⚙️ Service Management

### Check Status
```batch
nssm status REMO
```

### Stop Service
```batch
nssm stop REMO
```

### Start Service
```batch
nssm start REMO
```

### Restart Service
```batch
nssm restart REMO
```

### View Logs
```
logs\service_stdout.log
logs\service_stderr.log
logs\remo.log
```

---

## 🗑️ Uninstall

```batch
uninstall_service.bat
```

(Run as Administrator)

---

## 🔧 Manual Troubleshooting

If auto-install fails, check:

1. **Python in PATH?**
   ```
   where python
   ```

2. **.env file exists?**
   ```
   dir .env
   ```

3. **Run as Administrator?**
   - Right-click script → "Run as Administrator"

4. **Logs for errors:**
   ```
   type logs\service_stderr.log
   ```

---

## 🚀 After Installation

Service is now running! Access dashboard:

**http://localhost:8443/**

Login credentials from your `.env` file.

Bot will auto-start on Windows boot! 🎉
