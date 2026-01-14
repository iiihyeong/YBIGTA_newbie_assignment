from netprobe.tcp import connect_with_fallback

def test_connect_with_fallback_handles_empty():
    r = connect_with_fallback([], 80, timeout=0.5)
    assert r.error is not None
