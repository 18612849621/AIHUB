#!/usr/bin/env python3
"""
批量导入 Codex OAuth JSON / ZIP 文件到 CPA auth-dir.

CPA 通过监控 auth-dir 目录自动发现 OAuth 凭证，无需调用管理 API。
放入目录后 CPA 即刻生效。

用法:
  cpa-import <json目录|zip文件> [--cleanup]
  cpa-import /path/to/keys/
  cpa-import keys.zip --cleanup     # 导入后自动删除源文件
  cpa-import file1.json file2.json keys.zip

环境变量:
  CPA_AUTH_DIR  - CPA auth 目录, 默认 ~/.cli-proxy-api
  CPA_CONFIG    - CPA config.yaml 路径 (从中读取 auth-dir)
"""

import json, os, sys, base64, zipfile, tempfile, shutil
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
    if "CPA_AUTH_DIR" in os.environ:
        return Path(os.environ["CPA_AUTH_DIR"]).expanduser()

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

    return Path("~/.cli-proxy-api").expanduser()


def parse_codex_data(data: dict) -> tuple[dict, dict] | None:
    """解析 Codex JSON 数据，返回 (原始数据, 提取的账号信息)"""
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


def parse_codex_file(filepath: str) -> tuple[dict, dict] | None:
    """解析 Codex JSON 文件"""
    with open(filepath) as f:
        return parse_codex_data(json.load(f))


def extract_zip(zip_path: str) -> list[Path]:
    """解压 zip 并返回其中所有 JSON 文件的临时路径列表"""
    tmpdir = Path(tempfile.mkdtemp(prefix="cpa_import_"))
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # 只提取 JSON 文件
        json_names = [n for n in zf.namelist() if n.lower().endswith('.json')]
        if not json_names:
            print(f"  ⚠ {Path(zip_path).name} 中没有 JSON 文件")
            shutil.rmtree(tmpdir, ignore_errors=True)
            return []
        zf.extractall(tmpdir, members=json_names)
    return sorted(tmpdir.glob("**/*.json"))


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


def collect_files(args: list[str]) -> tuple[list[Path], list[Path]]:
    """
    从命令行参数收集文件，支持:
    - 目录: 收集其中 *.json
    - .json 文件: 直接加入
    - .zip 文件: 解压后收集其中 *.json
    返回 (普通文件列表, 临时目录列表(用于清理))
    """
    files = []
    tmpdirs = []

    for arg in args:
        p = Path(arg)
        if p.is_dir():
            files.extend(sorted(p.glob("*.json")))
        elif p.is_file() and p.suffix.lower() == '.zip':
            extracted = extract_zip(str(p))
            if extracted:
                files.extend(extracted)
                # 找到临时目录根
                for ep in extracted:
                    tmpdirs.append(ep.parent)
        elif p.is_file():
            files.append(p)
        else:
            print(f"  ⚠ {arg} 不存在，跳过")

    return files, tmpdirs


def main():
    # 解析 --cleanup 参数
    args = sys.argv[1:]
    cleanup = False
    if "--cleanup" in args:
        cleanup = True
        args = [a for a in args if a != "--cleanup"]

    if len(args) < 1:
        print(__doc__)
        sys.exit(1)

    files, tmpdirs = collect_files(args)

    if not files:
        print("未找到 JSON 文件")
        sys.exit(1)

    auth_dir = find_auth_dir()
    auth_dir.mkdir(parents=True, exist_ok=True)

    print(f"扫描 {len(files)} 个文件...")
    print(f"目标目录: {auth_dir}")
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.suffix.lower() == '.zip' and p.is_file():
            print(f"  解压: {p.name} → {sum(1 for f in files if str(f).startswith('/tmp/cpa_import_'))} 个 JSON")
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
            print(f"  ✗ {Path(f).name} (非 codex 类型，跳过)")

    if not accounts:
        print("\n无有效 Codex 账号")
        _cleanup(tmpdirs)
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
        # 从原始 JSON 文件名生成目标文件名 (用 email 更可读)
        email = info['email'].split('@')[0].replace('+', '_')
        dest_name = f"{email}.json"
        dest_path = auth_dir / dest_name

        if uid in existing:
            if existing[uid] == dest_name:
                print(f"  ⏭ {info['email']} (已存在)")
                skipped += 1
                continue
            else:
                old_path = auth_dir / existing[uid]
                old_path.unlink(missing_ok=True)
                print(f"  🔄 {info['email']} (覆盖旧文件 {existing[uid]})")
                updated += 1
        else:
            print(f"  → {info['email']}")
            imported += 1

        # 写入 JSON 文件到 auth-dir
        if "imported_at" not in data:
            from datetime import datetime, timezone
            data["imported_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(dest_path, 'w') as f:
            json.dump(data, f, indent=2)

    print()
    print(f"✅ 导入: {imported} | 更新: {updated} | 跳过: {skipped}")
    print(f"   CPA 已自动检测并加载，无需重启")

    # 清理临时文件
    _cleanup(tmpdirs)

    # --cleanup: 删除源文件
    if cleanup:
        deleted = []
        for a in args:
            p = Path(a)
            if p.is_file():
                p.unlink()
                deleted.append(p.name)
            elif p.is_dir() and p.name == "new_keys":
                # 目录也删 (new_keys 这类临时目录)
                shutil.rmtree(p, ignore_errors=True)
                deleted.append(f"{p.name}/")
        if deleted:
            print(f"   🗑 已清理: {', '.join(deleted)}")


def _cleanup(tmpdirs: list[Path]):
    for d in tmpdirs:
        try:
            shutil.rmtree(d, ignore_errors=True)
        except:
            pass


if __name__ == "__main__":
    main()
