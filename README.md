# AIHUB

CPA (CLIProxyAPI) 代理管理工具集. 提供命令行工具用于查看 CPA 状态和批量导入 Codex OAuth 凭证.

## 安装

```bash
bash install.sh
```

## 使用

```bash
cpa-status              # 查看 CPA 状态 (账号/模型/配置)
cpa-import <dir|zip>    # 批量导入 Codex JSON key / zip 文件
cpa-codex-config        # 生成 Codex CLI 配置 (可直接复制粘贴)
cpa-health              # 检查账号健康状态 / 清理过期账号
```

### cpa-import 用法

```bash
# 直接导入，无需任何环境变量
cpa-import /path/to/keys/

# 或导入指定文件
cpa-import file1.json file2.json

# CPA 通过文件监控自动加载，无需重启
```

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `CPA_PORT` | 代理端口 | `8317` |
| `CPA_URL` | 代理地址 | 自动检测 |
| `CPA_CONFIG` | config.yaml 路径 | 自动查找 |
| `CPA_MODEL` | cpa-codex-config 默认模型 | `gpt-5.5` |
| `CPA_AUTH_DIR` | auth 目录 | `~/.cli-proxy-api` |

## 配置路径自动检测

工具按以下顺序查找 `config.yaml`:
1. `$CPA_CONFIG` 环境变量
2. `/root/cliproxyapi/config.yaml`
3. `/home/*/cliproxyapi/config.yaml`
4. `/opt/cliproxyapi/config.yaml`
5. `./config.yaml`

## 卸载

```bash
bash uninstall.sh
```
