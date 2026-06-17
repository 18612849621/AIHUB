# AIHUB - CPA Agent Management

## Import Accounts Skill

When user provides a `.zip` or `.json` file with Codex OAuth credentials:

```bash
export PATH="$HOME/bin:$PATH"
cpa-import <file_or_directory>
```

Supports:
- `.zip` files (auto-extract)
- `.json` files
- Directories of JSON files

CPA auto-detects via file watcher — no restart needed.

## Check Health

```bash
cpa-health              # One-shot check
cpa-health --watch 10   # Live dashboard
cpa-health --clean      # Remove expired/banned accounts
```

## Environment

| Var | Purpose | Default |
|-----|---------|---------|
| `CPA_MANAGEMENT_KEY` | Management API key | Auto-detected from `~/.cli-proxy-api/.mgmt_key` |

## Paths

- CPA binary: `/root/cliproxyapi/cli-proxy-api`
- Config: `/root/cliproxyapi/config.yaml`
- Auth dir: `/root/.cli-proxy-api/`
- Management panel: `http://<ip>:8317/management.html`
