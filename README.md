# sub2study

将 YouTube 视频字幕整理成便于精读的双语学习 PDF。

平时看 YouTube 外语视频学习时，直接下载的字幕往往很难直接用来阅读：
- **断句稀碎**：自动生成的字幕（ASR）通常按时间切片，两三个单词一行，没有标点；
- **滚屏重复**：VTT 字幕里有大量上下滚动的重复行；
- **机翻生硬**：把碎短句直接扔给翻译软件，译文经常前言不搭后语；
- **反爬拦截**：YouTube 经常弹出人机验证（`Sign in to confirm you're not a bot`）。

`sub2study` 就是为了解决这些繁琐问题写的一个小工具。它会自动下载原声字幕、合并去重、规范标点，并配合 AI 完成语境翻译与生词整理，最终直接排版生成一份适合在平板或打印阅读的 A4 双语精读 PDF。

---

## 最终效果

执行后会生成两份文件：
1. **精读讲义 PDF**：俄汉（或外汉）上下对照排版，保留起始时间戳，整词换行（不会把长单词从中间截断），文末附带视频核心词汇表（含单词原型、重音标注、词性与真实例句）。
2. **Markdown 笔记**：方便直接导入 Obsidian 或 Notion 搜索与归档。

---

## 核心特性

- **自动解决 Cookie 验证**：自动定位并解密本机 Chrome / Edge 的主账号 Cookie，绕过 YouTube 频繁弹出的 Bot 限制，免去手动导出 `cookies.txt` 的麻烦。
- **字幕文本去重与断句**：过滤 YouTube ASR 的重复滚动词与时间标签，依据句末标点将碎片词条合并成完整长句，并按语义聚合成自然段落。
- **支持任意语言**：默认自动识别视频的原声语言（俄语、英语、日语、法语、德语等），也可手动指定语种代码。
- **学习导向排版**：采用自然左对齐与整词换行，绝无连字符把俄语长词硬生生切成两半的情况。

---

## 安装

### 方式一：一键安装（推荐）

```bash
git clone https://github.com/your-username/sub2study.git
cd sub2study
chmod +x install.sh
./install.sh
```

脚本会自动安装命令行工具，并把 Skill 规则注册到你的本地 AI 工具（如 Antigravity）中。

### 方式二：手动安装

需要 Python 3.8+ 及 Google Chrome（用于渲染 PDF）：

```bash
pip install -r requirements.txt
pip install -e .
```

---

## 使用方法

### 1. 配合 AI Agent（如 Google Antigravity）使用

如果你在使用支持 Agent Skill 的工具，克隆安装后，直接发视频链接即可：

> “用 sub2study 帮我把这个视频做成学习 PDF：https://www.youtube.com/watch?v=0-j8zPoJFJc”

Agent 会自动抓取、校对、翻译，并在你的桌面生成排版好的 PDF 和 Markdown。

---

### 2. 命令行直接使用

#### 第一步：抓取并清洗字幕为段落
```bash
sub2study extract "https://www.youtube.com/watch?v=0-j8zPoJFJc" -o ./output
```
会在 `./output` 目录下生成清洗好、带时间戳的 `cleaned_paragraphs.json`。

#### 第二步：翻译与导出 PDF
将翻译好的内容整理为 JSON 后，一行命令渲染出 PDF 和 Markdown：

```bash
sub2study render ./output/bilingual_result.json \
  -o ./output \
  --title "视频学习讲义标题" \
  --video-url "https://www.youtube.com/watch?v=0-j8zPoJFJc" \
  --speaker "主讲人姓名" \
  --source-lang ru
```

---

## 目录结构

```
sub2study/
├── sub2study/                 # 核心代码
│   ├── cookie_resolver.py     # 浏览器 Cookie 安全读取与反爬处理
│   ├── extractor.py           # 字幕抓取、去重与段落重组
│   ├── renderer.py            # PDF 与 Markdown 排版生成器
│   └── cli.py                 # 命令行入口
├── skill/                     # AI Agent Skill 配置文件
│   └── SKILL.md
├── install.sh                 # 安装脚本
├── setup.py                   # 安装配置
└── README.md
```

---

## 开源协议

本项目采用 [MIT License](LICENSE)。
