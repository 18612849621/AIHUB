#!/bin/bash
# AIHUB 安装脚本 - 将 cpa 工具安装到系统
set -e

INSTALL_DIR="${HOME}/bin"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " AIHUB 安装"
echo "========================================"
echo ""
echo "安装位置: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"

# 安装 cpa-status
cp "$REPO_DIR/cpa/cpa-status" "$INSTALL_DIR/cpa-status"
chmod +x "$INSTALL_DIR/cpa-status"
echo "  ✅ cpa-status"

# 安装 import_codex.py
cp "$REPO_DIR/cpa/import_codex.py" "$INSTALL_DIR/cpa-import"
chmod +x "$INSTALL_DIR/cpa-import"
echo "  ✅ cpa-import"

# 安装 cpa-codex-config
cp "$REPO_DIR/cpa/cpa-codex-config" "$INSTALL_DIR/cpa-codex-config"
chmod +x "$INSTALL_DIR/cpa-codex-config"
echo "  ✅ cpa-codex-config"

# 安装 cpa-health
cp "$REPO_DIR/cpa/cpa-health" "$INSTALL_DIR/cpa-health"

# 安装 cpa-claude-config
cp "$REPO_DIR/cpa/cpa-claude-config" "$INSTALL_DIR/cpa-claude-config"
chmod +x "$INSTALL_DIR/cpa-claude-config"
echo "  ✅ cpa-claude-config"
chmod +x "$INSTALL_DIR/cpa-health"
echo "  ✅ cpa-health"


# 确保 ~/bin 在 PATH 中
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
    if ! grep -q "PATH.*$INSTALL_DIR" ~/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        echo "  ✅ PATH 已更新 (~/.bashrc)"
    fi
fi

echo ""
echo "========================================"
echo " 安装完成!"
echo "========================================"
echo ""
echo "使用方法:"
echo "  cpa-status    查看 CPA 代理状态"
echo "  cpa-import <dir>  批量导入 Codex key"
echo ""
echo "新终端直接可用, 当前终端请先执行:"
echo "  export PATH=\"\$HOME/bin:\$PATH\""
echo ""
echo "卸载: bash $REPO_DIR/uninstall.sh"
