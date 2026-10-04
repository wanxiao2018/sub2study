#!/usr/bin/env python3
"""
sub2study - Command Line Interface
Main entrypoint for sub2study.
"""

import sys
import os
import argparse

try:
    from .extractor import download_subtitles, parse_vtt_clean_segments, reconstruct_paragraphs
    from .renderer import generate_documents
    from .interactive_builder import build_interactive_html
    from .cookie_resolver import resolve_youtube_cookies
except ImportError:
    from extractor import download_subtitles, parse_vtt_clean_segments, reconstruct_paragraphs
    from renderer import generate_documents
    from interactive_builder import build_interactive_html
    from cookie_resolver import resolve_youtube_cookies

def main():
    parser = argparse.ArgumentParser(
        prog="sub2study",
        description="Turn YouTube video subtitles into publication-grade bilingual study guides."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Download and clean YouTube subtitles into paragraphs")
    extract_parser.add_argument("url", nargs="?", help="YouTube video URL")
    extract_parser.add_argument("--vtt", help="Path to existing local VTT/SRT file")
    extract_parser.add_argument("-o", "--output-dir", default=".", help="Output directory")
    extract_parser.add_argument("--lang", default="auto", help="Subtitle language code (default: 'auto')")
    extract_parser.add_argument("--cookies", help="Path to custom cookies.txt")
    extract_parser.add_argument("--browser", default="chrome", help="Browser name for fallback")
    extract_parser.add_argument("--min-words", type=int, default=45, help="Minimum words per paragraph")
    extract_parser.add_argument("--keep-vtt", action="store_true", help="Keep raw .vtt subtitle file in output directory")

    # Command: render
    render_parser = subparsers.add_parser("render", help="Render bilingual JSON into Markdown, HTML, and PDF")
    render_parser.add_argument("json", help="Path to bilingual_result.json")
    render_parser.add_argument("-o", "--output-dir", default=".", help="Output directory")
    render_parser.add_argument("--title", default="双语精读讲义", help="Document title")
    render_parser.add_argument("--video-url", default="", help="YouTube video URL")
    render_parser.add_argument("--speaker", default="", help="Speaker name")
    render_parser.add_argument("--summary", default="", help="Video summary")
    render_parser.add_argument("--source-lang", default="ru", help="Source language code")
    render_parser.add_argument("--keep-html", action="store_true", help="Keep intermediate HTML file used for PDF generation")
    render_parser.add_argument("--no-clean", action="store_true", help="Do not clean up intermediate JSON files in output directory")

    # Command: interactive
    interactive_parser = subparsers.add_parser("interactive", help="Generate Interactive Sentence Study HTML player")
    interactive_parser.add_argument("json", help="Path to bilingual_result.json")
    interactive_parser.add_argument("-o", "--output", required=True, help="Output HTML file path")
    interactive_parser.add_argument("--title", default="沉浸式单句精听互动讲义", help="Document title")
    interactive_parser.add_argument("--video-url", default="", help="YouTube video URL")
    interactive_parser.add_argument("--speaker", default="", help="Speaker name")
    interactive_parser.add_argument("--summary", default="", help="Video summary")

    # Command: cookies
    cookie_parser = subparsers.add_parser("cookies", help="Inspect or export browser YouTube cookies")
    cookie_parser.add_argument("--export", help="Output path for exported Netscape cookies.txt")

    args = parser.parse_args()

    if not args.command:
        # Default fallback: if first argument is a URL, treat as extract
        if len(sys.argv) > 1 and ("youtube.com" in sys.argv[1] or "youtu.be" in sys.argv[1]):
            url = sys.argv[1]
            out_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else "./study_guide"
            os.makedirs(out_dir, exist_ok=True)
            vtt = download_subtitles(url, out_dir, lang="auto")
            segs = parse_vtt_clean_segments(vtt)
            paras = reconstruct_paragraphs(segs)
            if os.path.exists(vtt):
                try:
                    os.remove(vtt)
                except OSError:
                    pass
            import json
            out_json = os.path.join(out_dir, "cleaned_paragraphs.json")
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(paras, f, ensure_ascii=False, indent=2)
            print(f"[+] Successfully extracted {len(paras)} paragraphs to: {out_json}")
            sys.exit(0)
        else:
            parser.print_help()
            sys.exit(1)

    if args.command == "extract":
        if not args.url and not args.vtt:
            print("[-] Error: URL or --vtt required.")
            sys.exit(1)
        os.makedirs(args.output_dir, exist_ok=True)
        if args.url:
            vtt = download_subtitles(args.url, args.output_dir, lang=args.lang, cookies=args.cookies, browser=args.browser, keep_vtt=args.keep_vtt)
        else:
            vtt = args.vtt
        segs = parse_vtt_clean_segments(vtt)
        paras = reconstruct_paragraphs(segs, min_words_per_para=args.min_words)
        if not args.keep_vtt and args.url and os.path.exists(vtt):
            try:
                os.remove(vtt)
            except OSError:
                pass
        import json
        out_json = os.path.join(args.output_dir, "cleaned_paragraphs.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(paras, f, ensure_ascii=False, indent=2)
        print(f"[+] Successfully extracted {len(paras)} paragraphs to: {out_json}")

    elif args.command == "render":
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

    elif args.command == "interactive":
        build_interactive_html(
            args.json,
            args.output,
            title=args.title,
            video_url=args.video_url,
            speaker=args.speaker,
            summary=args.summary
        )

    elif args.command == "cookies":
        c_args = resolve_youtube_cookies()
        print("[+] Resolved cookie arguments:", " ".join(c_args))
        if args.export and len(c_args) == 2:
            import shutil
            shutil.copy(c_args[1], args.export)
            print(f"[+] Saved cookies to: {args.export}")

if __name__ == "__main__":
    main()
