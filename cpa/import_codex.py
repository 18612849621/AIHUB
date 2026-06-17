#!/usr/bin/env python3
"""
批量导入 Codex OAuth JSON 文件到 CPA (cli-proxy-api).

用法:
  python3 cpa-import <json目录>
  python3 cpa-import /path/to/keys/
  python3 cpa-import file1.json file2.json

环境变量:
  CPA_PORT             - CPA 端口, 默认 8317
  CPA_CONFIG           - CPA config.yaml 路径 (自动检测)
  CPA_MANAGEMENT_KEY   - CPA 管理密钥 (必填)
"""

import json, os, sys, base64, subprocess, time
from pathlib import Path

CPA_PORT = os.environ.get("CPA_PORT", "8317")
CPA_MANAGEMENT_KEY = os.environ.get("CPA_MANAGEMENT_KEY", "")

# Auto-detect config.yaml path
def _find_config():
    if "CPA_CONFIG" in os.environ:
        return os.environ["CPA_CONFIG"]
    search_paths = [
        "/root/cliproxyapi/config.yaml",
        "/opt/cliproxyapi/config.yaml",
        os.path.expanduser("~/cliproxyapi/config.yaml"),
    ]
    for p in search_paths:
        if os.path.isfile(p):
            return p
    # Also search /home/*/cliproxyapi/config.yaml
    for d in Path("/home").glob("*/cliproxyapi/config.yaml"):
        return str(d)
    return ""

CPA_CONFIG = _find_config()

# Auto-detect CPA binary path
def _find_binary():
    search_paths = [
        "/root/cliproxyapi/cli-proxy-api",
        "/opt/cliproxyapi/cli-proxy-api",
    ]
    for p in search_paths:
        if os.path.isfile(p):
            return p
    if CPA_CONFIG:
        d = Path(CPA_CONFIG).parent / "cli-proxy-api"
        if d.is_file():
            return str(d)
    return "cli-proxy-api"

CPA_BINARY = _find_binary()
API_BASE = f"http://127.0.0.1:{CPA_PORT}"


def decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except: return {}


def parse_codex_file(filepath: str) -> dict | None:
    with open(filepath) as f:
        data = json.load(f)
    if data.get("type") != "codex":
        return None
    token = data.get("access_token", "")
    if not token:
        return None
    jwt = decode_jwt_payload(token)
    auth = jwt.get("https://api.openai.com/auth", {})
    profile = jwt.get("https://api.openai.com/profile", {})
    return {
        "email": profile.get("email") or data.get("email", "?"),
        "user_id": auth.get("user_id", "?"),
        "access_token": token,
        "plan": data.get("plan_type", "free"),
        "expired": data.get("expired", "?"),
    }


def api(method: str, path: str, data=None) -> dict:
    if not CPA_MANAGEMENT_KEY:
        print("❌ 请设置环境变量 CPA_MANAGEMENT_KEY (CPA 管理密钥)")
        sys.exit(1)
    cmd = ["curl", "-s", "-X", method,
           "-H", f"X-Management-Key: {CPA_MANAGEMENT_KEY}",
           "-H", "Content-Type: application/json"]
    if data is not None:
        tmp = "/tmp/cpa_api.json"
        with open(tmp, 'w') as f:
            json.dump(data, f)
        cmd += ["-d", f"@{tmp}"]
    cmd.append(f"{API_BASE}{path}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(r.stdout) if r.stdout else {}
    except: return {}


def get_existing_ids() -> set:
    resp = api("GET", "/v0/management/codex-api-key")
    ids = set()
    for e in resp.get("codex-api-key", []):
        jwt = decode_jwt_payload(e.get("api-key", ""))
        uid = jwt.get("https://api.openai.com/auth", {}).get("user_id", "")
        if uid: ids.add(uid)
    return ids


def ensure_service():
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                         f"{API_BASE}/"], capture_output=True, text=True)
    if r.stdout.strip() not in ("200","401","404"):
        print("启动 CPA 服务...")
        subprocess.Popen(["nohup", CPA_BINARY,
                          ">/dev/null", "2>&1"])
        for _ in range(10):
            time.sleep(1)
            r2 = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                                  f"{API_BASE}/"], capture_output=True, text=True)
            if r2.stdout.strip() in ("200","401","404"):
                print("  已启动")
                return
        print("  ⚠️ 启动失败"); sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    files = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            files.extend(sorted(p.glob("*.json")))
        elif p.is_file():
            files.append(p)

    if not files:
        print("未找到 JSON 文件"); sys.exit(1)

    print(f"扫描 {len(files)} 个文件...\n")

    accounts = []
    for f in files:
        a = parse_codex_file(str(f))
        if a:
            accounts.append(a)
            print(f"  ✓ {a['email']} | {a['plan']} | {a['expired']}")
        else:
            print(f"  ✗ {f.name} (非codex)")

    if not accounts:
        print("\n无有效 Codex 账号"); return

    # 去重
    uniq = {}
    for a in accounts:
        if a["user_id"] not in uniq:
            uniq[a["user_id"]] = a

    print(f"\n解析: {len(accounts)} | 去重: {len(uniq)}")

    ensure_service()
    existing = get_existing_ids()
    new = {uid: a for uid, a in uniq.items() if uid not in existing}
    print(f"已存在: {len(uniq)-len(new)} | 新增: {len(new)}")

    if not new:
        print("无需更新"); return

    # 合并
    all_entries = api("GET", "/v0/management/codex-api-key").get("codex-api-key", [])
    for uid, a in new.items():
        all_entries.append({
            "api-key": a["access_token"],
            "prefix": "",
            "disable-cooling": False,
            "base-url": "https://api.openai.com/v1",
        })

    resp = api("PUT", "/v0/management/codex-api-key", all_entries)
    if resp.get("status") == "ok":
        print(f"\n✅ 导入成功! 当前共 {len(all_entries)} 个 Codex 账号")
    else:
        print(f"\n❌ 失败: {resp}")


if __name__ == "__main__":
    main()
