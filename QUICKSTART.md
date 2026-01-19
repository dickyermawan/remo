# 🚀 Quick Start Guide - REMO Bot

## ✅ Bot Sudah Berjalan!

Bot REMO sudah running dalam **POLLING MODE** (test mode tanpa perlu Cloudflare Tunnel).

```
✅ Bot started successfully!
📡 Polling for updates...
```

---

## 🧪 Test Sekarang!

### 1. Buka Telegram
Cari bot kamu di Telegram (using bot username from your `.env` file)

### 2. Kirim Command
Coba kirim salah satu command ini:

```
/start
/status
/screenshot
/volume
/lock
```

### 3. Test Power Commands (dengan konfirmasi)
```
/shutdown
/restart  
/sleep
```
Bot akan minta konfirmasi dengan tombol Yes/No

---

## 📝 Semua Command

| Command | Fungsi |
|---------|--------|
| `/start` | Welcome message |
| `/help` | Daftar semua command |
| **🔐 Power** ||
| `/lock` | Lock screen |
| `/sleep` | Sleep mode (konfirmasi) |
| `/shutdown` | Shutdown PC (konfirmasi) |
| `/restart` | Restart PC (konfirmasi) |
| **📊 Status** ||
| `/status` | CPU, RAM, Battery, Disk, Uptime |
| **📸 Display** ||
| `/screenshot` | Capture screen → kirim ke Telegram |
| `/brightness` | Lihat brightness |
| `/brightness 50` | Set brightness 50% |
| **🔊 Audio** ||
| `/volume` | Lihat volume |
| `/volume 75` | Set volume 75% |
| `/mute` | Mute audio |
| `/unmute` | Unmute audio |

---

## 🔄 Mode: Polling vs Webhook

### Saat Ini: **Polling Mode** ✅
- **File:** `main_polling.py`
- **Cara Run:** `python main_polling.py`
- **Keuntungan:** Simple, langsung jalan, tidak perlu setup domain
- **Kekurangan:** Bot harus selalu running di laptop

### Production: **Webhook Mode**
- **File:** `main.py`
- **Requirement:** Cloudflare Tunnel + Domain setup
- **Keuntungan:** Lebih efisien, real-time
- **Setup:** Lihat `README.md`

---

## ⏹️ Stop Bot

Tekan `Ctrl+C` untuk stop bot.

---

## 🔒 Security

✅ Bot hanya menerima command dari User ID yang di-set di `.env` file

✅ User lain yang coba kirim command akan ditolak dengan:
```
⛔ Access denied. You are not authorized to use this bot.
```

---

## 📦 Next Steps

### Untuk Production (nanti):
1. Setup Cloudflare Tunnel
2. Pointing domain (dari `.env` file)
3. Run `main.py` (webhook mode)
4. Install sebagai Windows Service (auto-start)

**Untuk sekarang:** Test dulu dengan `main_polling.py` sampai yakin semua command works! 🎉
