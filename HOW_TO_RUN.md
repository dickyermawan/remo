# REMO - How to Run

## 🚀 Quick Start (Webhook Mode)

### 1. Start the Server

```bash
cd d:\Dev\App\poker-face\remo
python main.py
```

You should see:
```
✅ Bot application initialized
🚀 Webhook server running on http://0.0.0.0:8443
📡 Webhook endpoint: /webhook/1n8RQWxbU4ex8AUnkf5IZ7agy3XILhcIiGZJMc_J8AA
🔗 Full webhook URL: https://remohp/webhook/1n8RQWxbU4ex8AUnkf5IZ7agy3XILhcIiGZJMc_J8AA

⚠️  NEXT STEPS:
1. Setup Cloudflare Tunnel to expose this server
2. Run: python set_webhook.py
```

### 2. Setup Cloudflare Tunnel (Your Part)

```bash
# Install cloudflared (if not installed)
winget install Cloudflare.cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create remo-bot

# Edit cloudflared config
notepad C:\Users\<username>\.cloudflared\config.yml

# Add this configuration:
tunnel: <your-tunnel-id>
credentials-file: C:\Users\<username>\.cloudflared\<tunnel-id>.json

ingress:
  - hostname: remohp
    service: http://localhost:8443
  - service: http_status:404

# Route DNS
cloudflared tunnel route dns remo-bot remohp

# Run tunnel (in separate terminal)
cloudflared tunnel run remo-bot
```

### 3. Set Webhook to Telegram

After Cloudflare Tunnel is running:

```bash
python set_webhook.py
```

Or check current webhook status:
```bash
python set_webhook.py info
```

### 4. Test Bot

Open Telegram → Send `/start` to your bot!

---

## 🧪 Alternative: Test Mode (Polling)

If you want to test without Cloudflare Tunnel:

```bash
python main_polling.py
```

This uses polling instead of webhook (simpler but less efficient).

---

## 📌 Important Notes

- **Webhook Path is STATIC**: `/webhook/1n8RQWxbU4ex8AUnkf5IZ7agy3XILhcIiGZJMc_J8AA`
  - Saved in `.webhook_secret` file
  - Will NOT change on restart
  
- **Server runs on**: `0.0.0.0:8443` (localhost)
  
- **Cloudflare Tunnel** exposes this to the internet

---

## ⏹️ Stop Server

Press `Ctrl+C`
