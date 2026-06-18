# AIHUB - CPA Agent Management

## Import Accounts

When user provides a `.zip` or `.json` file with Codex OAuth credentials:

```bash
export PATH="$HOME/bin:$PATH"
cpa-import <file> --cleanup     # Import + auto-delete source files
```

After import, always clean up source files (they're no longer needed).

## Check Health

```bash
cpa-health              # One-shot check
cpa-health --watch 10   # Live dashboard
cpa-health --clean      # Remove expired/banned accounts
```

## Paths

- CPA binary: `/root/cliproxyapi/cli-proxy-api`
- Config: `/root/cliproxyapi/config.yaml`
- Auth dir: `/root/.cli-proxy-api/`
- Management panel: `http://<ip>:8317/management.html`
