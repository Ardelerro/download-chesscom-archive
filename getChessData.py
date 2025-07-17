import requests
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json, text/plain, */*'
})

def get_username():
    print("Chess.com Game Downloader")
    print("=" * 40)
    while True:
        username = input("Enter your Chess.com username: ").strip()
        if not username:
            print("   Username cannot be empty. Please try again.")
            continue
        if not username.replace('_', '').replace('-', '').isalnum():
            print("   Invalid username format. Use only letters, numbers, underscores, and hyphens.")
            continue
        return username

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"HTTP {resp.status_code} for {url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

def fetch_archives(username):
    base_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    print(f"\nFetching archives list for {username}...")
    resp = fetch_with_retry(base_url)
    if not resp:
        print("   Failed to fetch archives list (username might be wrong or no games).")
        return None
    archives = resp.json().get("archives", [])
    if not archives:
        print("   No archives found for this user.")
        return None
    print(f"   Found {len(archives)} archive(s).")
    return archives

def fetch_month_games(username, archive_url):
    resp = fetch_with_retry(archive_url.replace("/pgn", ""))
    if not resp:
        return []
    return resp.json().get("games", [])

def download_games_json(username, archives, workers=5):
    output_pgn = f"{username}_all_games.pgn"
    total_games = 0
    results = []

    print(f"\nFetching {len(archives)} archives in parallel (up to {workers} workers)...")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_month_games, username, url): url for url in archives}
        for future in as_completed(futures):
            archive_url = futures[future]
            year_month = archive_url.rsplit('/', 2)[-2] + '/' + archive_url.rsplit('/', 2)[-1]
            try:
                games = future.result()
                if games:
                    results.extend(games)
                    print(f"✔ {year_month} ({len(games)} games)")
                    total_games += len(games)
                else:
                    print(f"✘ {year_month} (no games or failed)")
            except Exception as e:
                print(f"Error fetching {year_month}: {e}")

    with open(output_pgn, "w", encoding="utf-8") as f:
        for game in results:
            pgn = game.get("pgn", "").strip()
            if pgn:
                f.write(pgn + "\n\n")

    size = os.path.getsize(output_pgn)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            size_str = f"{size:.1f} {unit}"
            break
        size /= 1024
    else:
        size_str = f"{size:.1f} TB"

    print(f"\nFinished! Saved ~{total_games} games to {output_pgn}")
    print(f"File size: {size_str}")

def main():
    while True:
        username = get_username()
        archives = fetch_archives(username)
        if not archives:
            print("\n" + "=" * 50)
            print("Try a different username.")
            print("=" * 50)
            continue
        download_games_json(username, archives)
        print("\n" + "=" * 50)
        while True:
            choice = input("Download games for another user? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                print("\n" + "=" * 50)
                break
            elif choice in ['n', 'no']:
                if os.name == 'nt':
                    input("\nPress Enter to exit...")
                return
            else:
                print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n   Download cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n   Unexpected error: {e}")
        if os.name == 'nt':
            input("Press Enter to exit...")
        sys.exit(1)
