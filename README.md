# 🦞 Hermes Community Skills

Hermes Agent 社区共享 Skills 仓库。收集、整理和共享高质量的 Hermes skills。

## 📦 包含的 Skills

### media/video-to-article
将视频链接（YouTube、小宇宙播客等）转换为深度文章。

- 自动获取字幕（YouTube transcript API / Get笔记 / yt-dlp 多层 fallback）
- 小宇宙播客 show notes 提取
- 生成结构化深度长文（章节 + 时间戳）
- 支持输出：Discord 拆条 / Markdown / HTML 阅读页 / 表格图片

### media/youtube-content
YouTube 字幕提取与格式转换工具。

- `fetch_transcript.py` 脚本：支持多种 URL 格式、语言选择、时间戳
- 输出格式：章节 / 摘要 / 推文串 / 博客 / 金句
- 完善的 fallback 链处理 IP 封锁问题

## 🚀 安装

### 方式一：一键安装脚本

```bash
# 安装全部 skills
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash

# 或只安装指定分类
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash -s media
```

### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/AshleyGao031/hermes-community-skills.git /tmp/hermes-skills

# 复制到 Hermes skills 目录
cp -r /tmp/hermes-skills/media ~/.hermes/skills/

# 安装依赖
pip install youtube-transcript-api
```

### 方式三：Git Submodule（推荐开发者）

```bash
cd ~/.hermes/skills
git submodule add https://github.com/AshleyGao031/hermes-community-skills.git community
# 然后在需要的地方软链接
ln -s community/media media-community
```

## 🤝 贡献

欢迎提交 PR 添加新 skills 或改进现有 ones！

### Skill 目录结构

```
category/
└── skill-name/
    ├── SKILL.md           # 必需：Skill 定义文件
    ├── references/        # 可选：参考文档
    ├── templates/         # 可选：模板文件
    ├── scripts/           # 可选：脚本工具
    └── assets/            # 可选：静态资源
```

### 贡献步骤

1. Fork 本仓库
2. 按目录结构添加你的 skill
3. 在 README 中添加描述
4. 提交 PR

## 📋 环境变量

部分 skills 需要配置环境变量（在 `~/.hermes/.env` 中添加）：

| 变量 | 用途 | 所需 Skill |
|------|------|-----------|
| `GETNOTE_API_KEY` | Get笔记 API 密钥 | video-to-article |
| `GETNOTE_CLIENT_ID` | Get笔记客户端 ID | video-to-article |

## License

MIT
