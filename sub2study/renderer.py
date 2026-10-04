#!/usr/bin/env python3
"""
sub2study - Document Renderer
Generates:
1. Standard Markdown study guide (.md)
2. Standalone styled HTML reader (.html)
3. High-definition PDF (.pdf via Headless Chrome) with natural left-aligned typography (no word splitting).
"""

import sys
import os
import re
import json
import html
import subprocess
import argparse
import shutil
import tempfile

def find_chrome_executable():
    paths = [
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def cleanup_intermediates(output_dir, input_json=None, keep_html=False):
    """Archive or clean intermediate working files (.html, .vtt, .json) in output_dir,
    guaranteeing that ONLY .md and .pdf study guide files remain."""
    cache_dir = os.path.expanduser("~/.sub2study/cache")
    os.makedirs(cache_dir, exist_ok=True)

    # 1. Clean HTML
    if not keep_html:
        for f in os.listdir(output_dir):
            if f.endswith(".html"):
                try:
                    os.remove(os.path.join(output_dir, f))
                except OSError:
                    pass

    # 2. Archive intermediate files (json, vtt, srt)
    intermediate_patterns = [
        r"^cleaned_paragraphs.*\.json$",
        r"^bilingual_result.*\.json$",
        r"^part\d+.*\.json$",
        r"^.*\.vtt$",
        r"^.*\.srt$"
    ]
    archived = []
    for f in os.listdir(output_dir):
        fp = os.path.join(output_dir, f)
        if os.path.isdir(fp):
            continue
        # Strictly preserve the final study deliverables
        if f.endswith(".pdf") or f.endswith(".md"):
            continue

        is_intermediate = any(re.match(pat, f) for pat in intermediate_patterns)
        if is_intermediate or (input_json and os.path.abspath(fp) == os.path.abspath(input_json)):
            target = os.path.join(cache_dir, f)
            try:
                shutil.move(fp, target)
                archived.append(f)
            except Exception:
                try:
                    os.remove(fp)
                    archived.append(f)
                except OSError:
                    pass

    if archived:
        print(f"[+] Cleaned up intermediate files ({', '.join(archived)}) -> archived to ~/.sub2study/cache/")

def generate_documents(bilingual_json, output_dir, title="双语精读讲义", video_url="", speaker="", summary="", source_lang="ru", keep_html=False, clean=True):
    os.makedirs(output_dir, exist_ok=True)

    with open(bilingual_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    paragraphs = data.get("paragraphs", [])
    vocabulary = data.get("vocabulary", [])

    base_slug = re.sub(r'[^\w\-\u4e00-\u9fff]', '_', title)[:40].strip('_')
    if not base_slug:
        base_slug = "Bilingual_Study_Guide"

    # 1. Markdown Output
    md_lines = []
    md_lines.append(f"# {title}")
    md_lines.append("")
    if video_url:
        md_lines.append(f"> **原视频链接**: [{video_url}]({video_url})")
    if speaker:
        md_lines.append(f"> **主讲人**: {speaker}")
    if summary:
        md_lines.append(f"> **核心概要**: {summary}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 一、 双语对照精读正文")
    md_lines.append("")

    for idx, p in enumerate(paragraphs, 1):
        ts = p.get("timestamp", "00:00:00")
        src = p.get("ru") or p.get("src") or p.get("text") or ""
        zh = p.get("zh") or p.get("translation") or ""
        md_lines.append(f"### 段落 {idx} `[{ts}]`")
        md_lines.append("")
        md_lines.append(f"**原文**：  \n{src.strip()}")
        md_lines.append("")
        md_lines.append(f"**中文**：  \n> {zh.strip()}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    if vocabulary:
        md_lines.append(f"## 二、 核心生词与地道表达解析 ({len(vocabulary)} 条)")
        md_lines.append("")
        md_lines.append("| 序号 | 单词/表达 (带重音) | 词性与语法 | 中文释义 | 视频语境搭配与例句 |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for v_idx, v in enumerate(vocabulary, 1):
            w = (v.get("accent") or v.get("word") or "").replace("|", "/")
            pos = (v.get("pos") or "").replace("|", "/")
            meaning = (v.get("meaning") or "").replace("|", "/")
            colloc = (v.get("collocation") or "").replace("|", "/")
            md_lines.append(f"| {v_idx} | **{w}** | {pos} | {meaning} | {colloc} |")

    md_path = os.path.join(output_dir, f"{base_slug}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[+] Markdown saved to: {md_path}")

    # 2. HTML & Print PDF Output
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>""" + html.escape(title) + """</title>
<style>
  @page {
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
  }
  @media print {
    .page-break { page-break-before: always; }
    .avoid-break { page-break-inside: avoid; }
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    color: #1e293b;
    line-height: 1.68;
    font-size: 13.5px;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }
  .header-card {
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    color: #ffffff;
    border-radius: 10px;
    padding: 22px;
    margin-bottom: 24px;
  }
  .header-card h1 {
    margin: 0 0 10px 0;
    font-size: 22px;
    font-weight: 700;
  }
  .meta-item {
    font-size: 13px;
    opacity: 0.92;
    margin: 4px 0;
  }
  .meta-item strong {
    color: #93c5fd;
  }
  .meta-item a {
    color: #bfdbfe;
    text-decoration: underline;
  }
  .section-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 6px;
    margin: 26px 0 16px 0;
  }
  .p-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 14px;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }
  .p-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .p-badge {
    background: #eff6ff;
    color: #1d4ed8;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
    font-weight: 600;
    font-size: 11.5px;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #bfdbfe;
  }
  .p-idx {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
  }
  .p-src {
    font-size: 14px;
    font-weight: 500;
    color: #0f172a;
    margin-bottom: 8px;
    line-height: 1.65;
    text-align: left;
    word-break: normal;
    hyphens: none;
    -webkit-hyphens: none;
  }
  .p-zh {
    font-size: 13px;
    color: #334155;
    background: #f8fafc;
    border-left: 3.5px solid #3b82f6;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    line-height: 1.6;
    text-align: left;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    font-size: 12px;
  }
  tr { page-break-inside: avoid; }
  th, td {
    border: 1px solid #cbd5e1;
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
  }
  th { background: #f1f5f9; font-weight: 600; color: #1e293b; }
  tr:nth-child(even) td { background: #f8fafc; }
  .word-accent { color: #1d4ed8; font-weight: 700; font-size: 13px; }
  .word-pos { color: #64748b; font-style: italic; font-size: 11px; }
</style>
</head>
<body>
<div class="header-card">
  <h1>""" + html.escape(title) + """</h1>
""")
    if video_url:
        html_parts.append(f'  <div class="meta-item"><strong>视频链接：</strong> <a href="{html.escape(video_url)}">{html.escape(video_url)}</a></div>\n')
    if speaker or summary:
        html_parts.append(f'  <div class="meta-item"><strong>主讲人：</strong> {html.escape(speaker)} | <strong>概要：</strong> {html.escape(summary)}</div>\n')
    html_parts.append("""</div>

<div class="section-title">一、 双语对照精读（按时间轴排版）</div>
""")

    for idx, p in enumerate(paragraphs, 1):
        ts = html.escape(p.get("timestamp", "00:00:00"))
        src = html.escape(p.get("ru") or p.get("src") or p.get("text") or "")
        zh = html.escape(p.get("zh") or p.get("translation") or "")
        html_parts.append(f"""
<div class="p-card avoid-break">
  <div class="p-header">
    <span class="p-idx">段落 {idx}</span>
    <span class="p-badge">[{ts}]</span>
  </div>
  <div class="p-src" lang="{source_lang}">{src}</div>
  <div class="p-zh" lang="zh-CN">{zh}</div>
</div>
""")

    if vocabulary:
        html_parts.append(f"""
<div class="page-break"></div>
<div class="section-title">二、 核心生词与地道表达解析（{len(vocabulary)} 条）</div>
<table>
  <thead>
    <tr>
      <th style="width: 5%;">#</th>
      <th style="width: 22%;">单词 / 表达 (带重音)</th>
      <th style="width: 15%;">词性与语法</th>
      <th style="width: 25%;">中文释义</th>
      <th style="width: 33%;">语境搭配与例句</th>
    </tr>
  </thead>
  <tbody>
""")
        for v_idx, v in enumerate(vocabulary, 1):
            w = html.escape(v.get("accent") or v.get("word") or "")
            pos = html.escape(v.get("pos") or "")
            meaning = html.escape(v.get("meaning") or "")
            colloc = html.escape(v.get("collocation") or "")
            html_parts.append(f"""
    <tr>
      <td style="text-align: center; font-weight: 600; color: #64748b;">{v_idx}</td>
      <td><span class="word-accent">{w}</span></td>
      <td><span class="word-pos">{pos}</span></td>
      <td>{meaning}</td>
      <td>{colloc}</td>
    </tr>
""")
        html_parts.append("""
  </tbody>
</table>
""")

    html_parts.append("</body>\n</html>\n")
    html_path = os.path.join(output_dir, f"{base_slug}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("".join(html_parts))
    print(f"[+] HTML saved to: {html_path}")

    # Headless Chrome to PDF
    pdf_path = os.path.join(output_dir, f"{base_slug}.pdf")
    chrome_path = find_chrome_executable()
    if chrome_path:
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] PDF successfully generated at: {pdf_path}")
            if not keep_html and os.path.exists(html_path):
                try:
                    os.remove(html_path)
                except OSError:
                    pass
        else:
            print(f"[-] Chrome PDF generation failed: {res.stderr}")
    else:
        print("[-] Chromium browser not found, skipped PDF export (HTML and Markdown generated).")

    if clean:
        cleanup_intermediates(output_dir, input_json=bilingual_json, keep_html=keep_html)

    final_files = [f for f in os.listdir(output_dir) if f.endswith(".pdf") or f.endswith(".md")]
    print(f"[✓] Output directory contains ONLY final study materials:")
    for ff in sorted(final_files):
        print(f"    - {ff}")

def main():
    parser = argparse.ArgumentParser(description="Render Bilingual Markdown & PDF")
    parser.add_argument("--json", required=True, help="Path to bilingual JSON file containing paragraphs and vocabulary")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--title", default="双语精读讲义", help="Document title")
    parser.add_argument("--video-url", default="", help="Original YouTube video URL")
    parser.add_argument("--speaker", default="", help="Speaker name")
    parser.add_argument("--summary", default="", help="Video content summary")
    parser.add_argument("--source-lang", default="ru", help="Source language code (e.g. ru, en, ja, de, fr)")
    parser.add_argument("--keep-html", action="store_true", help="Keep intermediate HTML file used for PDF generation")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean up intermediate JSON files in output directory")

    args = parser.parse_args()
    generate_documents(
        args.json,
        args.output_dir,
        title=args.title,
        video_url=args.video_url,
        speaker=args.speaker,
        summary=args.summary,
        source_lang=args.source_lang,
        keep_html=args.keep_html,
        clean=not args.no_clean
    )

if __name__ == "__main__":
    main()
