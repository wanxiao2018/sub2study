# 🎓 sub2study: 将任何 YouTube 视频字幕秒变出版级双语学习讲义

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)
[![Platform: macOS | Linux | Windows](https://img.shields.io/badge/Platform-macOS%20|%20Linux%20|%20Windows-lightgrey.svg)]()
[![Antigravity: Skill Supported](https://img.shields.io/badge/Antigravity-Skill%20Ready-purple.svg)]()

> **sub2study**（*Subtitles to Study*）是一款专为外语自学者打造的自动化视频精读/精听材料制作工具与 AI Skill。它不仅能抓取全球任意语种的 YouTube 字幕（包括自动生成的 ASR 俄语/英语/日语/法语等），更针对常见语音识别痛点实现了**自动纠偏去重**、**智能断句聚合**、**AI 原文精修校对**、**地道上下文翻译**与**带重音核心生词提炼**，最终一键导出出版级 PDF、Markdown 笔记以及支持毫秒级视频联动的**单句交互式精听网页**！

---

## 🌟 核心产出成果

运行一次 `sub2study`，即可获得完整的“外语学习四件套”：

| 成果文件 | 格式 | 核心特点与使用场景 |
| :--- | :---: | :--- |
| **单句精听交互播放器** | `_Interactive_Sentence_Study.html` | **强烈推荐**。单文件零依赖，内嵌 YouTube 播放器与字幕流**毫秒级卡拉OK同步**，支持单句无限循环复读（<kbd>R</kbd>）、听写盲测遮罩模式（<kbd>T</kbd>）、TTS 发音与生词抽屉。 |
| **出版级精读讲义** | `.pdf` | 基于 Headless Chrome 矢量渲染，**自然左对齐排版**，严格保留完整单词（绝无连字符跨行截断），适配 iPad、打印机和静读学习。 |
| **双语对照学习笔记** | `.md` | 标准 GitHub 风格 Markdown，方便一键导入 Obsidian、Notion、Logseq 归档与检索。 |
| **纯净交互网页** | `.html` | 响应式自适应布局，可直接双击离线阅读。 |

---

## 🚀 为什么选择 sub2study？（四大技术杀手锏）

### 1. 彻底解决 YouTube Cookie 与 Bot 防爬拦截
* **传统痛点**：YouTube 频繁弹出 `Sign in to confirm you're not a bot`，且 `yt-dlp` 自带的 `--cookies-from-browser` 极易误读取 Chrome 扩展插件生成的 30KB 假 Cookie，导致下载反复失败。
* **sub2study 解法**：内置 **Smart Cookie Resolver**，自动定位主配置文件真实的高权重大体积数据库（>300KB），自动调用系统安全层（macOS Keychain / Windows DPAPI / Linux SecretService）解密并生成干净的 Cookie 缓存，一次配置、长期免密、100% 稳定。

### 2. ASR 俄语/多语种语音识别“智能预处理与精修”
* **传统痛点**：直接机翻 ASR 自动字幕是“垃圾进，垃圾出”（错别字、漏逗号、专有名词乱拼音译）。
* **sub2study 解法**：在翻译前加入 **AI Proofreading 审稿阶段**：
  * 专有名词纠偏（如 `айл-экзамен` $\rightarrow$ `IELTS-экзамен`, `бонку` $\rightarrow$ `учебник Бонк`）；
  * 补齐俄语复合句严谨标点与大小写；
  * 剔除口吃重复词，但保留真实地道俚语。

### 3. 带重音（Ударение）与体貌（Вид）的核心生词表
* 每篇讲义文末自动提取 20~35 个核心生词，严格按照正音辞典标注**急性重音符号**（如 `претендова́ть`、`прока́чивать`、`шлифо́вка`），明确标注动词体貌（未完成体/完成体）与视频原句地道搭配。

### 4. 严禁单词隔行截断（Whole Words Preservation）
* 排版放弃粗暴的强制两端对齐，采用出版规范的自然左对齐与整词换行（`word-break: normal; hyphens: none;`），确保每个俄语/外语长词完完整整显示在一行，绝不破坏记忆体验。

---

## 🛠️ 安装与快速上手

### 方式一：一键自动安装（推荐）

克隆仓库并运行一键安装脚本：

```bash
git clone https://github.com/your-username/sub2study.git
cd sub2study
chmod +x install.sh
./install.sh
```

脚本会自动：
1. 安装 Python CLI 工具 `sub2study`；
2. 自动将 Skill 挂载至 Antigravity 全局目录（`~/.gemini/config/skills/sub2study`）；
3. 自动完成 YouTube 浏览器会话 Cookie 探测与缓存。

---

### 方式二：手动安装

```bash
pip install -r requirements.txt
pip install -e .
```

---

## 💡 使用指南

### 1. 配合 AI Agent（如 Google Antigravity）使用（最智能）

直接在对话框中发任意 YouTube 链接：
> **“用 sub2study 帮我把这个视频做成学习讲义：https://www.youtube.com/watch?v=0-j8zPoJFJc”**

Agent 将自动调用预处理、翻译与渲染管线，几分钟内直接在你的桌面生成全套 PDF、Markdown 与交互 HTML！

### 2. 独立命令行（CLI）使用

#### ① 提取并清洗字幕为自然段落：
```bash
sub2study extract "https://www.youtube.com/watch?v=0-j8zPoJFJc" -o ./output --lang auto
```

#### ② 渲染已有双语 JSON 为 Markdown、HTML 和 PDF：
```bash
sub2study render ./bilingual_result.json \
  -o ./output \
  --title "AI时代的语言学习法" \
  --video-url "https://www.youtube.com/watch?v=0-j8zPoJFJc" \
  --speaker "Dmitry Petrov" \
  --source-lang ru
```

#### ③ 一键生成单句交互式精听精读网页：
```bash
sub2study interactive ./bilingual_result.json \
  -o ./output/Interactive_Study.html \
  --title "AI时代的语言学习法" \
  --video-url "https://www.youtube.com/watch?v=0-j8zPoJFJc"
```

---

## ⌨️ 交互播放器快捷键

在生成的 `_Interactive_Sentence_Study.html` 页面中，你可以使用以下按键极速操控：

| 快捷键 | 功能 |
| :---: | :--- |
| <kbd>Space</kbd> | 播放 / 暂停视频 |
| <kbd>R</kbd> | **单句无限复读**（反复听当前句，磨耳朵 / 影子跟读） |
| <kbd>→</kbd> / <kbd>←</kbd> | 跳至下一句 / 上一句 |
| <kbd>T</kbd> | **听写盲测模式**（开启/关闭所有中文译文模糊遮罩） |
| <kbd>🔊</kbd> | 原生 Web Speech 朗读标准发音 |

---

## 📂 项目结构

```
sub2study/
├── sub2study/                         # 核心 Python 源码
│   ├── __init__.py
│   ├── cli.py                         # 终端命令行入口
│   ├── cookie_resolver.py             # 核心反爬：智能主配置 Cookie 提取与解密
│   ├── extractor.py                   # 字幕下载、去重清洗与语义断句
│   ├── renderer.py                    # 无连字符 Markdown / HTML / PDF 渲染器
│   └── interactive_builder.py         # 交互式单句精听播放器构建器
├── skill/                             # AI Agent 技能配置
│   ├── SKILL.md                       # Antigravity 原生 Skill 规则文件
│   └── system_prompt_snippet.md       # 第三方 LLM 适配 Prompt 范例
├── install.sh                         # 一键安装脚本
├── setup.py                           # Python 包打包配置
├── requirements.txt                   # 依赖清单
├── LICENSE                            # MIT 开源协议
└── README.md                          # 项目说明文档
```

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！
- 支持更多视频平台（Bilibili、Coursera、TED 等）；
- 支持更多语言的特定形态学标注与变位解析；
- 欢迎分享基于 `sub2study` 制作的公开精读教材！

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 授权协议。
