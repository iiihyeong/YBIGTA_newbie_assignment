from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TCPConnectResult:
    ip: Optional[str]
    port: int
    connect_ms: Optional[float]
    local_addr: Optional[tuple[str, int]]
    peer_addr: Optional[tuple[str, int]]
    error: Optional[str]
    sock: Optional[socket.socket]


def _make_socket(ip: str, timeout: float) -> socket.socket:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(timeout)
    return s


def connect_one(ip: str, port: int, timeout: float):
    """
    특정 IP로 TCP 연결을 시도하고 지연 시간을 측정합니다.
    """
    try:
        s = _make_socket(ip, timeout)
        start = time.perf_counter()
        
        ###########################################################
        # TODO: 연결 직전과 직후의 시간을 측정하여 연결에 걸린 시간(ms)을 계산하세요.
        # HINT: time.perf_counter()를 사용하고, 단위가 초(s)이므로 1000을 곱하세요.
        
        s.connect((ip, port))
        ms = 0.0 
        
        end = time.perf_counter()
        ms = (end - start) * 1000.0

        ###########################################################

        return s, ms, None
    except Exception as e:
        try:
            s.close()
        except Exception:
            pass
        return None, None, str(e)


def connect_with_fallback(ips: list[str], port: int, timeout: float, prefer: str = "any") -> TCPConnectResult:
    """
    여러 IP 후보를 순회하며 TCP 연결이 성공할 때까지 시도합니다. (Fallback 메커니즘) 
    
    요구사항:
    1. prefer 정책(ipv4/ipv6)에 따라 IP 순회 순서(ordered list)를 결정하세요. 
    2. connect_one 함수를 사용하여 각 IP에 대해 연결을 시도하세요. 
    3. 연결 성공 시, 해당 소켓에서 local/peer 주소 정보를 추출하여 결과 객체를 반환하세요. 
    4. 모든 IP에 대해 실패할 경우 마지막 에러 메시지를 담아 반환하세요. 
    """
    if not ips:
        return TCPConnectResult(
            ip=None, port=port, connect_ms=None,
            local_addr=None, peer_addr=None,
            error="No IPs to connect", sock=None
        )

    # TODO 1: prefer 정책에 따라 v4, v6 주소의 우선순위가 반영된 ordered 리스트를 만드세요.
    # HINT: ':' 가 포함된 IP는 IPv6, '.' 이 포함된 IP는 IPv4 입니다.
    ordered = [] 
    v4 = [ip for ip in ips if "." in ip]
    v6 = [ip for ip in ips if ":" in ip]

    if prefer == "ipv4":
        ordered = v4 + v6  
    elif prefer == "ipv6":
        ordered = v6 + v4  
    else:
        ordered = ips      

    last_err: Optional[str] = None
    for ip in ordered:
        # TODO 2: connect_one을 호출하여 연결을 시도하고, 성공 시 정보를 추출하여 반환하세요.
        # HINT 1: connect_one은 성공 시 (sock, connect_ms), 실패 시 (None, error_message)를 반환합니다.
        # HINT 2: sock.getsockname()과 sock.getpeername()을 활용하세요. 
        sock, ms, err = connect_one(ip, port, timeout)
        
        if sock:
            return TCPConnectResult(
                ip=ip,
                port=port,
                connect_ms=ms,
                local_addr=sock.getsockname(),
                peer_addr=sock.getpeername(),
                error=None,
                sock=sock
            )
        
        last_err = err

    return TCPConnectResult(
        ip=ordered[-1] if ordered else None,
        port=port,
        connect_ms=None,
        local_addr=None,
        peer_addr=None,
        error=last_err or "All connections failed",
        sock=None
    )