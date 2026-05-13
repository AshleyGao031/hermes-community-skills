# 🦞 Hermes Community Skills

Hermes Agent 社区共享 Skills 仓库。收集、整理和共享高质量的 Hermes Skills，让每只龙虾都能用上最好的工具。

## 📦 已收录 Skills

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

---

## 🚀 安装

### 方式一：一键安装（推荐）

```bash
# 安装全部 skills
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash

# 只安装某个分类
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash -s media

# 只安装某个 skill
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash -s media/video-to-article
```

### 方式二：手动安装

```bash
git clone https://github.com/AshleyGao031/hermes-community-skills.git /tmp/hermes-skills
cp -r /tmp/hermes-skills/media ~/.hermes/skills/
pip install youtube-transcript-api
```

### 方式三：Git Submodule（适合开发者）

```bash
cd ~/.hermes/skills
git submodule add https://github.com/AshleyGao031/hermes-community-skills.git community
```

## 🔄 更新 Skills

已安装的 skills 如果有更新版本，可以重新运行安装脚本覆盖：

```bash
# 先删除旧版再重装
rm -rf ~/.hermes/skills/media/video-to-article ~/.hermes/skills/media/youtube-content
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash
```

或者用 submodule 方式（自动拉取）：

```bash
cd ~/.hermes/skills/community
git pull origin main
```

## 🤝 贡献你的 Skill

欢迎把你自己写的好用 skill 共享出来！流程很简单：

### 目录结构

```
category/           # 分类：media / research / productivity / ...
└── skill-name/
    ├── SKILL.md    # 必需：Skill 定义（frontmatter + 说明）
    ├── references/ # 可选：参考文档
    ├── templates/  # 可选：模板文件
    ├── scripts/    # 可选：脚本工具
    └── assets/     # 可选：静态资源
```

### 贡献步骤

1. **Fork** 本仓库
2. 在对应分类下创建你的 skill 目录（或新建分类）
3. 确保目录中有 `SKILL.md`（必须有）
4. 在 README 的「已收录 Skills」中添加描述
5. 提交 **Pull Request**

### Skill 命名规范

- 用小写英文 + 短横线：`my-cool-skill`
- 目录名即 skill 名，保持简短有意义
- 每个 skill 自包含，不依赖其他 skill 的内部文件

## 📋 环境变量

部分 skills 需要在 `~/.hermes/.env` 中配置：

| 变量 | 用途 | 所需 Skill |
|------|------|-----------|
| `GETNOTE_API_KEY` | Get笔记 API 密钥 | video-to-article |
| `GETNOTE_CLIENT_ID` | Get笔记客户端 ID | video-to-article |

## 💡 常见问题

**Q: 安装后会覆盖我已有的同名 skill 吗？**
A: 不会。安装脚本检测到同名目录会跳过，需要先删除旧版才能安装新版。

**Q: 我不熟悉 Git，怎么贡献？**
A: 最简单的方式：把你的 skill 文件（一个目录，含 SKILL.md）发给仓库维护者，帮忙提交即可。

**Q: Skill 和 Hermes 内置 skill 重名怎么办？**
A: 社区 skill 会安装到 `~/.hermes/skills/` 下，和内置 skill 路径相同，同名时会共存。Hermes 按 skill 名称加载，建议避免重名。

## License

MIT
