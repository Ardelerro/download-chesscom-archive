# Chess.com Game Downloader

A simple Python script to **download all games (PGN files)** from any Chess.com username.

---

## Features

- Fetches all available game archives from Chess.com API
- Downloads all PGNs and merges them into a single file
- Handles rate limits with retries
- Shows progress and number of games fetched
- Works on Windows, macOS, and Linux

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/chesscom-game-downloader.git
cd chesscom-game-downloader
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python chesscom_downloader.py
```

You will be prompted for a Chess.com username. Example:

```
Chess.com Game Downloader
==============================
Enter your Chess.com username: magnuscarlsen

Validating username and fetching game archives for magnuscarlsen...
Found 57 archive(s)
Downloading games to magnuscarlsen_all_games.pgn...
[1/57] Fetching ...
```

When complete, it will save a single PGN file like:

```
magnuscarlsen_all_games.pgn
```

## Example

Example session:

```
Chess.com Game Downloader
==============================
Enter your Chess.com username: hikaru

Validating username and fetching game archives for hikaru...
Found 120 archive(s)
Downloading games to hikaru_all_games.pgn...
[1/120] Fetching ...
Added 24 games ...

Successfully saved ~2850 games to hikaru_all_games.pgn
File size: 3.2 MB
```