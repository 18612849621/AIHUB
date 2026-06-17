#!/usr/bin/env python3
"""
批量导入 Codex OAuth JSON 文件到 CPA auth-dir.

CPA 通过监控 auth-dir 目录自动发现 OAuth 凭证，无需调用管理 API。
放入目录后 CPA 即刻生效。

用法:
  cpa-import <json目录>
  cpa-import /path/to/keys/
  cpa-import file1.json file2.json

环境变量:
  CPA_AUTH_DIR  - CPA auth 目录, 默认 ~/.cli-proxy-api
  CPA_CONFIG    - CPA config.yaml 路径 (从中读取 auth-dir)
"""

import json, os, sys, base64
from pathlib import Path


def decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except:
        return {}


def find_auth_dir():
    """自动检测 CPA auth 目录"""
    # 优先用环境变量
    if "CPA_AUTH_DIR" in os.environ:
        return Path(os.environ["CPA_AUTH_DIR"]).expanduser()

    # 尝试从 config.yaml 读取
    config_paths = [
        os.environ.get("CPA_CONFIG", ""),
        "/root/cliproxyapi/config.yaml",
        "/opt/cliproxyapi/config.yaml",
        os.path.expanduser("~/cliproxyapi/config.yaml"),
    ]
    for cp in config_paths:
        if cp and Path(cp).is_file():
            try:
                import yaml
                with open(cp) as f:
                    cfg = yaml.safe_load(f)
                ad = cfg.get("auth-dir", "")
                if ad:
                    return Path(ad).expanduser()
            except:
                pass

    # 默认
    return Path("~/.cli-proxy-api").expanduser()


def parse_codex_file(filepath: str) -> tuple[dict, dict] | None:
    """解析 Codex JSON 文件，返回 (文件数据, 提取的账号信息)"""
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
    info = {
        "email": profile.get("email") or data.get("email", "?"),
        "user_id": auth.get("user_id", "?"),
        "plan": data.get("plan_type", "free"),
        "expired": data.get("expired", "?"),
    }
    return data, info


def scan_existing(auth_dir: Path) -> dict:
    """扫描 auth-dir 中已有的 Codex 文件，返回 {user_id: filename}"""
    existing = {}
    if not auth_dir.is_dir():
        return existing
    for f in auth_dir.glob("*.json"):
        result = parse_codex_file(str(f))
        if result:
            _, info = result
            uid = info["user_id"]
            if uid and uid != "?":
                existing[uid] = f.name
    return existing


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # 收集输入文件
    files = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            files.extend(sorted(p.glob("*.json")))
        elif p.is_file():
            files.append(p)

    if not files:
        print("未找到 JSON 文件")
        sys.exit(1)

    auth_dir = find_auth_dir()
    auth_dir.mkdir(parents=True, exist_ok=True)

    print(f"扫描 {len(files)} 个文件...")
    print(f"目标目录: {auth_dir}")
    print()

    # 解析所有文件
    accounts = []
    for f in files:
        result = parse_codex_file(str(f))
        if result:
            data, info = result
            accounts.append((f, data, info))
            exp = info["expired"]
            print(f"  ✓ {info['email']}")
            print(f"    plan={info['plan']}  expired={exp}")
        else:
            print(f"  ✗ {f.name} (非 codex 类型，跳过)")

    if not accounts:
        print("\n无有效 Codex 账号")
        return

    # 去重 (按 user_id)
    seen = {}
    for f, data, info in accounts:
        uid = info["user_id"]
        if uid not in seen:
            seen[uid] = (f, data, info)

    print(f"\n解析: {len(accounts)} | 去重: {len(seen)}")

    # 检查已有文件
    existing = scan_existing(auth_dir)
    imported, skipped, updated = 0, 0, 0

    for uid, (src_path, data, info) in seen.items():
        dest_name = src_path.name
        dest_path = auth_dir / dest_name

        if uid in existing:
            if existing[uid] == dest_name:
                print(f"  ⏭ {info['email']} (已存在)")
                skipped += 1
                continue
            else:
                # user_id 相同但文件名不同 → 覆盖
                old_path = auth_dir / existing[uid]
                old_path.unlink(missing_ok=True)
                print(f"  🔄 {info['email']} (覆盖旧文件 {existing[uid]})")
                updated += 1
        else:
            print(f"  → {info['email']}")
            imported += 1

        # 直接复制 JSON 文件到 auth-dir
        with open(src_path) as f:
            original = json.load(f)
        # 添加导入时间戳
        if "imported_at" not in original:
            from datetime import datetime, timezone
            original["imported_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(dest_path, 'w') as f:
            json.dump(original, f, indent=2)

    print()
    print(f"✅ 导入: {imported} | 更新: {updated} | 跳过: {skipped}")
    print(f"   CPA 已自动检测并加载，无需重启")


if __name__ == "__main__":
    main()
