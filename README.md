<div align="center">

# <img src="frontend/public/icons/trackly.png" width="32" height="32" alt="Trackly Icon"> Trackly

### A web-based interface for tracking music releases.

[![GitHub stars](https://img.shields.io/github/stars/7eventy7/trackly.svg?style=social&label=Star&maxAge=2592000)](https://github.com/7eventy7/trackly/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/7eventy7/trackly.svg)](https://github.com/7eventy7/trackly/issues)
[![Docker Pulls](https://img.shields.io/docker/pulls/7eventy7/trackly.svg)](https://hub.docker.com/r/7eventy7/trackly)
[![License](https://img.shields.io/github/license/7eventy7/trackly.svg)](https://github.com/7eventy7/trackly/blob/main/LICENSE)

A modern web application designed to enhance your Jellyfin music library experience. Browse your collection with a beautiful interface and optionally receive Discord notifications for new releases from your favorite artists.

[📸 View Interface Gallery](GALLERY.md)

</div>

---

## ✨ Features

- **🌐 Modern Web Interface**: Browse your music collection with a sleek, responsive UI
- **🎵 Jellyfin Integration**: Works seamlessly with your existing Jellyfin music library
- **🎨 Artist Visualization**: Beautiful artist pages with backdrop images and album covers
- **🔍 Smart Filtering**: Filter releases by year and other metadata
- **📢 Discord Integration**: Get notified about new releases through Discord webhooks
- **🔄 Automatic Updates**: Regular checks for new releases with configurable intervals
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose
- **💪 Multi-Architecture**: Supports both AMD64 and ARM64 architectures (including Raspberry Pi)

## 📁 Required Folder Structure

Trackly is designed to work with Jellyfin's music library organization. The backdrop and cover are required for the web interface. Your music folder must follow this structure:

> **Note**: Image dimension specifications
> - backdrop.png should be 16:9 aspect ratio
> - cover.png should be 1:1 aspect ratio (square)

```
/music/
├── Artist1/
│   ├── backdrop.png
│   ├── cover.png
│   ├── Album1/
│   │   └── music files...
│   └── Album2/
│       └── music files...
└── Artist2/
    ├── backdrop.png
    ├── cover.png
    ├── Album1/
    │   └── music files...
    └── Album2/
        └── music files...
```

## 🚀 Getting Started

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/7eventy7/trackly.git
cd trackly
```

2. Configure the application:
Edit the `docker-compose.yml` file to set your desired configuration. You can configure:

3. Start the application:
```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables
These can be configured in the docker-compose.yml file:
- `UPDATE_INTERVAL`: Cron schedule for checking new releases (default: "0 0 * * *")
- `DISCORD_WEBHOOK`: Discord webhook URL for notifications (optional)
- `DISCORD_ROLE`: Discord role ID to mention in notifications (optional)
- `NOTIFY_ON_SCAN`: Send Discord notification when scan completes (default: false)
- `DISCORD_NOTIFY`: Enable/disable Discord notifications during scan (default: true)

### Volumes
- `/music`: Mount your Jellyfin music directory here
- `/data`: Persistent storage for application data

## 🛠️ Technical Stack

- React + Vite
- Tailwind CSS
- Python 3
- MusicBrainz API
- Docker
- Discord Webhooks (Optional)

## 👥 Contributing

We welcome contributions! Whether it's:

- 🐛 Reporting bugs
- 💡 Suggesting features
- 📝 Improving documentation
- 🔍 Submitting fixes
- ✨ Adding new features

Please check our [GitHub Issues](https://github.com/7eventy7/trackly/issues) before submitting new ones.

## 📝 License

MIT License - feel free to use this project for any purpose.

---

<div align="center">

Made with ❤️ by [7eventy7](https://github.com/7eventy7)

</div>