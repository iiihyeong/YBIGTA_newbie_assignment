from netprobe.dns import resolve

def test_resolve_localhost():
    ips, err = resolve("localhost")
    assert err is None
    assert len(ips) >= 1
