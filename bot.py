    except praw.exceptions.APIException as e:
        if "RATELIMIT" in str(e):
            print(f"⛔ Reddit rate limit hit: {e}")

            # Try to extract the number of seconds from Reddit's error message
            import re
            match = re.search(r"(\d+)\s*seconds?", str(e))
            wait_time = int(match.group(1)) if match else 60

            print(f"⏳ Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"⚠️ API Exception: {e}")
            time.sleep(REPLY_COOLDOWN)
