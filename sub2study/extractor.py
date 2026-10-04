#!/usr/bin/env python3
"""
sub2study - Subtitle Downloader & Text Cleaner
Downloads raw VTT/SRT subtitles via yt-dlp, cleans rolling duplicates,
reconstructs complete sentences, and groups them into coherent paragraphs.
"""

import sys
import os
import re
import json
import subprocess
import argparse
import tempfile
import shutil

try:
    from .cookie_resolver import resolve_youtube_cookies
except ImportError:
    from cookie_resolver import resolve_youtube_cookies

def detect_target_lang(url, cookies=None, browser="chrome"):
    """Query YouTube metadata to find the video's original spoken/subtitle language."""
    cmd = ["yt-dlp", "--dump-single-json", "--skip-download"]
    cmd.extend(resolve_youtube_cookies(explicit_cookies=cookies, browser=browser))
    cmd.append(url)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            manual_subs = list(data.get("subtitles", {}).keys())
            auto_subs = list(data.get("automatic_captions", {}).keys())
            for k in auto_subs:
                if "-orig" in k:
                    return k.replace("-orig", "")
            if manual_subs:
                return manual_subs[0]
            if auto_subs:
                return auto_subs[0]
    except Exception as e:
        print(f"[!] Warning during language auto-detection: {e}")
    return "ru"

def download_subtitles(url, output_dir=None, lang="auto", cookies=None, browser="chrome", keep_vtt=False):
    if keep_vtt and output_dir:
        download_dir = output_dir
    else:
        download_dir = os.path.join(tempfile.gettempdir(), "sub2study_raw_subs")
    os.makedirs(download_dir, exist_ok=True)
    
    if lang == "auto":
        print("[+] Auto-detecting original language of the video...")
        detected = detect_target_lang(url, cookies=cookies, browser=browser)
        print(f"[+] Detected video language: {detected}")
        sub_lang = f"{detected},{detected}-orig"
    else:
        sub_lang = f"{lang},{lang}-orig"

    out_tmpl = os.path.join(download_dir, "%(title)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--write-sub",
        "--write-auto-sub",
        "--sub-lang", sub_lang,
        "--skip-download",
        "-o", out_tmpl
    ]
    cookie_args = resolve_youtube_cookies(explicit_cookies=cookies, browser=browser)
    cmd.extend(cookie_args)
    cmd.append(url)

    print(f"[+] Running yt-dlp: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] yt-dlp warning/error: {res.stderr}")
        if "Sign in to confirm" in res.stderr:
            print("[!] YouTube bot challenge detected. Please sign in to YouTube on your browser or provide --cookies.")

    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith(".vtt") or f.endswith(".srt")]
    if not files:
        raise FileNotFoundError(f"No subtitle (.vtt/.srt) file found in {download_dir}")
    files.sort(key=lambda x: (1 if "orig" in x else 0, os.path.getmtime(x)), reverse=True)
    return files[0]

def parse_vtt_clean_segments(vtt_file):
    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    raw_segments = []

    for b in blocks:
        lines = [l.strip() for l in b.strip().split("\n") if l.strip()]
        if not lines:
            continue
        t_m = re.search(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})", lines[0])
        if not t_m:
            continue
        start_t = t_m.group(1)
        text_lines = lines[1:]

        c_lines = [l for l in text_lines if "<c>" in l]
        if c_lines:
            for cl in c_lines:
                clean_text = re.sub(r"<[^>]+>", "", cl).strip()
                if clean_text:
                    raw_segments.append((start_t, clean_text))
        else:
            for tl in text_lines:
                clean_text = re.sub(r"<[^>]+>", "", tl).strip()
                if clean_text and (not raw_segments or raw_segments[-1][1] != clean_text):
                    raw_segments.append((start_t, clean_text))

    return raw_segments

def reconstruct_paragraphs(raw_segments, min_words_per_para=45):
    sentences = []
    curr_start = None
    curr_tokens = []

    for start_t, text in raw_segments:
        words = text.split()
        for w in words:
            if curr_start is None:
                curr_start = start_t[:8] # HH:MM:SS
            curr_tokens.append(w)
            if re.search(r"[\.\!\?]+[\"»]?$", w):
                sent_text = " ".join(curr_tokens)
                sentences.append((curr_start, sent_text))
                curr_tokens = []
                curr_start = None

    if curr_tokens:
        sentences.append((curr_start, " ".join(curr_tokens)))

    paragraphs = []
    p_start = None
    p_tokens = []

    for s_start, s_text in sentences:
        if p_start is None:
            p_start = s_start
        p_tokens.append(s_text)
        w_count = sum(len(x.split()) for x in p_tokens)
        if w_count >= min_words_per_para:
            paragraphs.append({
                "timestamp": p_start,
                "text": " ".join(p_tokens)
            })
            p_start = None
            p_tokens = []

    if p_tokens:
        paragraphs.append({
            "timestamp": p_start,
            "text": " ".join(p_tokens)
        })

    return paragraphs

def main():
    parser = argparse.ArgumentParser(description="Extract & clean YouTube subtitles")
    parser.add_argument("--url", help="YouTube video URL")
    parser.add_argument("--vtt", help="Path to existing local VTT file")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--lang", default="auto", help="Subtitle language (default 'auto')")
    parser.add_argument("--browser", default="chrome", help="Browser for cookies fallback")
    parser.add_argument("--cookies", help="Path to custom cookies.txt file")
    parser.add_argument("--min-words", type=int, default=45, help="Minimum words per paragraph")
    parser.add_argument("--keep-vtt", action="store_true", help="Keep raw subtitle (.vtt) file in output directory")

    args = parser.parse_args()

    if not args.url and not args.vtt:
        print("[-] Error: Either --url or --vtt must be specified.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    if args.url:
        vtt_file = download_subtitles(args.url, args.output_dir, lang=args.lang, cookies=args.cookies, browser=args.browser, keep_vtt=args.keep_vtt)
    else:
        vtt_file = args.vtt

    print(f"[+] Processing subtitle file: {vtt_file}")
    raw_segments = parse_vtt_clean_segments(vtt_file)
    paragraphs = reconstruct_paragraphs(raw_segments, min_words_per_para=args.min_words)

    if not args.keep_vtt and args.url and os.path.exists(vtt_file):
        try:
            os.remove(vtt_file)
        except OSError:
            pass

    out_json = os.path.join(args.output_dir, "cleaned_paragraphs.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)

    print(f"[+] Successfully extracted {len(paragraphs)} coherent paragraphs.")
    print(f"[+] Cleaned data saved to: {out_json}")

if __name__ == "__main__":
    main()
