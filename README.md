<div align="center">

# <img src="frontend/public/icons/trackly.png" width="32" height="32" alt="Trackly Icon"> Trackly

### Music Release Tracker for Discord

[![GitHub stars](https://img.shields.io/github/stars/7eventy7/trackly.svg?style=social&label=Star&maxAge=2592000)](https://github.com/7eventy7/trackly/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/7eventy7/trackly.svg)](https://github.com/7eventy7/trackly/issues)
[![Docker Pulls](https://img.shields.io/docker/pulls/7eventy7/trackly.svg)](https://hub.docker.com/r/7eventy7/trackly)
[![License](https://img.shields.io/github/license/7eventy7/trackly.svg)](https://github.com/7eventy7/trackly/blob/main/LICENSE)

A powerful python application that monitors your music library and notifies you about new album releases from your favorite artists through discord. Stay updated with the latest releases from artists in your collection.

</div>

---

## ✨ Features

- **🎵 Automatic Artist Tracking**: Automatically tracks artists from your music directory
- **🔍 MusicBrainz Integration**: Uses MusicBrainz API for accurate release information
- **📢 Discord Notifications**: Get notified about new releases through Discord webhooks
- **🎨 Unique Artist Colors**: Each artist gets their own vibrant color for easy identification
- **⏱️ Smart Rate Limiting**: Built-in rate limiting for API requests
- **🔄 Automatic Updates**: Regular checks for new releases with configurable intervals
- **📅 Year-Based Reset**: Notification history automatically resets each year
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose

## 🚀 Getting Started

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/7eventy7/trackly.git
cd trackly
```

2. Configure your environment variables:
```bash
cp .env.example .env
# Edit .env with your Discord webhook URL and settings
```

3. Start the application:
```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables
- `UPDATE_INTERVAL`: Cron schedule to check for releases (required)
- `DISCORD_WEBHOOK`: Your Discord webhook URL (required)
- `DISCORD_ROLE`: Discord role ID to mention in notifications (optional)


### Volumes
- `/music`: Mount your music directory here
- `/config`: Persistent storage for application data

## 🛠️ Technical Stack

- Python 3
- MusicBrainz API
- Discord Webhooks
- Docker
- Schedule
- Requests
- Logging
- JSON

## 👥 Contributing

We love your input! We want to make contributing to Trackly as easy and transparent as possible, whether it's:

- 💡 Suggesting new features
- 🐛 Reporting a bug
- 📝 Improving documentation
- 🔍 Submitting bug fixes
- ✨ Proposing new features

### Feature Requests

We're always looking for ways to make Trackly better! If you have an idea for a new feature:

1. Check the [GitHub Issues](https://github.com/7eventy7/trackly/issues) to see if it's already been suggested
2. If not, create a new issue with the label `feature request`
3. Describe your feature idea in detail:
   - What problem does it solve?
   - How would it work?
   - Any technical considerations?
4. Engage with the community in the discussion

Your feature requests help shape the future of Trackly. No suggestion is too small - we appreciate all input!

## 📝 License

MIT License - feel free to use this project for any purpose.

---

<div align="center">

Made with ❤️ by [7eventy7](https://github.com/7eventy7)

</div>
