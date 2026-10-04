# sub2study - Claude Code Guidelines

`sub2study` automates turning any YouTube video subtitles into publication-grade bilingual study guides and printable PDFs.

## How to execute sub2study with Claude Code

When the user asks you to process a YouTube video or generate a bilingual study guide:

1. **Step 1: Extract & Clean Subtitles**
   ```bash
   sub2study extract "<YOUTUBE_URL>" -o "./output" --lang auto
   ```
   This generates `./output/cleaned_paragraphs.json` with deduplicated, punctuation-reconstructed sentences grouped into ~50-word paragraphs.

2. **Step 2: AI Proofreading & Translation (Run by Claude)**
   - Read `./output/cleaned_paragraphs.json`.
   - Proofread and refine the source text (fix speech-to-text typos, casing, missing commas, and dialogue tags).
   - Translate each paragraph into fluent, natural Chinese in the context of the video topic.
   - Extract 15-25 high-value language learning vocabulary words with phonetic IPA, part of speech, Chinese definition, and contextual collocations from the video.
   - Save the result to `./output/bilingual_result.json`:
     ```json
     {
       "paragraphs": [
         { "timestamp": "00:00:00", "ru": "Source paragraph text...", "zh": "中文译文..." }
       ],
       "vocabulary": [
         { "word": "equity", "accent": "/ˈekwɪti/", "pos": "n.", "meaning": "公司股权", "collocation": "companies call it equity" }
       ]
     }
     ```

3. **Step 3: Render Publication-Grade PDF & Markdown**
   ```bash
   sub2study render "./output/bilingual_result.json" \
     -o "./output" \
     --title "<VIDEO_TITLE>" \
     --video-url "<YOUTUBE_URL>" \
     --speaker "<SPEAKER_NAME>" \
     --summary "<SUMMARY>" \
     --source-lang "en"
   ```
   This outputs:
   - `<TITLE>.pdf`: Print-ready A4 PDF with natural left alignment and no word hyphen cutting.
   - `<TITLE>.md`: Companion Markdown for Obsidian/Notion.
