#!/bin/bash
# AIHUB 卸载脚本
set -e

INSTALL_DIR="${HOME}/bin"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " AIHUB 卸载"
echo "========================================"

rm -f "$INSTALL_DIR/cpa-status"
rm -f "$INSTALL_DIR/cpa-import"
rm -f "$INSTALL_DIR/cpa-codex-config"
rm -f "$INSTALL_DIR/cpa-health"
echo "  ✅ 已删除 cpa-status"
echo "  ✅ 已删除 cpa-import"
echo "  ✅ 已删除 cpa-codex-config"
echo "  ✅ 已删除 cpa-health"

# 清理 PATH (移除 ~/bin 引用)
if [ -f ~/.bashrc ]; then
    sed -i '\|export PATH="$HOME/bin:$PATH"|d' ~/.bashrc 2>/dev/null
    echo "  ✅ 已清理 ~/.bashrc"
fi

echo ""
echo "卸载完成"
echo ""
echo "重新安装: bash $REPO_DIR/install.sh"
