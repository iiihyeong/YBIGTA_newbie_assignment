from netprobe.http import build_request, parse_status_and_preview

def test_build_request_has_host_and_crlf():
    raw = build_request("example.com", "/")
    s = raw.decode("utf-8")
    assert s.startswith("GET / HTTP/1.1\r\n")
    assert "Host: example.com\r\n" in s
    assert s.endswith("\r\n\r\n")

def test_parse_status_and_preview():
    raw = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"\r\n"
        b"HELLO_WORLD"
    )
    status, preview, err = parse_status_and_preview(raw, max_preview=5)
    assert err is None
    assert status == 200
    assert preview == "HELLO"
