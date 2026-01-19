# Troubleshooting: Bot Not Responding

User reports bot tidak merespon command di Telegram.

## ✅ Yang Sudah Benar:

1. **Webhook set** ✅
   ```
   ✅ Webhook set successfully!
   URL: https://remohp.ermalogi.com/webhook/1n8RQWxbU4ex8AUnkf5IZ7agy3XILhcIiGZJMc_J8AA
   Pending updates: 0
   ```

2. **Server running** ✅
   ```
   Server: http://0.0.0.0:8443
   Health check: PASS
   ```

3. **Cloudflare Tunnel setup** ✅ (kata user)

---

## 🔍 Kemungkinan Masalah:

### 1. Cloudflare Tunnel tidak pointing ke localhost:8443

**Check:**
```bash
# Lihat config tunnel
cat C:\Users\<username>\.cloudflared\config.yml
```

**Harus ada:**
```yaml
ingress:
  - hostname: remohp.ermalogi.com
    service: http://localhost:8443  # <-- HARUS 8443!
```

### 2. Tunnel tidak running

**Check:**
```bash
# Apakah cloudflared running?
Get-Process cloudflared
```

**Start tunnel jika belum:**
```bash
cloudflared tunnel run remo-bot
```

### 3. Test webhook manual

**Test apakah webhook endpoint bisa diakses:**
```bash
curl https://remohp.ermalogi.com/webhook/1n8RQWxbU4ex8AUnkf5IZ7agy3XILhcIiGZJMc_J8AA
```

Should return: `403 Forbidden` (karena tidak ada secret token)

---

## 🔧 Quick Fix:

1. **Pastikan tunnel running:**
   ```bash
   cloudflared tunnel run remo-bot
   ```

2. **Pastikan main.py running:**
   ```bash
   python main.py
   ```

3. **Test di Telegram:**
   ```
   /start
   ```

4. **Check jika ada request di terminal main.py**
   - Seharusnya ada log request masuk

---

## 📋 Debug Checklist:

- [ ] Cloudflare tunnel running?
- [ ] main.py running?
- [ ] Tunnel config pointing ke localhost:8443?
- [ ] Domain remohp.ermalogi.com resolve ke Cloudflare?
- [ ] Firewall tidak block port 8443?
