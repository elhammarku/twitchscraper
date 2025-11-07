import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables
load_dotenv('twitchscraper.env')
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
STREAMERS = [s.strip() for s in os.getenv("STREAMERS", "").split(",") if s.strip()]
BASE_URL = "https://api.twitch.tv/helix"

# ====================
# Get OAuth Token
# ====================
def get_access_token():
    resp = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        },
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_headers(token):
    return {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {token}"}

# ====================
# Safe GET function
# ====================
def safe_get(url, headers, params=None):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed for URL: {url} -> {e}")
        return None

# ====================
# Twitch API Functions
# ====================
# (Functions remain unchanged)

# ... [keep all existing functions here unchanged] ...

# ====================
# Main Function
# ====================
def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[ERROR] CLIENT_ID and CLIENT_SECRET must be set in environment (.env).")
        return

    token = get_access_token()
    headers = get_headers(token)
    all_data = []

    if not STREAMERS:
        print("[WARN] No streamers specified in STREAMERS environment variable.")

    scrape_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for username in STREAMERS:
        username = username.strip()
        if not username:
            continue

        user = get_user_info(headers, username)
        user_id = user.get("id")
        if not user_id:
            print(f"[WARN] Skipping {username}, user not found or API returned no data.")
            continue

        followers_count = get_followers_count(headers, user_id)
        followed_channels = get_followed_channels(headers, user_id)
        stream = get_stream(headers, user_id)
        videos = get_videos(headers, user_id)
        clips = get_clips(headers, user_id)

        viewer_count = stream.get("viewer_count", 0) if stream else 0
        game_name = get_game_name(headers, stream.get("game_id")) if stream else ""

        all_data.append({
            "Date of Scraping": scrape_date,
            "Streamer": username,
            "Display Name": user.get("display_name", ""),
            "Description": user.get("description", ""),
            "Profile Image": user.get("profile_image_url", ""),
            "Followers": followers_count,
            "Followed Channels": [c.get("to_name") for c in followed_channels],
            "Is Live": bool(stream),
            "Live Title": stream.get("title", "") if stream else "",
            "Viewer Count": viewer_count,
            "Game ID": stream.get("game_id", "") if stream else "",
            "Game Name": game_name,
            "Tags": user.get("tags", []),
            "Content Classification Labels": user.get("content_classification_labels", []),
            "Is Branded Content": user.get("is_branded_content", False),
            "Videos": len(videos),
            "Clips": len(clips)
        })

    df = pd.DataFrame(all_data)

    date_prefix = datetime.now().strftime('%Y%m%d')
    file_name = f"{date_prefix}_twitch_combined_data.csv"

    df.to_csv(file_name, index=False, encoding='utf-8-sig')  # Force UTF-8 encoding to avoid errors
    print(f"[Saved] {file_name} with {len(all_data)} streamers.")  # Replace Unicode checkmark with plain text


if __name__ == "__main__":
    main()
