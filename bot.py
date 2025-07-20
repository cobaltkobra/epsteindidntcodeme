import praw
import os
import time
import random

EMOJI_SUFFIXES = ["🧠", "📎", "🔍", "🧬", "🐇", "🕵️‍♂️"]
def emoji_tag():
    return random.choice(EMOJI_SUFFIXES)

import csv
from datetime import datetime, timedelta

# --- CONFIG ---
REPLY_COOLDOWN = 5  # Global delay between replies (in seconds)
USER_COOLDOWN_SECONDS = 3600  # Cooldown per user (1 hour)
SUBREDDIT_COOLDOWN_SECONDS = 300  # Cooldown per subreddit (5 mins)
MIN_COMMENT_LENGTH = 50  # Skip short comments
SHADOW_MODE = False  # True = dry-run (no replies)

# --- FILE LOADERS ---
def load_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"⚠️ Could not load {filepath}: {e}")
        return []

REPLIES = load_lines("replies.txt")
KEYWORDS = [kw.lower() for kw in load_lines("keywords.txt")]
WHITELISTED_SUBS = [sub.lower() for sub in load_lines("whitelist.txt")]
REPLY_TEXT_FALLBACK = "This is a default fallback reply."

# --- REDDIT API AUTH ---
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent="epsteindidntcodeme_v3 by u/{}".format(os.environ["REDDIT_USERNAME"])
)

# --- TRACKING MAPS ---
already_replied = set()
user_cooldowns = {}
sub_cooldowns = {}

# --- CSV LOGGING FUNCTION ---
def log_to_csv(data):
    with open("log.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

# --- STARTUP LOG ---
print("🤖 Bot is starting up...")
print(f"🌀 Shadow mode: {'ON' if SHADOW_MODE else 'OFF'}")
print(f"📚 Keywords loaded: {len(KEYWORDS)}")
print(f"🧾 Reply options: {len(REPLIES)}")
print(f"📌 Whitelisted subs: {len(WHITELISTED_SUBS)}\n")

# --- MAIN LOOP ---
for comment in reddit.subreddit("all").stream.comments(skip_existing=True):
    try:
        body = comment.body.lower()
        subreddit = comment.subreddit.display_name.lower()
        author = str(comment.author)
        now = datetime.utcnow()

        if subreddit not in WHITELISTED_SUBS:
            continue
        if len(body) < MIN_COMMENT_LENGTH:
            continue
        if author == reddit.user.me():
            continue
        if comment.id in already_replied:
            continue
        if now < user_cooldowns.get(author, datetime.min):
            continue
        if now < sub_cooldowns.get(subreddit, datetime.min):
            continue

        matched = [kw for kw in KEYWORDS if kw in body]
        if not matched:
            continue

        reply_text = random.choice(REPLIES) if REPLIES else REPLY_TEXT_FALLBACK

        # --- Logging ---
        print("📝 --- REPLY LOG ---")
        print(f"📌 Subreddit   : r/{subreddit}")
        print(f"🧑 User        : u/{author}")
        print(f"🧠 Matched     : {matched}")
        print(f"💬 Snippet     : {comment.body[:120]}...")
        print(f"🔗 Comment URL : https://www.reddit.com{comment.permalink}")
        print(f"{'👻 SHADOW MODE - No reply sent' if SHADOW_MODE else '✅ Replied ✅'}")
        print("---------------\n")

        # --- CSV Logging ---
        log_to_csv([
            now.isoformat(),
            subreddit,
            author,
            comment.id,
            ", ".join(matched),
            f"https://www.reddit.com{comment.permalink}"
        ])

        # --- Reply & Cooldowns ---
        if not SHADOW_MODE:
            comment.reply(f\"{reply_text} {emoji_tag()}\")
            already_replied.add(comment.id)
            user_cooldowns[author] = now + timedelta(seconds=USER_COOLDOWN_SECONDS)
            sub_cooldowns[subreddit] = now + timedelta(seconds=SUBREDDIT_COOLDOWN_SECONDS)

        time.sleep(REPLY_COOLDOWN)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(REPLY_COOLDOWN)
