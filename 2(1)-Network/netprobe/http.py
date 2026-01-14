from __future__ import annotations

from typing import Optional


def build_request(host: str, path: str) -> bytes:
    """
    HTTP GET 요청 메시지를 바이트 형태로 생성합니다.
    """
    if not path.startswith("/"):
        path = "/" + path

    ###########################################################
    # TODO: HTTP/1.1 규격에 맞게 요청 문자열(GET, Host, Connection 헤더 포함)을 완성하세요.
    # HINT: 각 줄의 끝은 \r\n이며, 헤더의 끝에는 빈 줄(\r\n)이 하나 더 필요합니다.
    
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    
    ###########################################################

    return req.encode("utf-8")


def send_and_recv(sock, request: bytes, max_bytes: int) -> bytes:
    
    sock.sendall(request)

    chunks: list[bytes] = []
    total = 0
    while True:
        data = sock.recv(4096)
        if not data:
            break
        chunks.append(data)
        total += len(data)
        if total > max_bytes:
            break
    return b"".join(chunks)


def parse_status_and_preview(raw: bytes, max_preview: int = 200) -> tuple[Optional[int], str, Optional[str]]:
    """
    서버의 Raw 응답 데이터를 분석하여 상태 코드와 본문 미리보기를 추출합니다. 
    
    요구사항:
    1. 헤더와 바디를 구분하는 CRLF 2번(b"\\r\\n\\r\\n")의 위치를 찾으세요. 
    2. 헤더 영역을 decode한 뒤, Status Line(첫 줄)에서 상태 코드를 추출하세요. 
    3. 바디 영역에서 max_preview 만큼의 데이터를 decode하여 반환하세요. 
    4. 규격에 맞지 않는 데이터가 들어올 경우 적절한 에러 메시지를 반환하세요. 
    """
    
    ###########################################################
    # TODO: HTTP 응답 파싱 로직 전체를 직접 구현하세요.
    # 1. b"\r\n\r\n"를 기준으로 헤더와 바디를 분리합니다.
    # 2. 첫 줄(Status Line)에서 상태 코드(int)를 추출합니다. 
    # 3. 바디 영역을 max_preview 만큼 decode하여 preview를 만듭니다. 

    # HINT 1: raw.find(b"\\r\\n\\r\\n")으로 헤더와 바디의 경계를 나눕니다.
    # HINT 2: header.split("\\r\\n")의 첫 번째 줄을 다시 공백으로 split하면 상태 코드를 찾을 수 있습니다.

    status_code = None
    preview = ""
    error = None

    try:
        boundary = raw.find(b"\r\n\r\n")
        
        if boundary == -1:
            return None, "", "Invalid HTTP response: No header-body separator"


        header_part = raw[:boundary].decode("utf-8", errors="replace")

        body_part = raw[boundary + 4:]

        status_line = header_part.split("\r\n")[0]
        status_code = int(status_line.split(" ")[1])

        preview = body_part.decode("utf-8", errors="replace")[:max_preview]

    except Exception as e:
        status_code = None
        preview = ""
        error = f"Parsing error: {str(e)}"

    ###########################################################
    
    return status_code, preview, error