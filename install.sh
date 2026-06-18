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

cp "$REPO_DIR/cpa/cpa-status" "$INSTALL_DIR/cpa-status"
chmod +x "$INSTALL_DIR/cpa-status"
echo "  ✅ cpa-status"

cp "$REPO_DIR/cpa/import_codex.py" "$INSTALL_DIR/cpa-import"
chmod +x "$INSTALL_DIR/cpa-import"
echo "  ✅ cpa-import"

cp "$REPO_DIR/cpa/cpa-config" "$INSTALL_DIR/cpa-config"
chmod +x "$INSTALL_DIR/cpa-config"
echo "  ✅ cpa-config"

cp "$REPO_DIR/cpa/cpa-health" "$INSTALL_DIR/cpa-health"
chmod +x "$INSTALL_DIR/cpa-health"
echo "  ✅ cpa-health"

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
echo "  cpa-status           查看 CPA 代理状态"
echo "  cpa-import <dir|zip> 批量导入 Codex key"
echo "  cpa-config            生成 Codex + Claude Code 配置"
echo "  cpa-health            账号健康检查"
echo ""
echo "新终端直接可用, 当前终端请先执行:"
echo "  export PATH=\"\$HOME/bin:\$PATH\""
echo ""
echo "卸载: bash $REPO_DIR/uninstall.sh"
