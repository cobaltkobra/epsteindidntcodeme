import praw
import os
import time

# --- Load reply text from file ---
with open("reply.txt", "r", encoding="utf-8") as f:
    REPLY_TEXT = f.read().strip()

# --- Config ---
KEYWORDS = ["epstein", "Epstein files", "trump", "trump is a pedo", "pedo trump", "trumpstein files", "u/EpsteinDidntCodeMe print"]

# Subreddit whitelist - lowercase only
WHITELISTED_SUBS = ["conspiracy", "politics", "worldnews", "sipstea", "agedlikemilk", "bottesting", "epsteindidntcodeme", "conservativememes", "highqualitygifs", "askreddit", "funny", "pics"]

# Stream from all Reddit comments, we'll filter later
STREAM_SUBREDDITS = "all"

# --- Reddit API login ---
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent="epsteindidntcodeme_v1 by u/{}".format(os.environ["REDDIT_USERNAME"])
)

# Track which comments have already been replied to
already_replied = set()

# --- Main loop ---
for comment in reddit.subreddit(STREAM_SUBREDDITS).stream.comments(skip_existing=True):
    try:
        subreddit_name = comment.subreddit.display_name.lower()

        if subreddit_name not in WHITELISTED_SUBS:
            continue  # skip subreddits not in the whitelist

        body = comment.body.lower()
        if any(keyword in body for keyword in KEYWORDS):
            if comment.id not in already_replied and comment.author != reddit.user.me():
                comment.reply(REPLY_TEXT)
                print(f"✅ Replied to comment ID: {comment.id} in r/{subreddit_name}")
                already_replied.add(comment.id)
                time.sleep(5)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)
