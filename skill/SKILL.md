---
name: sub2study
description: >-
  Turn YouTube video subtitles (especially Russian ASR captions) into publication-grade bilingual study guides.
  Performs intelligent ASR preprocessing/proofreading, contextual translation, stress-marked vocabulary extraction,
  and exports Markdown (.md) and PDF study guides.
---

# sub2study: YouTube Subtitles to Bilingual Study Guide

`sub2study` automates the entire journey from raw video subtitles to polished language learning materials.
It fixes speech-to-text mistakes (proper nouns, missing commas, speech disfluencies), performs context-aware translation,
extracts high-value vocabulary with stress marks, and generates ready-to-print PDFs.

---

## Workflow Overview

```
YouTube Video URL
       │
       ▼  [yt-dlp + Smart Cookie Resolver]
Raw VTT / SRT Subtitles (e.g., .ru.vtt / .ru-orig.vtt)
       │
       ▼  [sub2study extract / scripts/extract_and_clean_subtitles.py]
Mechanical Cleaning & Paragraph Chunking (strip duplicates, group by timestamps)
       │
       ▼  [★ AI Preprocessing & Proofreading ★]
Grammar cleanup, proper noun correction, punctuation restoration, filler removal
       │
       ▼  [AI Translation & Vocabulary Extraction]
Bilingual Paragraphs + Stress-marked Vocabulary Table (lemma, accent, POS, collocations)
       │
       ▼  [sub2study render & sub2study interactive]
1. Study Markdown (.md)
2. Interactive Reader HTML (.html)
3. Print-Ready PDF (.pdf via Headless Chrome, whole words preserved)
4. Interactive Sentence Study Player (Karaoke Sync + Replay + Blind Test)
```

---

## Quick Reference / Commands

### Step 1: Download & Clean Subtitles into Paragraphs
```bash
sub2study extract "<YOUTUBE_URL>" -o "~/Desktop/Russian_Study" --lang auto
```
* **Output**: `cleaned_paragraphs.json`
* **Features**:
  * **Any Language Supported**: Automatically detects the video's original spoken/subtitle language (English, Russian, Japanese, German, French, etc.) via `--lang auto`, or accepts explicit language codes like `ru`, `en`, `de`, `ja`.
  * **Bulletproof Cookie Resolution**: Auto-locates primary browser profile cookies (Chrome/Edge/Brave) to bypass YouTube's "Sign in to confirm you're not a bot" challenge without extension interference.
  * Strips ASR rolling duplicates and inline `<c>` word tags.
  * Reconstructs full sentences ending in `.`, `!`, `?`.
  * Groups sentences into natural paragraphs (~45-75 words) with anchor timestamps `[MM:SS]`.

---

### Step 2: AI Preprocessing & Proofreading
Before translating, pass the cleaned paragraphs through an AI proofreading step:
- Correct misrecognized terms (e.g. `айл-экзамен` -> `IELTS-экзамен`, `веков X и двадцать первого` -> `веков XX и XXI`).
- Restore missing commas and conjunction punctuation for complex clauses.
- Remove stuttered duplicate words while preserving colloquial idioms.

### Step 3: High-Fidelity Translation & Vocabulary Extraction
For long transcripts (over 30-40 paragraphs), split the paragraphs into chunks and invoke concurrent `self` subagents or process sequentially:
1. **Paragraph Translation Requirements**:
   - Provide natural, context-aware, idiomatic Chinese.
   - Accurately translate domain terminology.
   - Maintain the paragraph's `timestamp` and source text.
2. **Core Vocabulary Extraction (15-35 items)**:
   - `word`: Lemma
   - `accent`: Stress-marked form (e.g. `отма́зка`, `претендова́ть`)
   - `pos`: Part of speech and aspect/gender (e.g. `глагол несов.`, `сущ. ж.р.`)
   - `meaning`: Clear Chinese definition
   - `collocation`: Real collocation/usage from the video with translation

Save combined results into a single `bilingual_result.json`:
```json
{
  "paragraphs": [
    { "timestamp": "00:00:00", "ru": "...", "zh": "..." }
  ],
  "vocabulary": [
    { "word": "отмазка", "accent": "отма́зка", "pos": "сущ. ж. р.", "meaning": "借口，托词", "collocation": "это отмазка (这只是托词)" }
  ]
}
```

---

### Step 4: Render Final Deliverables & Zero-Clutter Cleanup
```bash
sub2study render "<OUTPUT_DIR>/bilingual_result.json" \
  -o "<OUTPUT_DIR>" \
  --title "<VIDEO_TITLE>" \
  --video-url "<YOUTUBE_URL>" \
  --speaker "<SPEAKER_NAME>" \
  --summary "<SUMMARY>" \
  --source-lang "en"
```
* **Strict Output Cleanliness Guarantee**:
  `sub2study render` automatically cleans up temporary HTML files and safely archives intermediate working JSON files to `~/.sub2study/cache/`.
  Upon completion, the target directory will contain **ONLY TWO FINAL DELIVERABLES**:
  - `[Title].pdf`: Print-ready A4 PDF generated via Headless Google Chrome, featuring natural left-aligned typography (`text-align: left`) that strictly preserves whole words without hyphen cutting.
  - `[Title].md`: Standard Markdown with bilingual cards and vocabulary table for Obsidian/Notion.
