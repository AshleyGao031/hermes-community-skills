#!/usr/bin/env bash
# Hermes Community Skills 安装脚本
# 用法:
#   bash install.sh          # 安装全部
#   bash install.sh media    # 只安装 media 分类
#   bash install.sh media/video-to-article  # 只安装某个 skill

set -e

SKILLS_DIR="${HOME}/.hermes/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 如果是从 URL 运行，先克隆到临时目录
if [ ! -d "${SCRIPT_DIR}/media" ]; then
    TMP_DIR=$(mktemp -d)
    echo "📥 克隆仓库到临时目录..."
    git clone --depth 1 https://github.com/AshleyGao031/hermes-community-skills.git "$TMP_DIR/repo"
    SCRIPT_DIR="$TMP_DIR/repo"
fi

mkdir -p "$SKILLS_DIR"

install_skill() {
    local src="$1"
    local skill_name=$(basename "$src")
    local category=$(basename "$(dirname "$src")")
    local dest="${SKILLS_DIR}/${category}/${skill_name}"

    if [ -d "$dest" ]; then
        echo "⏭️  ${category}/${skill_name} 已存在，跳过（如需更新请先删除）"
    else
        mkdir -p "$(dirname "$dest")"
        cp -r "$src" "$dest"
        echo "✅ 已安装 ${category}/${skill_name}"
    fi
}

TARGET="${1:-all}"

if [ "$TARGET" = "all" ]; then
    echo "🦞 安装全部 Hermes Community Skills..."
    for category_dir in "$SCRIPT_DIR"/*/; do
        [ "$(basename "$category_dir")" = ".git" ] && continue
        category=$(basename "$category_dir")
        for skill_dir in "$category_dir"*/; do
            [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ] && install_skill "$skill_dir"
        done
    done
elif [ -d "$SCRIPT_DIR/$TARGET" ]; then
    target_path="$SCRIPT_DIR/$TARGET"
    if [ -f "$target_path/SKILL.md" ]; then
        install_skill "$target_path"
    else
        echo "🦞 安装 $TARGET 分类下的所有 skills..."
        for skill_dir in "$target_path"/*/; do
            [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ] && install_skill "$skill_dir"
        done
    fi
else
    echo "❌ 找不到: $TARGET"
    echo "可用分类: $(ls -d "$SCRIPT_DIR"/*/ 2>/dev/null | xargs -I{} basename {})"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo "Skills 目录: $SKILLS_DIR"

# 检查依赖
echo ""
echo "📋 检查依赖..."
if python3 -c "import youtube_transcript_api" 2>/dev/null; then
    echo "  ✅ youtube-transcript-api 已安装"
else
    echo "  ⚠️  youtube-transcript-api 未安装，运行: pip install youtube-transcript-api"
fi

# 清理临时目录
if [ -n "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
fi
