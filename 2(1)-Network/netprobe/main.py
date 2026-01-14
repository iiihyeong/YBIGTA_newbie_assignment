from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlparse

from .dns import resolve, pick_ip
from .tcp import connect_with_fallback
from .http import build_request, send_and_recv, parse_status_and_preview
from .report import print_report, save_json


@dataclass
class Report:
    url: str
    host: str
    port: int
    path: str
    dns_ips: list[str]
    chosen_ip: Optional[str]
    tcp_ms: Optional[float]
    local_addr: Optional[tuple[str, int]]
    peer_addr: Optional[tuple[str, int]]
    http_status: Optional[int]
    body_preview: str
    stage: str  # "ok" | "dns" | "tcp" | "http"
    error: Optional[str]


def parse_url(url: str) -> tuple[str, int, str]:
    p = urlparse(url)
    if p.scheme.lower() != "http":
        raise ValueError("Only http:// URLs are supported")
    if not p.hostname:
        raise ValueError("Invalid URL (missing host)")

    host = p.hostname
    port = p.port or 80
    path = p.path or "/"
    if p.query:
        path = f"{path}?{p.query}"
    return host, port, path


def _emit(r: Report, pretty: bool, json_path: str | None) -> None:
    if pretty:
        print_report(asdict(r))
    if json_path:
        save_json(asdict(r), json_path)


def run_one(url: str, prefer: str, timeout: float, json_path: str | None, pretty: bool) -> Report:
    host, port, path = parse_url(url)

    # 1) DNS
    ips, dns_err = resolve(host)
    if dns_err:
        r = Report(
            url=url, host=host, port=port, path=path,
            dns_ips=[], chosen_ip=None, tcp_ms=None,
            local_addr=None, peer_addr=None,
            http_status=None, body_preview="",
            stage="dns", error=dns_err
        )
        _emit(r, pretty, json_path)
        return r

    chosen = pick_ip(ips, prefer=prefer)

    # 2) TCP (fallback)
    tcp_res = connect_with_fallback(
        ips=ips,
        port=port,
        timeout=timeout,
        prefer=prefer,
    )

    chosen_ip = tcp_res.ip or chosen

    if tcp_res.error or tcp_res.sock is None:
        r = Report(
            url=url, host=host, port=port, path=path,
            dns_ips=ips, chosen_ip=chosen_ip, tcp_ms=tcp_res.connect_ms,
            local_addr=tcp_res.local_addr, peer_addr=tcp_res.peer_addr,
            http_status=None, body_preview="",
            stage="tcp", error=tcp_res.error or "TCP connection failed"
        )
        _emit(r, pretty, json_path)
        return r

    # 3) HTTP
    sock = tcp_res.sock
    try:
        try:
            req = build_request(host, path)
            raw = send_and_recv(sock, req, max_bytes=1_000_000)
            status, preview, http_err = parse_status_and_preview(raw, max_preview=200)

        except TimeoutError as e:
            # HTTP recv timeout은 TCP 실패로 분류
            r = Report(
                url=url, host=host, port=port, path=path,
                dns_ips=ips, chosen_ip=chosen_ip,
                tcp_ms=tcp_res.connect_ms,
                local_addr=tcp_res.local_addr, peer_addr=tcp_res.peer_addr,
                http_status=None, body_preview="",
                stage="tcp", error=str(e)
            )
            sock.close()
            _emit(r, pretty, json_path)
            return r
        
        except Exception as e:
            status, preview, http_err = None, "", str(e)

        if http_err:
            r = Report(
                url=url, host=host, port=port, path=path,
                dns_ips=ips, chosen_ip=chosen_ip, tcp_ms=tcp_res.connect_ms,
                local_addr=tcp_res.local_addr, peer_addr=tcp_res.peer_addr,
                http_status=None, body_preview="",
                stage="http", error=http_err
            )
        else:
            r = Report(
                url=url, host=host, port=port, path=path,
                dns_ips=ips, chosen_ip=chosen_ip, tcp_ms=tcp_res.connect_ms,
                local_addr=tcp_res.local_addr, peer_addr=tcp_res.peer_addr,
                http_status=status, body_preview=preview,
                stage="ok", error=None
            )
    finally:
        try:
            sock.close()
        except Exception:
            pass

    _emit(r, pretty, json_path)
    return r


def main():
    ap = argparse.ArgumentParser(prog="netprobe")
    ap.add_argument("url", help="http://host[:port][/path]")
    ap.add_argument("--prefer", choices=["any", "ipv4", "ipv6"], default="any")
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--json", dest="json_path", default=None)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    run_one(args.url, prefer=args.prefer, timeout=args.timeout, json_path=args.json_path, pretty=args.pretty)


if __name__ == "__main__":
    main()
