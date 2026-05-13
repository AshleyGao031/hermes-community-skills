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

### 一键安装（推荐）

```bash
# 安装全部 skills
curl -sSL https://raw.githubusercontent.com/AshleyGao031/hermes-community-skills/main/install.sh | bash

# 只安装某个分类
curl -sSL ... | bash -s media

# 只安装某个 skill
curl -sSL ... | bash -s media/video-to-article
```

### 手动安装

```bash
git clone https://github.com/AshleyGao031/hermes-community-skills.git /tmp/hermes-skills
bash /tmp/hermes-skills/install.sh
```

### 更新已安装的 Skills

```bash
bash ~/.hermes/community-skills-repo/install.sh pull
```

## ⚠️ 安全审查（必读）

**推送 Skill 前必须检查以下内容，确保不泄露敏感信息：**

1. **API Key / Token / Secret** — 搜索所有文件，确保没有硬编码的密钥
   ```bash
   # 推送前自查命令
   grep -rn "api_key\|token\|secret\|password\|bearer" your-skill/
   ```
2. **环境变量引用可以保留** — `process.env.API_KEY`、`os.environ.get("KEY")` 这类写法没问题，只要不是实际值
3. **个人路径** — 检查是否包含你的真实用户名、IP、内部域名等
4. **内部服务地址** — 公司/团队的内部 API 地址不应包含在内

> 💡 原则：Skill 应该拿过来就能用，敏感信息通过环境变量注入，而不是写在文件里。

## 🤝 贡献你的 Skill

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
3. 确保目录中有 `SKILL.md`
4. **⚠️ 按上方安全审查清单检查所有文件**
5. 在 README 的「已收录 Skills」中添加描述
6. 提交 **Pull Request**

### Skill 命名规范

- 小写英文 + 短横线：`my-cool-skill`
- 每个 skill 自包含，不依赖其他 skill 的内部文件

### 推送本地 Skills

如果你已经在本地写好了 skill，可以用安装脚本直接推送：

```bash
bash ~/.hermes/community-skills-repo/install.sh push "添加了 xxx skill"
```

推送前同样要完成安全审查。

## 📋 环境变量

部分 skills 需要在 `~/.hermes/.env` 中配置：

| 变量 | 用途 | 所需 Skill |
|------|------|-----------|
| `GETNOTE_API_KEY` | Get笔记 API 密钥 | video-to-article |
| `GETNOTE_CLIENT_ID` | Get笔记客户端 ID | video-to-article |

## 💡 常见问题

**Q: 安装后会覆盖我已有的同名 skill 吗？**
A: 会覆盖同名目录。建议先备份或用不同分类。

**Q: Skill 和 Hermes 内置 skill 重名怎么办？**
A: 建议避免和内置 skill 重名，用不同的名字。

**Q: 我不熟悉 Git，怎么贡献？**
A: 把你的 skill 文件（一个目录，含 SKILL.md）发给仓库维护者，帮忙提交即可。

## License

MIT
