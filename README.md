# <img src="icons/trackly.png" width="32"> Trackly

A sophisticated music release tracker that monitors your music library and notifies you about new album releases from your favorite artists via Discord.

![GitHub last commit](https://img.shields.io/github/last-commit/7eventy7/trackly)
![GitHub issues](https://img.shields.io/github/issues/7eventy7/trackly)
![GitHub stars](https://img.shields.io/github/stars/7eventy7/trackly)
![GitHub license](https://img.shields.io/github/license/7eventy7/trackly)

## Features

- 🎵 Automatically scans your music directory for artists
- 🔍 Uses MusicBrainz API to track new album releases
- 🎨 Generates vibrant colors for each artist's notifications
- 📢 Sends Discord notifications for new releases
- ⚡ Smart rate limiting and error handling
- 🔄 Automatic yearly cache clearing
- 📁 Maintains a history of notified releases
- 🕒 Configurable update intervals

## Installation

1. Clone the repository:
```bash
git clone https://github.com/7eventy7/trackly.git
cd trackly
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
UPDATE_INTERVAL=08:00  # Time to check for updates (24h format)
DISCORD_WEBHOOK=your_webhook_url
DISCORD_ROLE=optional_role_id  # Optional
```

## Configuration

Trackly uses two main configuration files:

- `artists.json`: Stores tracked artists and their MusicBrainz IDs
- `notified.json`: Keeps track of previously notified releases

These files are automatically created and managed in the `/config` directory.

## Usage

1. Place Trackly in a directory with access to your music library
2. Ensure your music is organized in the format: `/music/artist_name/album_name`
3. Run Trackly:
```bash
python src/main.py
```

Trackly will:
- Scan your music directory
- Create necessary configuration files
- Start monitoring for new releases
- Send Discord notifications for new albums

## Docker Support

Trackly can be run in a Docker container:

```bash
docker-compose up -d
```

Made with ❤️ by [7eventy7](https://github.com/7eventy7)