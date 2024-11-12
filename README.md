# Artist Tracker

A Docker container that monitors your music library and notifies you about new releases from your favorite artists via Discord webhooks. The application scans a specified music directory for artist folders and tracks new releases using the Discogs API.

## Features

- 📁 Monitors a local music directory for artist folders
- 🎵 Tracks new releases (albums, EPs, and singles) from your artists
- 🔔 Sends Discord notifications for new releases
- 🤖 Automatic periodic checks based on configured schedule
- 🔄 Real-time updates when new artists are added to the music folder

## Prerequisites

- Docker and Docker Compose installed on your system
- A Discord webhook URL for notifications
- A local music directory organized by artist folders

## Directory Structure

Your music directory should be organized with one folder per artist:

```
Music/
├── Artist1/
├── Artist2/
├── Artist3/
└── ...
```

## Quick Start with Docker Hub

The easiest way to get started is using the pre-built Docker image:

```bash
# Pull the latest image
docker pull yourusername/artist-tracker:latest

# Create your .env file
cp .env.example .env
nano .env  # Edit with your settings

# Run with docker-compose
docker-compose up -d
```

## Environment Variables

Create a `.env` file with the following variables:

- `MUSIC_PATH`: Full path to your music directory
- `UPDATE_INTERVAL`: Time to check for updates (24-hour format, e.g., "00:00")
- `DISCORD_WEBHOOK`: Your Discord webhook URL

Example `.env` file:
```env
MUSIC_PATH=/path/to/your/music
UPDATE_INTERVAL=00:00
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your-webhook-url
```

## Installation & Usage

### Using Docker Hub Image

1. Create your `.env` file:
```bash
curl -O https://raw.githubusercontent.com/yourusername/artist-tracker/main/.env.example
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
  artist-tracker:
    image: yourusername/artist-tracker:latest
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

### Building from Source

1. Clone this repository:
```bash
git clone https://github.com/yourusername/artist-tracker.git
cd artist-tracker
```

2. Create your `.env` file:
```bash
cp .env.example .env
```

3. Edit the `.env` file with your configuration:
```bash
nano .env
```

4. Build and start the container:
```bash
docker-compose up -d --build
```

## Discord Notifications

The bot will send Discord notifications with the following information when new releases are found:

- Release type (Album, EP, or Single)
- Artist name
- Release name
- Release date
- Album artwork thumbnail

## Monitoring and Logs

View container logs:
```bash
docker-compose logs -f
```

Check container status:
```bash
docker-compose ps
```

## Stopping the Container

To stop the tracker:
```bash
docker-compose down
```

## Development

### GitHub Actions CI/CD

This project uses GitHub Actions to automatically build and publish Docker images to Docker Hub. To set up automated builds:

1. Fork this repository
2. Add the following secrets to your GitHub repository:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token (create one at https://hub.docker.com/settings/security)

The workflow will:
- Build on every push to main
- Create versioned tags for releases (v*.*.*)
- Build multi-architecture images (amd64, arm64)
- Push to Docker Hub automatically

### Version Tags

The following tags are automatically generated:
- `latest`: Most recent build from main
- `vX.Y.Z`: Release versions (e.g., v1.0.0)
- `vX.Y`: Major.Minor version (e.g., v1.0)
- `sha-XXXXXXX`: Commit SHA

## Troubleshooting

1. If the container fails to start, check your environment variables:
```bash
docker-compose config
```

2. Verify your music directory permissions:
```bash
ls -l $MUSIC_PATH
```

3. Check container logs for errors:
```bash
docker-compose logs
```

## License

MIT License - feel free to use and modify as needed.