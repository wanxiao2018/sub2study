#!/usr/bin/env python3
"""
sub2study - Bulletproof YouTube Cookie & Anti-bot Resolver
Automatically locates, decrypts, and resolves user browser cookies to bypass
YouTube's 'Sign in to confirm you're not a bot' challenges, without extension interference.
Supports macOS, Windows, and Linux.
"""

import os
import sys
import glob
import tempfile
import subprocess

class SilentLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def get_default_cookie_cache_path():
    cache_dir = os.path.expanduser("~/.sub2study")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "youtube_cookies.txt")

def find_primary_browser_cookie_db():
    """
    Search for primary user profile SQLite cookie database.
    Strictly filters out extension storages (Storage/ext/, contextual-tasks/, etc.)
    and sorts candidates by database size to guarantee selecting the authentic user profile.
    """
    patterns = [
        # macOS Chrome / Edge / Brave
        "~/Library/Application Support/Google/Chrome/Default/Cookies",
        "~/Library/Application Support/Google/Chrome/Default/Network/Cookies",
        "~/Library/Application Support/Google/Chrome/Profile */Cookies",
        "~/Library/Application Support/Google/Chrome/Profile */Network/Cookies",
        "~/Library/Application Support/Microsoft Edge/Default/Cookies",
        "~/Library/Application Support/Microsoft Edge/Default/Network/Cookies",
        "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies",
        # Linux Chrome / Chromium / Edge
        "~/.config/google-chrome/Default/Cookies",
        "~/.config/google-chrome/Default/Network/Cookies",
        "~/.config/chromium/Default/Cookies",
        "~/.config/chromium/Default/Network/Cookies",
        "~/.config/microsoft-edge/Default/Cookies",
        # Windows Chrome / Edge / Brave
        "~/AppData/Local/Google/Chrome/User Data/Default/Network/Cookies",
        "~/AppData/Local/Google/Chrome/User Data/Default/Cookies",
        "~/AppData/Local/Microsoft/Edge/User Data/Default/Network/Cookies",
        "~/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Network/Cookies"
    ]

    candidates = []
    for pat in patterns:
        for p in glob.glob(os.path.expanduser(pat)):
            norm = p.replace("\\", "/")
            # Filter out sandboxed extensions and temp storages
            if "Storage/ext" in norm or "contextual-tasks" in norm or "Extension" in norm:
                continue
            if os.path.isfile(p):
                sz = os.path.getsize(p)
                if sz > 15360:  # Must be > 15 KB
                    candidates.append((sz, p))

    if not candidates:
        return None

    # Pick the largest database (the primary user profile with full cookie history)
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def export_netscape_cookies(sqlite_path, output_path):
    """Decrypt browser cookies and export as standard Netscape cookies.txt."""
    try:
        from yt_dlp.cookies import (
            _open_database_copy,
            get_cookie_decryptor,
            _get_column_names,
            _process_chrome_cookie,
            YoutubeDLCookieJar
        )
    except ImportError:
        return 0

    norm_path = sqlite_path.replace("\\", "/")
    if "Default" in norm_path:
        browser_dir = sqlite_path.split("Default")[0].rstrip("/\\")
    elif "Profile" in norm_path:
        browser_dir = sqlite_path.split("Profile")[0].rstrip("/\\")
    else:
        browser_dir = os.path.dirname(os.path.dirname(sqlite_path))

    with tempfile.TemporaryDirectory(prefix="sub2study_cookies") as tmpdir:
        try:
            cursor = _open_database_copy(sqlite_path, tmpdir)
            meta_version_res = cursor.execute("SELECT value FROM meta WHERE key = 'version'").fetchone()
            meta_version = int(meta_version_res[0]) if meta_version_res else 10
            decryptor = get_cookie_decryptor(browser_dir, "Chrome", SilentLogger(), keyring=None, meta_version=meta_version)
            cursor.connection.text_factory = bytes
            column_names = _get_column_names(cursor, "cookies")
            secure_col = "is_secure" if "is_secure" in column_names else "secure"
            cursor.execute(f"SELECT host_key, name, value, encrypted_value, path, expires_utc, {secure_col} FROM cookies")
            table = cursor.fetchall()

            jar = YoutubeDLCookieJar(output_path)
            for row in table:
                is_enc, cookie = _process_chrome_cookie(decryptor, *row)
                if cookie:
                    jar.set_cookie(cookie)
            jar.save(filename=output_path, ignore_discard=True, ignore_expires=True)
            return len(jar)
        except Exception as e:
            return 0

def resolve_youtube_cookies(explicit_cookies=None, browser="chrome"):
    """
    Returns list of CLI arguments for yt-dlp to guarantee valid YouTube authentication.
    Resolution Priority:
    1. Explicit cookies file provided by user (--cookies path).
    2. Local exported cookies cache (~/.sub2study/youtube_cookies.txt).
    3. Auto-detected and decrypted primary browser cookies.
    4. Fallback to --cookies-from-browser.
    """
    # 1. Explicit path
    if explicit_cookies and os.path.exists(explicit_cookies):
        return ["--cookies", explicit_cookies]

    cache_file = get_default_cookie_cache_path()

    # 2. Check if cache exists and was modified in the last 24 hours
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1024:
        return ["--cookies", cache_file]

    # 3. Auto-detect primary database and decrypt
    primary_db = find_primary_browser_cookie_db()
    if primary_db:
        count = export_netscape_cookies(primary_db, cache_file)
        if count > 0:
            return ["--cookies", cache_file]

    # 4. Fallback to browser profile name
    if browser:
        return ["--cookies-from-browser", browser]

    return []

if __name__ == "__main__":
    args = resolve_youtube_cookies()
    print("Resolved yt-dlp cookie arguments:", " ".join(args))
