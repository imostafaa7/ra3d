# رعد — RA3D v2.0

**HTTP Stealth Stress & Evasion Engine**  
محرك اختبار ضغط خفي مع تناوب البروكسيات والتخفي التام

```
  ╔══════════════════════════════════════════════╗
  ║                  رعد                         ║
  ║       RA3D v2 — STEALTH ENGINE               ║
  ╚══════════════════════════════════════════════╝
```

---

## المميزات

- **خواديم بروكسي** — تحميل تلقائي من 6 مصادر + إضافة يدوي + blacklist للفاشل
- **تخفي كامل** — تناوب User-Agent / Referer / Accept-Language عشوائياً
- **التفاف IP** — X-Forwarded-For و X-Real-IP مزيفة
- **منع التخزين المؤقت** — Cache-Bust + Random URL + Pragma no-cache
- **وضع Stealth** — 10 threads + 200ms تأخير + Jitter 100ms + Proxies
- **وضع Aggressive** — 200 thread + 5s timeout لأقصى ضغط
- **SOCK5 Proxy** — دعم بروكسيات SOCKS عبر PySocks
- **لوحة تحكم مباشر** — RPS + Sparkline + P50/P95/P99 + حجم البيانات
- **تثبيت تلقائي** — يشوف النواقص وينصبها

---

## التثبيت

```bash
chmod +x ra3d.py
sudo mv ra3d.py /usr/local/bin/ra3d
```

ما يحتاج تثبيت — السكريبت ينصب dependencies تلقائياً (requests + PySocks).

---

## الاستخدام

### الوضع الخفي (أوصى به)
```bash
ra3d https://example.com --stealth
```
- 10 threads | 200ms delay | 100ms jitter | proxy rotate | X-Forwarded-For

### الوضع العادي
```bash
ra3d https://example.com
```
- 50 threads | بدون تأخير | بدون بروكسيات

### الوضع العنيف
```bash
ra3d https://example.com --aggressive -m GET POST
```
- 200 threads | 5s timeout | أقصى ضغط

### مع بروكسيات
```bash
ra3d https://example.com --proxy-rotate
ra3d https://example.com --proxy-rotate --proxy-file proxies.txt
ra3d https://example.com --proxy http://1.2.3.4:8080
```

### تحديد مدة أو عدد
```bash
ra3d https://example.com --time 60            # دقيقة
ra3d https://example.com -n 1000              # 1000 طلب
ra3d https://example.com --time 300 -q        # 5 دقايق بدون شاشة
```

### طرق متعددة
```bash
ra3d https://example.com -m GET POST PUT
```

### تخفي إضافي
```bash
ra3d https://example.com --random-url --cache-bust --x-forwarded --jitter 50 -d 100
```

### هيدرات وبودي مخصص
```bash
ra3d https://example.com -m POST --body "user=admin&pass={rand}" --cookie "session=abc123" --header "X-API-Key: test123"
```

---

## جميع الخيارات

| الخيار | الوصف |
|--------|-------|
| `target` | رابط الهدف (مطلوب) |
| `-t, --threads` | عدد الخيوط (default: 50) |
| `-m, --methods` | الطرق: GET POST PUT DELETE PATCH HEAD |
| `-d, --delay` | تأخير بالميلي ثانية |
| `--jitter` | تمويج عشوائي ± (ms) |
| `--timeout` | مهلة الاتصال (s) |
| `-n, --max-requests` | يتوقف بعد N طلب |
| `--time` | يتوقف بعد N ثانية |
| `--proxy-rotate` | يحمل بروكسيات من النت ويبدلهم |
| `--proxy-file` | ملف بروكسيات (ip:port لكل سطر) |
| `--proxy` | بروكسي واحد (http://ip:port) |
| `--random-url` | مسارات URL عشوائية |
| `--cache-bust` | إضافة معامل لمنع التخزين |
| `--x-forwarded` | تزوير X-Forwarded-For |
| `--stealth` | الوضع الخفي الكامل |
| `--aggressive` | الوضع العنيف |
| `--body` | نص الطلب ({rand} يصير رقم عشوائي) |
| `--header` | هيدر مخصص (يتكرر) |
| `--cookie` | قيمة Cookie |
| `-q, --quiet` | بدون شاشة عرض |
| `--no-install` | لا ينصب dependencies |

---

## لوحة التحكم

```
  ╔══════════════════════════════════════════════╗
  ║                  رعد                         ║
  ║       RA3D v2 — STEALTH ENGINE               ║
  ╚══════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────┐
  │  Target:     https://example.com             │
  │  Methods:    GET,POST                        │
  │  Threads:    10    Proxy: 1427               │
  │  Duration:   45s                             │
  └──────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────┐
  │  RPS Trend:  ▂▃▅▇██▇▆▅▄▃▂▁                  │
  │  Current:     142.3 req/s     Avg: 138.7     │
  │  Total:       6,382 req     Time: 0:00:46    │
  │  ------------------------------------------- │
  │  Avg time:   72.34 ms                         │
  │  Min/Max:    12.1 / 345.6 ms                 │
  │  P50/P95/P99: 45.2/210.8/312.4 ms            │
  │  ------------------------------------------- │
  │  Sent:       427.1 KB      Recv: 1.2 MB       │
  │  ------------------------------------------- │
  │  OK:         6,382        Fail: 0             │
  │  HTTP 200:   6,382                            │
  └──────────────────────────────────────────────┘

  Ctrl+C to stop  |  Proxy pool: 1427 active
```

---

## هيكل المشروع

```
~/Tools/
├── ra3d              # السكريبت الرئيسي
└── proxies.txt       # ملف بروكسيات (اختياري)
```

---

## الترخيص

للاستخدام التعليمي والأبحاث الأمنية فقط.  
**For educational and security research purposes only.**
