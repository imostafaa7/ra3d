
<p align="center">
  <img src="https://img.shields.io/badge/ra3d-v1.0-red?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/purpose-stress--testing-red?style=for-the-badge">
</p>

```
  ╔═══╗╦═══╗╦  ╦╦═══╗╦═══╗╦═╗╔═╗
  ║╔═╗║║╔═╗║╚╗╔╝║╔═╗║║╔═╗║║╔╗║║║
  ║╚═╝║║╚═╝║ ║║ ║╚═╝║║╚═╝║║║║║║║╚╗
  ║╔══╣║╔═╗║ ║║ ║╔══╣║╔═╗║║║║║║║ ║
  ║║  ║║╚═╝║ ║║ ║║  ║║╚═╝║║╚╝║║╚═╝║
  ╚╝  ╚╩═══╩ ╚╝ ╚╝  ╚╩═══╩╩══╝╩═══╝
```

<p align="center">
  <b>رعد</b> — <i>thunder that doesn't knock twice</i>
</p>

# ra3d (رعد) 🔴

**HTTP Stress Testing Engine — رعد**

ra3d is a high-performance, socket-based HTTP stress testing tool with a beautiful real-time terminal dashboard. It launches thousands of concurrent connections against a target, rotates User-Agents and headers dynamically, and displays live statistics with RPS sparklines, response time percentiles, and status code breakdown — all in a striking red-themed interface.

---

## 📖 Overview

| Aspect | Detail |
|---|---|
| **Architecture** | Pure socket-level (no heavy libs) — maximum speed |
| **Protocol** | HTTP/1.1 with keep-alive |
| **Transport** | Raw TCP sockets + SSL/TLS support |
| **Display** | Real-time dashboard updated every 1 second |
| **Threading** | Configurable worker threads (default: 50) |

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ **Raw socket engine** | No requests/urllib3 — direct TCP for max throughput |
| 📊 **Live dashboard** | RPS, total requests, elapsed time, response times |
| 📈 **RPS sparkline** | 60-second trend bar chart using Unicode blocks |
| ⏱ **Percentiles** | P50, P95, P99 response times |
| 🌐 **UA rotation** | 10+ User-Agents (browsers, bots, mobile) |
| 🔀 **Multi-method** | GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS |
| 🎲 **Random URL** | Append random paths to bypass caching |
| 🧪 **Custom body** | Request body with `{rand}` placeholder |
| 🧷 **Custom headers** | Repeatable `--header` flag |
| 🍪 **Cookie support** | Set cookies via `--cookie` |
| ⏲ **Duration mode** | `--time N` seconds |
| 🔢 **Count mode** | `-n N` total requests |
| ⏳ **Delay control** | `-d N` ms between requests |
| 🤫 **Quiet mode** | `-q` for headless operation |
| 🎯 **Summary screen** | Full stats on completion |

---

## 📦 Installation

```bash
# Save the script
nano ~/Tools/ra3d

# Make executable
chmod +x ~/Tools/ra3d

# Or
wget -O ~/Tools/ra3d https://raw.githubusercontent.com/your/ra3d/main/ra3d
chmod +x ~/Tools/ra3d

# Symlink to PATH
sudo ln -sf ~/Tools/ra3d /usr/local/bin/ra3d

# Run
ra3d https://target.com
```

---

## 🚀 Usage

### Basic

```bash
ra3d https://target.com                          # 50 threads, GET only
ra3d https://target.com -t 100                   # 100 threads
ra3d https://target.com -m GET POST              # Mixed methods
ra3d https://target.com -n 10000                 # 10,000 requests total
ra3d https://target.com --time 30                # Run for 30 seconds
ra3d https://target.com -d 50                    # 50ms delay between requests
```

### Advanced

```bash
# Deep stress — 200 threads, random URLs, mixed methods, 5 min
ra3d https://target.com -t 200 -m GET POST PUT --time 300 --random-url

# Application-layer DDoS simulation
ra3d https://target.com/api/login -t 100 -m POST --body 'user=admin&pass={rand}'

# Session-based testing
ra3d https://target.com/dashboard --cookie 'session=abc123' -t 50 -n 5000

# Stealth mode (slower, more realistic)
ra3d https://target.com -t 10 -d 200 --time 60

# Quick burst
ra3d https://target.com -t 500 -n 10000

# Headless / scripting
ra3d https://target.com -t 50 --time 30 -q
```

### Options

```
Positional:
  target                    Target URL (e.g., https://example.com)

General:
  -t, --threads N           Number of worker threads (default: 50)
  -m, --methods LIST        HTTP methods: GET POST PUT DELETE PATCH HEAD OPTIONS
  -d, --delay N             Delay between requests in milliseconds
  --timeout N               Socket timeout in seconds (default: 10)

Duration (mutually exclusive):
  -n, --max-requests N      Stop after N total requests
  --time N                  Run for N seconds

Request:
  --body TEXT               Request body (use {rand} for random values)
  --header HEADER           Custom header, repeatable (e.g., --header "X-API: key")
  --cookie TEXT             Cookie header value
  --random-url              Append random path segments to evade caches

Output:
  -q, --quiet               Disable live dashboard (for scripting)
  --proxy URL               HTTP proxy (not yet implemented — coming soon)
```

---

## 📊 Live Dashboard

