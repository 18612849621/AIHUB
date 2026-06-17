# AIHUB

CPA 代理管理工具集。

## 安装

```bash
bash install.sh
```

## 使用

```bash
cpa-status              # 查看 CPA 状态 (账号/模型/配置)
cpa-import <dir>        # 批量导入 Codex JSON key
```

## 环境变量 (可选)

| 变量 | 说明 | 默认 |
|------|------|------|
| `CPA_PORT` | 代理端口 | `8317` |
| `CPA_URL` | 代理地址 | 自动检测 |
| `CPA_CONFIG` | config.yaml 路径 | 自动查找 |

## 卸载

```bash
bash uninstall.sh
```
