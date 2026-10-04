#!/usr/bin/env python3
"""
Interactive Sentence-by-Sentence Study HTML Generator
Features:
1. Embedded YouTube Player with timeline sync.
2. Active sentence focus card with sentence replay loop.
3. Blind listening test mode (toggle/reveal Chinese).
4. Web Speech API native TTS pronunciation.
5. Auto-scroll karaoke-style sync with keyboard shortcuts.
6. Embedded vocabulary reference drawer.
"""

import sys
import os
import re
import json
import html
import argparse

def extract_youtube_id(url):
    m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)', url)
    return m.group(1) if m else ""

def parse_time_to_seconds(ts_str):
    try:
        parts = [float(x) for x in ts_str.strip().split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
    except Exception:
        pass
    return 0.0

def build_interactive_html(bilingual_json, output_file, title="单句精读精听互动讲义", video_url="", speaker="", summary=""):
    with open(bilingual_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    paragraphs = data.get("paragraphs", [])
    vocabulary = data.get("vocabulary", [])
    video_id = extract_youtube_id(video_url) or "8CpC8HI9TaM"

    # Augment paragraphs with seconds and end_seconds
    for i, p in enumerate(paragraphs):
        p["start_sec"] = parse_time_to_seconds(p.get("timestamp", "00:00:00"))
        if i + 1 < len(paragraphs):
            p["end_sec"] = parse_time_to_seconds(paragraphs[i + 1].get("timestamp", "00:00:00"))
        else:
            p["end_sec"] = p["start_sec"] + 30.0

    json_payload = json.dumps({
        "videoId": video_id,
        "title": title,
        "videoUrl": video_url,
        "speaker": speaker,
        "summary": summary,
        "items": paragraphs,
        "vocabulary": vocabulary
    }, ensure_ascii=False)

    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | 沉浸式单句精听互动讲义</title>
<style>
  :root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #eff6ff;
    --slate-900: #0f172a;
    --slate-800: #1e293b;
    --slate-700: #334155;
    --slate-500: #64748b;
    --slate-200: #e2e8f0;
    --slate-100: #f1f5f9;
    --slate-50: #f8fafc;
    --amber-500: #f59e0b;
    --green-600: #16a34a;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f8fafc;
    color: var(--slate-800);
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* Top Navbar */
  header {
    background: #ffffff;
    border-bottom: 1px solid var(--slate-200);
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 10;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .brand-badge {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: #fff;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }
  .header-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--slate-900);
  }
  .header-tools {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .btn {
    border: 1px solid var(--slate-200);
    background: #ffffff;
    color: var(--slate-700);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }
  .btn:hover {
    background: var(--slate-100);
    border-color: var(--slate-300);
  }
  .btn-primary {
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
  }
  .btn-primary:hover {
    background: var(--primary-dark);
  }
  .btn.active {
    background: var(--primary-light);
    color: var(--primary);
    border-color: #bfdbfe;
  }

  /* Main Workspace Layout */
  .workspace {
    flex: 1;
    display: grid;
    grid-template-columns: 460px 1fr;
    height: calc(100vh - 53px);
    overflow: hidden;
  }
  @media (max-width: 1024px) {
    .workspace { grid-template-columns: 380px 1fr; }
  }
  @media (max-width: 768px) {
    .workspace {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
      overflow-y: auto;
    }
  }

  /* Left Panel: Video & Controller */
  .player-sidebar {
    background: #ffffff;
    border-right: 1px solid var(--slate-200);
    display: flex;
    flex-direction: column;
    padding: 16px;
    overflow-y: auto;
    gap: 14px;
  }
  .video-container {
    width: 100%;
    position: relative;
    padding-bottom: 56.25%;
    border-radius: 8px;
    overflow: hidden;
    background: #000;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  }
  .video-container iframe, .video-container div#player {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
  }

  /* Active Card Focus Area */
  .active-focus-card {
    background: var(--primary-light);
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .focus-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .focus-tag {
    font-size: 11px;
    font-weight: 700;
    color: var(--primary);
    background: #dbeafe;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .focus-time {
    font-family: ui-monospace, SFMono-Regular, monospace;
    font-size: 12px;
    font-weight: 600;
    color: var(--primary-dark);
  }
  .focus-ru {
    font-size: 14.5px;
    font-weight: 600;
    color: var(--slate-900);
    line-height: 1.6;
    text-align: justify;
    text-justify: inter-word;
    hyphens: auto;
  }
  .focus-zh {
    font-size: 13.5px;
    color: var(--slate-700);
    line-height: 1.55;
    border-top: 1px dashed #bfdbfe;
    padding-top: 8px;
    text-align: justify;
  }
  .focus-controls {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 4px;
  }
  .btn-sm {
    padding: 4px 9px;
    font-size: 11.5px;
  }

  /* Keyboard Tips */
  .shortcuts-box {
    background: var(--slate-50);
    border: 1px solid var(--slate-200);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 11.5px;
    color: var(--slate-500);
    line-height: 1.6;
  }
  .kbd {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    padding: 1px 5px;
    border-radius: 4px;
    font-family: ui-monospace, monospace;
    font-weight: 600;
    color: var(--slate-800);
  }

  /* Right Panel: Sentence Stream */
  .sentence-stream {
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
  }
  .stream-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--slate-200);
    margin-bottom: 4px;
  }
  .stream-count {
    font-size: 13px;
    font-weight: 600;
    color: var(--slate-500);
  }

  /* Individual Sentence Card */
  .s-card {
    background: #ffffff;
    border: 1px solid var(--slate-200);
    border-radius: 8px;
    padding: 14px 16px;
    transition: all 0.15s ease;
    cursor: pointer;
    position: relative;
  }
  .s-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
  .s-card.playing {
    border-color: var(--primary);
    background: #f0f7ff;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
  }
  .s-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .s-idx {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--slate-500);
  }
  .s-time-btn {
    background: var(--slate-100);
    color: var(--slate-700);
    font-family: ui-monospace, monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid var(--slate-200);
    transition: all 0.1s ease;
  }
  .s-card.playing .s-time-btn {
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
  }
  .s-ru {
    font-size: 14px;
    font-weight: 500;
    color: var(--slate-900);
    line-height: 1.65;
    margin-bottom: 8px;
    text-align: justify;
    text-justify: inter-word;
    hyphens: auto;
    -webkit-hyphens: auto;
  }
  .s-zh {
    font-size: 13px;
    color: var(--slate-700);
    background: var(--slate-50);
    border-left: 3px solid var(--primary);
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    line-height: 1.6;
    text-align: justify;
    transition: all 0.2s ease;
  }
  .s-zh.hidden-mode {
    filter: blur(5px);
    user-select: none;
    cursor: pointer;
  }
  .s-zh.hidden-mode:hover {
    filter: blur(2px);
  }
  .s-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    opacity: 0.6;
    transition: opacity 0.15s ease;
  }
  .s-card:hover .s-actions, .s-card.playing .s-actions {
    opacity: 1;
  }

  /* Vocab Drawer / Modal */
  .modal-backdrop {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(2px);
    z-index: 100;
    display: none;
    align-items: center;
    justify-content: center;
  }
  .modal-content {
    background: #ffffff;
    width: 90%;
    max-width: 800px;
    max-height: 85vh;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .modal-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--slate-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .modal-body {
    padding: 20px;
    overflow-y: auto;
  }
  table.vocab-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
  }
  table.vocab-table th, table.vocab-table td {
    border: 1px solid var(--slate-200);
    padding: 9px 12px;
    text-align: left;
    vertical-align: top;
  }
  table.vocab-table th { background: var(--slate-50); font-weight: 600; }
  .v-word { color: var(--primary); font-weight: 700; font-size: 13.5px; }
  .v-pos { color: var(--slate-500); font-style: italic; font-size: 11px; }
