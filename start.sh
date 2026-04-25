#!/bin/bash
# FurniQuote AI · 启动脚本
# 从 macOS Keychain 加载密钥 → 注入环境变量 → 启动 master.py
#
# 一次性配置 Keychain（示例）:
#   security add-generic-password -a "leslie" -s "DASHSCOPE_API_KEY" -w "<你的密钥>"
#   security add-generic-password -a "leslie" -s "HUNYUAN3D_API_KEY" -w "<你的密钥>"
#   ...

set -e

KEYCHAIN_ACCOUNT="leslie"
SECRETS=(
    "DASHSCOPE_API_KEY"
    "ANTHROPIC_API_KEY"
    "DEEPSEEK_API_KEY"
    "HUNYUAN3D_API_KEY"
    "SEEDREAM_API_KEY"
    "DINGTALK_APP_KEY"
    "DINGTALK_APP_SECRET"
)

echo "正在从 Keychain 加载密钥..."

MISSING=()
for KEY in "${SECRETS[@]}"; do
    VALUE=$(security find-generic-password -a "$KEYCHAIN_ACCOUNT" -s "$KEY" -w 2>/dev/null || echo "")
    if [ -z "$VALUE" ]; then
        MISSING+=("$KEY")
    else
        export "$KEY=$VALUE"
        # 仅显示前4位，安全脱敏
        MASKED="${VALUE:0:4}...${VALUE: -4}"
        echo "  ✓ $KEY = $MASKED"
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  以下密钥未在 Keychain 中找到（开发环境可继续，生产环境必须配置）:"
    for KEY in "${MISSING[@]}"; do
        echo "  - $KEY"
        echo "    配置命令: security add-generic-password -a $KEYCHAIN_ACCOUNT -s $KEY -w <密钥值>"
    done
    echo ""
fi

# 加载非敏感配置
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo ""
echo "启动 FurniQuote AI 总控..."
exec python master.py
