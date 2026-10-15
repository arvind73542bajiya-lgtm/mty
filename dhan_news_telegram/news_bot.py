#!/usr/bin/env python3
"""Dhan API se news headlines laakar Telegram par bhejne wala bot.

Sirf Python standard library use hoti hai (koi pip install nahi chahiye),
isliye ye PC, server ya Android (Termux) kahin bhi chal sakta hai.

Commands:
    python3 news_bot.py --chat-id   Telegram chat id pata karo
    python3 news_bot.py --test      Dhan news API ka raw jawaab dekho
    python3 news_bot.py --once      Ek baar news check karke bhejo
    python3 news_bot.py             Lagatar chalao (har POLL_SECONDS par check)
"""

import argparse
import hashlib
import html
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "config.json")
SEEN_FILE = os.path.join(HERE, "seen_news.json")
DHAN_BASE = "https://api.dhan.co"
MAX_SEEN = 2000

# Response mein headline / time / link dhoondhne ke liye possible key names
TITLE_KEYS = ("headline", "title", "newsHeadline", "heading", "subject", "news")
TIME_KEYS = ("publishedAt", "publishedTime", "newsTime", "time", "date",
             "dateTime", "timestamp", "createdAt")
LINK_KEYS = ("url", "link", "newsUrl", "sourceUrl")
SOURCE_KEYS = ("source", "sourceName", "publisher")
SYMBOL_KEYS = ("symbol", "tradingSymbol", "securityName", "companyName", "scrip")
SUMMARY_KEYS = ("summary", "description", "shortDescription", "body", "content")
ID_KEYS = ("id", "newsId", "news_id", "uuid")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        sys.exit("config.json nahi mili. config.example.json ko copy karke "
                 "config.json banao aur details bharo.")
    with open(CONFIG_FILE, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg.setdefault("news_method", "POST")
    cfg.setdefault("news_request_body", {})
    cfg.setdefault("poll_seconds", 300)
    cfg.setdefault("max_messages_per_run", 15)
    return cfg


def http_json(url, method="GET", headers=None, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} {url}: {detail[:500]}") from None
    return json.loads(raw) if raw.strip() else {}


# ---------------- Dhan ----------------

def fetch_dhan_news(cfg):
    path = cfg.get("news_path", "").strip()
    if not path or "FILL" in path:
        sys.exit("config.json mein 'news_path' bharo (api.dhan.co/v2 docs ke "
                 "News Headline section se).")
    url = path if path.startswith("http") else DHAN_BASE + "/" + path.lstrip("/")
    method = cfg["news_method"].upper()
    headers = {
        "access-token": cfg["dhan_access_token"],
        "client-id": str(cfg["dhan_client_id"]),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = cfg["news_request_body"] if method != "GET" else None
    return http_json(url, method, headers, body)


def find_news_list(data):
    """Response ke andar sabse badi list-of-dicts dhoondho (news items)."""
    best = []
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            dicts = [x for x in node if isinstance(x, dict)]
            if len(dicts) > len(best) and any(pick(d, TITLE_KEYS) for d in dicts):
                best = dicts
            stack.extend(node)
        elif isinstance(node, dict):
            stack.extend(node.values())
    if not best and isinstance(data, dict) and pick(data, TITLE_KEYS):
        best = [data]
    return best


def pick(item, keys):
    lower = {k.lower(): v for k, v in item.items()}
    for k in keys:
        v = lower.get(k.lower())
        if v not in (None, "", []):
            return v if isinstance(v, str) else str(v)
    return ""


def news_key(item):
    nid = pick(item, ID_KEYS)
    base = nid or (pick(item, TITLE_KEYS) + "|" + pick(item, TIME_KEYS))
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def format_message(item):
    e = html.escape
    title = pick(item, TITLE_KEYS)
    lines = [f"📰 <b>{e(title)}</b>"]
    summary = pick(item, SUMMARY_KEYS)
    if summary and summary != title:
        lines.append(e(summary[:600]))
    meta = [x for x in (pick(item, SYMBOL_KEYS), pick(item, SOURCE_KEYS),
                        pick(item, TIME_KEYS)) if x]
    if meta:
        lines.append("<i>" + e(" • ".join(meta)) + "</i>")
    link = pick(item, LINK_KEYS)
    if link.startswith("http"):
        lines.append(f'<a href="{e(link, quote=True)}">Poori khabar padho</a>')
    return "\n".join(lines)


# ---------------- Telegram ----------------

def tg(cfg, method, payload=None):
    url = f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/{method}"
    return http_json(url, "POST", {"Content-Type": "application/json"},
                     payload or {})


def send_telegram(cfg, text):
    tg(cfg, "sendMessage", {
        "chat_id": cfg["telegram_chat_id"],
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })


def show_chat_id(cfg):
    updates = tg(cfg, "getUpdates").get("result", [])
    chats = {}
    for u in updates:
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("title") or chat.get("first_name", "")
    if not chats:
        print("Koi message nahi mila. Telegram mein apne bot ko /start bhejo, "
              "phir ye command dobara chalao.")
    for cid, name in chats.items():
        print(f"chat id: {cid}   ({name})")


# ---------------- Main loop ----------------

def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen[-MAX_SEEN:], f)


def run_once(cfg):
    items = find_news_list(fetch_dhan_news(cfg))
    seen = load_seen()
    first_run = seen is None
    seen = seen or []
    seen_set = set(seen)
    fresh = [it for it in items if news_key(it) not in seen_set]

    if first_run:
        # Pehli baar sirf latest kuch headlines bhejo, purana dher nahi
        to_send = fresh[:5]
    else:
        to_send = fresh[:cfg["max_messages_per_run"]]

    # Purani news pehle, nayi baad mein (agar API latest-first deta hai)
    for item in reversed(to_send):
        send_telegram(cfg, format_message(item))
        time.sleep(1)  # Telegram rate limit

    seen.extend(news_key(it) for it in fresh)
    save_seen(seen)
    print(time.strftime("%H:%M:%S"),
          f"news mili: {len(items)}, nayi: {len(fresh)}, bheji: {len(to_send)}")


def main():
    ap = argparse.ArgumentParser(description="Dhan news -> Telegram")
    ap.add_argument("--chat-id", action="store_true", help="Telegram chat id dikhao")
    ap.add_argument("--test", action="store_true", help="Dhan ka raw jawaab dikhao")
    ap.add_argument("--once", action="store_true", help="Ek baar chalao")
    args = ap.parse_args()
    cfg = load_config()

    if args.chat_id:
        show_chat_id(cfg)
        return
    if args.test:
        data = fetch_dhan_news(cfg)
        print(json.dumps(data, indent=2, ensure_ascii=False)[:4000])
        items = find_news_list(data)
        print(f"\n--- {len(items)} news items pehchaane ---")
        for it in items[:5]:
            print("*", pick(it, TITLE_KEYS), "|", pick(it, TIME_KEYS))
        return
    if args.once:
        run_once(cfg)
        return

    print(f"Bot chalu. Har {cfg['poll_seconds']} second par check karega. "
          "Band karne ke liye Ctrl+C.")
    while True:
        try:
            run_once(cfg)
        except Exception as e:  # network/API error par bot band na ho
            print("Error:", e)
        time.sleep(cfg["poll_seconds"])


if __name__ == "__main__":
    main()