</style>
</head>
<body>

<header>
  <div class="brand">
    <span class="brand-badge">sub2study</span>
    <span class="header-title">__TITLE__</span>
  </div>
  <div class="header-tools">
    <button class="btn" id="btn-toggle-zh" title="隐藏/揭晓所有中文译文 (快捷键 T)">
      👁️ <span>听写盲测模式</span>
    </button>
    <button class="btn" id="btn-auto-scroll" title="播放时自动跟随滚屏">
      🔄 <span id="scroll-status">自动滚屏: 开</span>
    </button>
    <button class="btn btn-primary" id="btn-vocab">
      📖 核心生词表 (<span id="vocab-count">0</span>)
    </button>
  </div>
</header>

<div class="workspace">
  <!-- Left Side: Player & Controller -->
  <aside class="player-sidebar">
    <div class="video-container">
      <div id="player"></div>
    </div>

    <!-- Active Sentence Card -->
    <div class="active-focus-card">
      <div class="focus-header">
        <span class="focus-tag">当前聚焦句子</span>
        <span class="focus-time" id="focus-timestamp">00:00:00</span>
      </div>
      <div class="focus-ru" id="focus-ru" lang="ru">点击任意右侧句子或开始播放视频...</div>
      <div class="focus-zh" id="focus-zh">点击右侧中文可单独揭晓译文</div>
      <div class="focus-controls">
        <button class="btn btn-sm" id="btn-replay-focus">🔁 单句复读 [R]</button>
        <button class="btn btn-sm" id="btn-tts-focus">🔊 原声朗读</button>
        <button class="btn btn-sm" id="btn-prev-s">◀ 上一句</button>
        <button class="btn btn-sm" id="btn-next-s">下一句 ▶</button>
      </div>
    </div>

    <!-- Keyboard Shortcuts Reference -->
    <div class="shortcuts-box">
      <strong>⌨️ 键盘快捷键</strong><br>
      • <span class="kbd">Space</span> 播放 / 暂停<br>
      • <span class="kbd">R</span> 重播当前单句<br>
      • <span class="kbd">←</span> / <span class="kbd">→</span> 上一句 / 下一句<br>
      • <span class="kbd">T</span> 切换中文显示/隐藏<br>
      • <span class="kbd">0.75x</span> / <span class="kbd">1.0x</span> 可在 YouTube 播放器齿轮设置中调速
    </div>
  </aside>

  <!-- Right Side: Interactive Sentence Stream -->
  <main class="sentence-stream" id="sentence-stream">
    <div class="stream-header">
      <span class="stream-count" id="stream-count">全部 0 个单句卡片</span>
      <span style="font-size: 11.5px; color: var(--slate-500);">💡 点击卡片或时间戳跳播 | 双击中文单独揭晓</span>
    </div>
    <div id="cards-container" style="display: flex; flex-direction: column; gap: 12px;"></div>
  </main>
