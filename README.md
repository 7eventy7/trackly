# <img src="icons/trackly.png" alt="Trackly Logo" width="32" height="32" style="vertical-align: middle"> Trackly

> Track your favorite artists' new releases with Discord notifications

Trackly is a Docker container that monitors your music library and notifies you about new releases from your favorite artists via Discord webhooks. The application scans a specified music directory for artist folders and tracks new releases using the Discogs API.

## ✨ Features

- 📁 **Smart Directory Monitoring** - Watches your local music directory for artist folders
- 🎵 **Release Tracking** - Tracks new releases (albums, EPs, and singles) from your artists
- 🔔 **Discord Integration** - Sends beautiful Discord notifications for new releases
- 🤖 **Automated Updates** - Automatic periodic checks based on your schedule
- 🔄 **Real-time Updates** - Instant updates when new artists are added to the music folder

## 📋 Prerequisites

- Docker and Docker Compose installed on your system
- A Discord webhook URL for notifications
- A local music directory organized by artist folders

## 📁 Directory Structure

Your music directory should be organized with one folder per artist:

```
Music/
├── Artist1/
├── Artist2/
├── Artist3/
└── ...
```

## 🚀 Quick Start with Docker Hub

The easiest way to get started is using the pre-built Docker image:

```bash
# Pull the latest image
docker pull yourusername/trackly:latest

# Create your .env file
cp .env.example .env
nano .env  # Edit with your settings

# Run with docker-compose
docker-compose up -d
```

## ⚙️ Environment Variables

Create a `.env` file with the following variables:

```env
MUSIC_PATH=/path/to/your/music
UPDATE_INTERVAL=00:00
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your-webhook-url
```

## 📦 Installation & Usage

### 🐳 Using Docker Hub Image

1. Create your `.env` file:
```bash
curl -O https://raw.githubusercontent.com/yourusername/trackly/main/.env.example
mv .env.example .env
```

2. Edit the `.env` file with your configuration:
```bash
nano .env
```

3. Create a docker-compose.yml:
```yaml
version: '3.8'

services:
  trackly:
    image: yourusername/trackly:latest
    volumes:
      - ${MUSIC_PATH:-./music}:/music:ro
    environment:
      - MUSIC_PATH=/music
      - UPDATE_INTERVAL=${UPDATE_INTERVAL:-"00:00"}
      - DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
    restart: unless-stopped
```

4. Start the container:
```bash
docker-compose up -d
```

### 🛠️ Building from Source

1. Clone this repository:
```bash
git clone https://github.com/yourusername/trackly.git
cd trackly
```

2. Create and configure your `.env` file:
```bash
cp .env.example .env
nano .env
```

3. Build and start the container:
```bash
docker-compose up -d --build
```

## 💬 Discord Notifications

The bot sends beautiful Discord notifications with:

- 📀 Release type (Album, EP, or Single)
- 👤 Artist name
- 🎵 Release name
- 📅 Release date
- 🖼️ Album artwork thumbnail

## 📊 Monitoring and Logs

```bash
# View container logs
docker-compose logs -f

# Check container status
docker-compose ps

# Stop the tracker
docker-compose down
```

## 👨‍💻 Development

### 🔄 GitHub Actions CI/CD

This project uses GitHub Actions for automated Docker image builds. To set up:

1. Fork this repository
2. Add these secrets to your GitHub repository:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

### 🏷️ Version Tags

- `latest`: Most recent build from main
- `vX.Y.Z`: Release versions (e.g., v1.0.0)
- `vX.Y`: Major.Minor version (e.g., v1.0)
- `sha-XXXXXXX`: Commit SHA

## 🔧 Troubleshooting

```bash
# Check environment variables
docker-compose config

# Verify music directory permissions
ls -l $MUSIC_PATH

# Check container logs
docker-compose logs
```

## 📄 License

MIT License - feel free to use and modify as needed.

---

<div align="center">
Made with ❤️ by 7eventy7
</div>
