import json

def print_report(r: dict) -> None:
    print(f"[URL] {r['url']}")
    print(f"[DNS] ips={r['dns_ips']}")
    print(f"[CHOSEN] ip={r['chosen_ip']}")
    print(f"[TCP] ms={r['tcp_ms']}, local={r['local_addr']}, peer={r['peer_addr']}")
    print(f"[HTTP] status={r['http_status']}")
    if r["stage"] != "ok":
        print(f"[ERROR] stage={r['stage']} error={r['error']}")
    print("[BODY PREVIEW]")
    print(r["body_preview"])

def save_json(r: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
