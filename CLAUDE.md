# AIHUB - CPA Agent Management

## Import Accounts

When user provides a `.zip` or `.json` file with Codex OAuth credentials:

```bash
export PATH="$HOME/bin:$PATH"
cpa-import <file> --cleanup     # Import + auto-delete source files
```

After import, always clean up source files (they're no longer needed).

## Check Health & Clean Dead Accounts

### 核心原则

**两步检测法，只测失败号，不浪费正常账号额度。**

### HTTP 状态码含义 (直连 OpenAI `/v1/models`)

| 状态码 | 含义 | 操作 |
|--------|------|------|
| **401** | TOKEN 失效/被撤销 → 死号 | **清理** |
| **403** | TOKEN 有效但无 models 权限 / 额度用光 | **保留** |
| 200 | TOKEN 完全有效 | 保留 |
| 429 | 限流 | 保留 |

### 用法

```bash
cpa-health                    # 快速检查 (仅 CPA 管理 API，不消耗额度)
cpa-health --test             # 两步检测: CPA API 找失败号 → 只对失败号直连测试
cpa-health --test --clean     # 检测并清理 401 死号 (需确认)
cpa-health --test --clean -f  # 不确认直接删 401
cpa-health --watch [N]        # 实时监测 (默认10秒)
```

### 两步检测流程

1. 先从 CPA 管理 API (`/v0/management/auth-files`) 获取近期全失败的账号 (success=0, failed>0)
2. 只对失败账号直连 OpenAI API 测试真实 HTTP 状态码
3. **401 才删，403 不删**（403 = 额度用光，token 本身有效）

### 关键规则

- **不能全量直连测试**: 会消耗正常账号的请求额度 (free 账号每天 ~100 次)
- **403 不要删**: OpenAI OAuth 免费 token 没有 `api.model.read` 权限，返回 403 是正常现象
- **401 必然删**: `"Your authentication token has been invalidated"` 不可恢复
- CPA 管理 API 的 `failed` 计数器包含所有失败类型 (401/429/403)，不能仅凭 `failed` 计数删号

## Paths

- CPA binary: `/root/cliproxyapi/cli-proxy-api`
- Config: `/root/cliproxyapi/config.yaml`
- Auth dir: `/root/.cli-proxy-api/`
- Management panel: `http://<ip>:8317/management.html`
- Management API key: env `CPA_MANAGEMENT_KEY` or `/root/.cli-proxy-api/.mgmt_key`
- Scripts: `/root/cliproxyapi/AIHUB/cpa/`
