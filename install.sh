#!/usr/bin/env bash
# Hermes Community Skills 安装脚本
# 用法:
#   bash install.sh              # 安装全部 skills
#   bash install.sh media        # 只安装 media 分类
#   bash install.sh media/video-to-article  # 只安装某个 skill
#   bash install.sh pull         # 拉取最新更新（已安装过的）
#   bash install.sh push "msg"   # 推送本地 skills 到仓库

set -e

SKILLS_DIR="${HOME}/.hermes/skills"
REPO_URL="https://github.com/AshleyGao031/hermes-community-skills.git"
REPO_DIR="${HOME}/.hermes/community-skills-repo"

setup_repo() {
    if [ ! -d "$REPO_DIR" ]; then
        echo "📥 克隆仓库..."
        git clone --depth 1 "$REPO_URL" "$REPO_DIR"
    fi
}

install_from_repo() {
    setup_repo

    echo "📥 拉取最新..."
    cd "$REPO_DIR"
    git pull origin main 2>/dev/null || true

    TARGET="${1:-all}"

    install_skill() {
        local src="$1"
        local skill_name=$(basename "$src")
        local category=$(basename "$(dirname "$src")")
        local dest="${SKILLS_DIR}/${category}/${skill_name}"
        mkdir -p "$(dirname "$dest")"
        cp -r "$src" "$dest"
        echo "  ✅ ${category}/${skill_name}"
    }

    if [ "$TARGET" = "all" ]; then
        echo "🦞 安装全部 Community Skills..."
        for category_dir in "$REPO_DIR"/*/; do
            [ "$(basename "$category_dir")" = ".git" ] && continue
            for skill_dir in "$category_dir"*/; do
                [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ] && install_skill "$skill_dir"
            done
        done
    elif [ -d "$REPO_DIR/$TARGET" ]; then
        target_path="$REPO_DIR/$TARGET"
        if [ -f "$target_path/SKILL.md" ]; then
            install_skill "$target_path"
        else
            for skill_dir in "$target_path"*/; do
                [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ] && install_skill "$skill_dir"
            done
        done
    else
        echo "❌ 找不到: $TARGET"
        exit 1
    fi
    echo ""
    echo "🎉 安装完成！"
}

push_to_repo() {
    if [ ! -d "$REPO_DIR" ]; then
        echo "❌ 仓库未克隆，请先运行: bash install.sh"
        exit 1
    fi

    local msg="${1:-update skills}"
    echo "📥 拉取最新..."
    cd "$REPO_DIR"
    git pull origin main 2>/dev/null || true

    echo "📦 同步本地 skills 到仓库..."
    for category_dir in "$REPO_DIR"/*/; do
        [ "$(basename "$category_dir")" = ".git" ] && continue
        category=$(basename "$category_dir")
        for skill_dir in "$category_dir"*/; do
            [ ! -d "$skill_dir" ] && continue
            skill_name=$(basename "$skill_dir")
            local_skill="${SKILLS_DIR}/${category}/${skill_name}"
            if [ -d "$local_skill" ]; then
                rm -rf "$skill_dir"
                cp -r "$local_skill" "$skill_dir"
                echo "  📤 ${category}/${skill_name}"
            fi
        done
    done

    cd "$REPO_DIR"
    git add -A
    if git diff --cached --quiet; then
        echo "✅ 没有变更，无需推送"
    else
        git commit -m "$msg"
        git push origin main
        echo "🎉 推送成功！"
    fi
}

case "${1:-install}" in
    pull|update) install_from_repo "${2:-all}" ;;
    push)        push_to_repo "${2:-update skills}" ;;
    *)           install_from_repo "$1" ;;
esac
