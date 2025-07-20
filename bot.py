import praw
import os
import time

# --- Load reply text from file ---
def load_reply(filepath="reply.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reply = f.read().strip()
            print("✅ Reply text loaded.")
            return reply
    except Exception as e:
        print(f"⚠️ Could not load reply text: {e}")
        return "This is a default fallback reply."

REPLY_TEXT = load_reply()

# --- Load subreddit whitelist from file ---
def load_whitelist(filepath="whitelist.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            subs = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
            print(f"✅ Loaded {len(subs)} whitelisted subs.")
            return subs
    except Exception as e:
        print(f"⚠️ Could not load whitelist: {e}")
        return []

WHITELISTED_SUBS = load_whitelist()

# --- Load keywords and key phrases from file ---
def load_keywords(filepath="keywords.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            keywords = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
            print(f"✅ Loaded {len(keywords)} keywords.")
            return keywords
    except Exception as e:
        print(f"⚠️ Could not load keywords: {e}")
        return []

KEYWORDS = load_keywords()

# --- Reddit API login ---
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent="epsteindidntcodeme_v2 by u/{}".format(os.environ["REDDIT_USERNAME"])
)

# --- Bot config ---
STREAM_SUBREDDITS = "all"
REPLY_COOLDOWN = 2  # seconds between replies
already_replied = set()

# --- Bot startup logs ---
print("🤖 Bot is starting...")
print("🔍 Watching subreddits:", WHITELISTED_SUBS)
print("📚 Keywords:", KEYWORDS)

# --- Main loop ---
for comment in reddit.subreddit(STREAM_SUBREDDITS).stream.comments(skip_existing=True):
    try:
        subreddit_name = comment.subreddit.display_name.lower()

        if subreddit_name not in WHITELISTED_SUBS:
            continue

        body = comment.body.lower()
        matched = [kw for kw in KEYWORDS if kw in body]

        if matched:
            if comment.id not in already_replied and comment.author != reddit.user.me():
                comment.reply(REPLY_TEXT)

                # 📜 Internal Logging
                print("📝 --- REPLY LOG ---")
                print(f"📌 Subreddit   : r/{subreddit_name}")
                print(f"🧑 User        : u/{comment.author}")
                print(f"🧠 Matched     : {matched}")
                print(f"💬 Snippet     : {comment.body[:120]}...")
                print(f"🔗 Comment URL : https://www.reddit.com{comment.permalink}")
                print("✅ Replied ✅")
                print("---------------\n")

                already_replied.add(comment.id)
                time.sleep(REPLY_COOLDOWN)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(REPLY_COOLDOWN)
