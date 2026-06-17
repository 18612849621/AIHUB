# AIHUB

CPA (CLIProxyAPI) 代理管理工具集. 提供命令行工具用于查看 CPA 状态和批量导入 Codex OAuth 凭证.

## 安装

```bash
bash install.sh
```

## 使用

```bash
cpa-status              # 查看 CPA 状态 (账号/模型/配置)
cpa-import <dir>        # 批量导入 Codex JSON key 文件
```

### cpa-import 用法

```bash
# 设置管理密钥 (必需)
export CPA_MANAGEMENT_KEY="你的管理密钥"

# 导入目录中所有 JSON 文件
cpa-import /path/to/keys/

# 或导入指定文件
cpa-import file1.json file2.json
```

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `CPA_PORT` | 代理端口 | `8317` |
| `CPA_URL` | 代理地址 | 自动检测 |
| `CPA_CONFIG` | config.yaml 路径 | 自动查找 |
| `CPA_MANAGEMENT_KEY` | CPA 管理密钥 (cpa-import 必需) | 无 |

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