```
  ╔══════════════════════════════════════════════╗
  ║                  رعد                         ║
  ║         RA3D — HTTP STRESS ENGINE            ║
  ╚══════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────┐
  │  Target:     https://target.com                │
  │  Methods:    GET,POST                          │
  │  Threads:    100                               │
  │  Duration:   0:45 remaining                    │
  └────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────┐
  │  RPS Trend:  ▇▇▆▇█▇▆▅▇█▇▆▅▄▃▂▁▂▃▄▅▆▇         │
  │  Current:    1245.3 req/s     Avg: 1120.8      │
  │  Total:      56,892 req      Time: 0:45        │
  │  ────────────────────────────────────────────── │
  │  Avg time:   42.18 ms                           │
  │  Min/Max:    12.3 / 893.4 ms                    │
  │  P50/P95/P99: 38.2/98.7/245.1 ms                │
  │  ────────────────────────────────────────────── │
  │  Sent:      4,892 KB          Recv: 12,341 KB   │
  │  ────────────────────────────────────────────── │
  │  OK:         52,341              Fail: 4,551    │
  │  HTTP 200:   48,234                             │
  │  HTTP 301:     1,203                            │
  │  HTTP 403:     2,904                            │
  │  HTTP 500:     1,548                            │
  │  Errors:      4,551                             │
  │     timeout:    892                             │
  │     refused:  3,201                             │
  │     other:      458                             │
  └────────────────────────────────────────────────┘

  Press Ctrl+C to stop
```

---

## 📈 Summary Screen

```
  ╔══════════════════════════════════════════════════════╗
  ║                   ATTACK COMPLETE                    ║
  ╠══════════════════════════════════════════════════════╣
  ║  Target:      https://target.com                     ║
  ║  Duration:    45.2s                                  ║
  ║  Threads:     100                                    ║
  ║  Total req:   56,892                                 ║
  ║  RPS:         1,258.4                                ║
  ╠══════════════════════════════════════════════════════╣
  ║  Avg time:    42.18 ms                               ║
  ║  Success:     52,341                                 ║
  ║  Failed:      4,551                                  ║
  ║  HTTP 200:    48,234                                 ║
  ║  HTTP 301:     1,203                                 ║
  ║  HTTP 403:     2,904                                 ║
  ║  HTTP 500:     1,548                                 ║
  ║  Sent:        4,892 KB                               ║
  ║  Recv:       12,341 KB                               ║
  ╚══════════════════════════════════════════════════════╝
```

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────┐
│                  ra3d ENGINE                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
│  │Worker 1│  │Worker 2│  │Worker N│  │ Display│    │
│  │ (socket)│  │ (socket)│  │ (socket)│  │ (UI)   │    │
│  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘    │
│      │           │           │           │          │
│      ▼           ▼           ▼           ▼          │
│  ┌─────────────────────────────────────────┐        │
│  │          Target Server:443/80           │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
│  Thread Pool: N workers                             │
│  Each worker:                                       │
│    1. Open socket (or SSL wrap)                     │
│    2. Build HTTP request (random UA/ref/accept)     │
│    3. Send request                                  │
│    4. Read response (parse status code)             │
│    5. Record: status, duration, bytes               │
│    6. Close socket                                  │
│    7. Optional delay                                │
│    8. Repeat until stop signal                      │
│                                                      │
│  Stats shared via thread-safe lock                  │
│  Display thread renders dashboard every 1s          │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Performance

| Threads | Target | RPS (avg) | CPU | Memory |
|---|---|---|---|---|
| 50 | Local | ~8,000 | 15% | 15 MB |
| 100 | Local | ~14,000 | 30% | 25 MB |
| 200 | Local | ~22,000 | 55% | 45 MB |
| 500 | Local | ~35,000 | 85% | 90 MB |
| 50 | Remote | ~1,200 | 8% | 15 MB |
| 200 | Remote | ~3,500 | 25% | 45 MB |

*Performance depends on network latency, server capacity, and CPU cores.*

---

## 🎯 Use Cases

| Scenario | Command |
|---|---|
| **Load testing** | `ra3d https://app.example.com -t 100 --time 120 -q` |
| **Rate limit testing** | `ra3d https://api.example.com -t 200 -n 10000` |
| **WAF stress** | `ra3d https://example.com -t 300 -m GET POST PUT DELETE --random-url` |
| **Login brute simulation** | `ra3d https://example.com/login -m POST --body 'user=admin&pass={rand}' -t 50 --time 60` |
| **Cache bypass** | `ra3d https://cdn.example.com/file.pdf -t 100 --random-url -n 50000` |
| **Session persistence** | `ra3d https://app.example.com/dashboard --cookie 'token=abc123' -t 20 --time 300` |
| **Endpoint fuzzing (load)** | `ra3d https://example.com/api/v1/users -t 50 -m GET PUT DELETE PATCH -n 20000` |

---

## ⚠️ Disclaimer

```
ra3d is intended for:
  ✅ Authorized penetration testing
  ✅ Load testing your own infrastructure
  ✅ Educational purposes in lab environments

ra3d is NOT intended for:
  ❌ Unauthorized attacks against any system
  ❌ Denial-of-service attacks without written consent
  ❌ Any illegal activity

The author assumes NO responsibility for misuse.
You are solely responsible for complying with all applicable laws.
```

---

<p align="center">
  <b>رعد</b> — <i>strike hard, strike fast</i>
</p>

<p align="center">
  <sub>Built with 🔴 in Python | Red Team Tooling</sub>
</p>
