#!/usr/bin/env bash
# sub2study One-Click Installer
set -e

echo "=========================================="
echo "   Installing sub2study Tool & Skill      "
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Install Python package
echo "[1/4] Installing sub2study Python CLI..."
python3 -m pip install -e "$SCRIPT_DIR"

# 2. Register Antigravity Skill
echo "[2/4] Registering Antigravity Skill..."
SKILL_TARGET="$HOME/.gemini/config/skills/sub2study"
mkdir -p "$SKILL_TARGET/scripts"

cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_TARGET/SKILL.md"
cp "$SCRIPT_DIR/sub2study/extractor.py" "$SKILL_TARGET/scripts/extract_and_clean_subtitles.py"
cp "$SCRIPT_DIR/sub2study/renderer.py" "$SKILL_TARGET/scripts/render_bilingual_doc.py"
cp "$SCRIPT_DIR/sub2study/cookie_resolver.py" "$SKILL_TARGET/scripts/cookie_resolver.py"

chmod +x "$SKILL_TARGET/scripts/"*.py

# 3. Cache YouTube cookies if Chrome exists
echo "[3/4] Resolving browser session cookies..."
python3 "$SCRIPT_DIR/sub2study/cli.py" cookies || true

# 4. Check dependencies
echo "[4/4] Verifying dependencies..."
if command -v yt-dlp &> /dev/null; then
    echo "  ✓ yt-dlp is installed"
else
    echo "  ⚠ yt-dlp not found in PATH, installing..."
    python3 -m pip install yt-dlp
fi

echo ""
echo "=========================================="
echo "  ✓ sub2study installed successfully!     "
echo "=========================================="
echo ""
echo "Usage in Terminal:"
echo "  sub2study extract 'https://www.youtube.com/watch?v=...' -o ./study"
echo ""
echo "Usage in Antigravity:"
echo "  Ask the agent: '用 sub2study 帮我把这个视频做成学习讲义：<链接>'"
echo ""
