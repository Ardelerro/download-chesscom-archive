import requests
import time
import sys
import os

def get_username():
    print("Chess.com Game Downloader")
    print("=" * 30)
    
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/plain, application/json, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"HTTP {resp.status_code} for {url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

def validate_username_and_get_archives(username):

    base_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    print(f"\nValidating username and fetching game archives for {username}...")
    
    try:
        archives_resp = fetch_with_retry(base_url)
        if not archives_resp:
            print("   Failed to fetch archives list")
            print("   This could mean the username doesn't exist or has no games.")
            return None
        
        archives = archives_resp.json().get("archives", [])
        if not archives:
            print("   No archives found")
            print("   This user may not have any games")
            return None
            
        print(f"   Found {len(archives)} archive(s)")
        return archives
        
    except Exception as e:
        print(f"   Error fetching archives: {e}")
        return None

def main():
    while True:

        while True:
            username = get_username()
            archives = validate_username_and_get_archives(username)
            
            if archives:
                break
            else:
                print("\n" + "=" * 50)
                print("Please try a different username.")
                print("=" * 50)
                continue
        
        output_pgn = f"{username}_all_games.pgn"
        total_games = 0
        print(f"\nDownloading games to {output_pgn}...")
        
        with open(output_pgn, "w", encoding="utf-8") as outfile:
            for i, archive_url in enumerate(archives, 1):
                pgn_url = archive_url + "/pgn"
                print(f"[{i}/{len(archives)}] Fetching {pgn_url}")
                
                resp = fetch_with_retry(pgn_url)
                if resp and resp.text.strip():
                    game_count = resp.text.count('[Event "')
                    total_games += game_count
                    
                    outfile.write(resp.text)
                    if not resp.text.endswith('\n'):
                        outfile.write('\n')
                    
                    print(f"     Added {game_count} games")
                else:
                    print(f"     Failed to fetch or empty response")
                
                time.sleep(0.1)

        print(f"\n   Successfully saved ~{total_games} games to {output_pgn}")
        print(f"   File size: {get_file_size(output_pgn)}")
        
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

def get_file_size(filename):
    try:
        size = os.path.getsize(filename)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "unknown"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n   Download cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n   Unexpected error: {e}")
        if os.name == 'nt':
            input("Press Enter to exit...")
        sys.exit(1)