</div>

<!-- Vocab Modal -->
<div class="modal-backdrop" id="vocab-modal">
  <div class="modal-content">
    <div class="modal-header">
      <h3 style="font-size: 16px; font-weight: 700; color: var(--slate-900);">📚 视频核心生词与地道表达表</h3>
      <button class="btn btn-sm" id="btn-close-vocab">✕ 关闭</button>
    </div>
    <div class="modal-body">
      <table class="vocab-table">
        <thead>
          <tr>
            <th style="width: 5%;">#</th>
            <th style="width: 25%;">单词 / 表达 (带重音)</th>
            <th style="width: 15%;">词性</th>
            <th style="width: 25%;">中文释义</th>
            <th style="width: 30%;">语境搭配与例句</th>
          </tr>
        </thead>
        <tbody id="vocab-tbody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Load YouTube IFrame API -->
<script src="https://www.youtube.com/iframe_api"></script>
<script>
  const DATA = __DATA_JSON__;
  let player = null;
  let currentIndex = 0;
  let autoScroll = true;
  let blindMode = false;
  let pollInterval = null;

  document.getElementById('vocab-count').innerText = (DATA.vocabulary || []).length;
  document.getElementById('stream-count').innerText = `全部 ${DATA.items.length} 个对照段落/句子`;

  // Render cards
  const container = document.getElementById('cards-container');
  DATA.items.forEach((item, idx) => {
    const card = document.createElement('div');
    card.className = 's-card';
    card.id = `card-${idx}`;
    card.dataset.index = idx;
    card.dataset.start = item.start_sec;
    card.dataset.end = item.end_sec;

    card.innerHTML = `
      <div class="s-meta">
        <span class="s-idx">段落 ${idx + 1}</span>
        <button class="s-time-btn" onclick="event.stopPropagation(); seekTo(${item.start_sec}, ${idx})">[${item.timestamp}] ▶</button>
      </div>
      <div class="s-ru" lang="ru">${item.ru}</div>
      <div class="s-zh" onclick="event.stopPropagation(); toggleCardZh(this)">${item.zh}</div>
      <div class="s-actions">
        <button class="btn btn-sm" onclick="event.stopPropagation(); seekTo(${item.start_sec}, ${idx})">▶ 播放</button>
        <button class="btn btn-sm" onclick="event.stopPropagation(); speakRu('${escapeJs(item.ru)}')">🔊 朗读</button>
      </div>
    `;

    card.addEventListener('click', () => {
      seekTo(item.start_sec, idx);
    });

    container.appendChild(card);
  });

  // Render Vocab Table
  const vTbody = document.getElementById('vocab-tbody');
  (DATA.vocabulary || []).forEach((v, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="text-align: center; color: var(--slate-500); font-weight: 600;">${idx + 1}</td>
      <td><span class="v-word">${v.accent || v.word}</span></td>
      <td><span class="v-pos">${v.pos || ''}</span></td>
      <td>${v.meaning || ''}</td>
      <td>${v.collocation || ''}</td>
    `;
    vTbody.appendChild(tr);
  });

  // YouTube IFrame API Callback
  function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      videoId: DATA.videoId,
      playerVars: {
        'playsinline': 1,
        'rel': 0,
        'modestbranding': 1
      },
      events: {
        'onStateChange': onPlayerStateChange
      }
    });
  }

  function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.PLAYING) {
      startSync();
    } else {
      stopSync();
    }
  }

  function startSync() {
    stopSync();
    pollInterval = setInterval(() => {
      if (!player || !player.getCurrentTime) return;
      const t = player.getCurrentTime();
      updateActiveByTime(t);
    }, 250);
  }

  function stopSync() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  function updateActiveByTime(currTime) {
    let foundIdx = -1;
    for (let i = 0; i < DATA.items.length; i++) {
      const it = DATA.items[i];
      if (currTime >= it.start_sec && currTime < it.end_sec) {
        foundIdx = i;
        break;
      }
    }
    if (foundIdx === -1 && currTime >= DATA.items[DATA.items.length - 1].start_sec) {
      foundIdx = DATA.items.length - 1;
    }
    if (foundIdx !== -1 && foundIdx !== currentIndex) {
      setActive(foundIdx, false);
    }
  }

  function setActive(idx, doSeek = true) {
    currentIndex = idx;
    const item = DATA.items[idx];
    if (!item) return;

    // Update Card UI
    document.querySelectorAll('.s-card').forEach(c => c.classList.remove('playing'));
    const activeCard = document.getElementById(`card-${idx}`);
    if (activeCard) {
      activeCard.classList.add('playing');
      if (autoScroll) {
        activeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    // Update Left Focus Card
    document.getElementById('focus-timestamp').innerText = `[${item.timestamp}]`;
    document.getElementById('focus-ru').innerText = item.ru;
    document.getElementById('focus-zh').innerText = item.zh;

    if (doSeek && player && player.seekTo) {
      player.seekTo(item.start_sec, true);
      player.playVideo();
    }
  }

  function seekTo(sec, idx) {
    setActive(idx, true);
  }

  function replayCurrent() {
    if (currentIndex >= 0 && currentIndex < DATA.items.length) {
      seekTo(DATA.items[currentIndex].start_sec, currentIndex);
    }
  }

  function toggleCardZh(el) {
    el.classList.toggle('hidden-mode');
  }

  function speakRu(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'ru-RU';
      u.rate = 0.9;
      window.speechSynthesis.speak(u);
    } else {
      alert('您的浏览器暂不支持语音合成。');
    }
  }

  function escapeJs(str) {
    return (str || '').replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
  }

  // Event Listeners
  document.getElementById('btn-replay-focus').addEventListener('click', replayCurrent);
  document.getElementById('btn-tts-focus').addEventListener('click', () => {
    if (DATA.items[currentIndex]) speakRu(DATA.items[currentIndex].ru);
  });
  document.getElementById('btn-prev-s').addEventListener('click', () => {
    if (currentIndex > 0) setActive(currentIndex - 1, true);
  });
  document.getElementById('btn-next-s').addEventListener('click', () => {
    if (currentIndex + 1 < DATA.items.length) setActive(currentIndex + 1, true);
  });

  // Toggle Blind Mode
  document.getElementById('btn-toggle-zh').addEventListener('click', function() {
    blindMode = !blindMode;
    this.classList.toggle('active', blindMode);
    document.querySelectorAll('.s-zh').forEach(el => {
      if (blindMode) {
        el.classList.add('hidden-mode');
      } else {
        el.classList.remove('hidden-mode');
      }
    });
  });

  // Auto Scroll Toggle
  document.getElementById('btn-auto-scroll').addEventListener('click', function() {
    autoScroll = !autoScroll;
    this.classList.toggle('active', autoScroll);
    document.getElementById('scroll-status').innerText = `自动滚屏: ${autoScroll ? '开' : '关'}`;
  });

  // Vocab Modal Toggle
  document.getElementById('btn-vocab').addEventListener('click', () => {
    document.getElementById('vocab-modal').style.display = 'flex';
  });
  document.getElementById('btn-close-vocab').addEventListener('click', () => {
    document.getElementById('vocab-modal').style.display = 'none';
  });
  document.getElementById('vocab-modal').addEventListener('click', (e) => {
    if (e.target.id === 'vocab-modal') {
      document.getElementById('vocab-modal').style.display = 'none';
    }
  });

  // Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    // Avoid shortcuts if typing in input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.code === 'Space') {
      e.preventDefault();
      if (!player || !player.getPlayerState) return;
      const state = player.getPlayerState();
      if (state === YT.PlayerState.PLAYING) player.pauseVideo();
      else player.playVideo();
    } else if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      replayCurrent();
    } else if (e.key === 'ArrowLeft' || e.key === 'k') {
      e.preventDefault();
      if (currentIndex > 0) setActive(currentIndex - 1, true);
    } else if (e.key === 'ArrowRight' || e.key === 'j') {
      e.preventDefault();
      if (currentIndex + 1 < DATA.items.length) setActive(currentIndex + 1, true);
    } else if (e.key === 't' || e.key === 'T') {
      e.preventDefault();
      document.getElementById('btn-toggle-zh').click();
    }
  });
</script>
</body>
</html>
"""

    rendered_html = html_template.replace("__TITLE__", html.escape(title))
    rendered_html = rendered_html.replace("__DATA_JSON__", json_payload)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"[+] Interactive Sentence Study HTML saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate Interactive Sentence Study HTML")
    parser.add_argument("--json", required=True, help="Path to bilingual_result.json")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--title", default="沉浸式单句精读精听互动讲义", help="Document title")
    parser.add_argument("--video-url", default="", help="YouTube video URL")
    parser.add_argument("--speaker", default="", help="Speaker name")
    parser.add_argument("--summary", default="", help="Video summary")

    args = parser.parse_args()
    build_interactive_html(
        args.json,
        args.output,
        title=args.title,
        video_url=args.video_url,
        speaker=args.speaker,
        summary=args.summary
    )

if __name__ == "__main__":
    main()
