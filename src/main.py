import os
import json
import time
from datetime import datetime
import schedule
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import logging
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "/config/artists.json"
MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "Trackly/1.0.0 (https://github.com/7eventy7/trackly)"

class RateLimiter:
    def __init__(self, min_delay=1.0, max_delay=3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.consecutive_failures = 0

    def wait(self):
        """Wait appropriate time between requests"""
        now = time.time()
        # Calculate delay with jitter
        delay = self.min_delay + random.random() * (self.max_delay - self.min_delay)
        # Add exponential backoff if there were failures
        if self.consecutive_failures > 0:
            delay *= (2 ** self.consecutive_failures)
            delay = min(delay, 30)  # Cap maximum delay at 30 seconds
        
        time_since_last = now - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()

    def success(self):
        """Reset failure counter on successful request"""
        self.consecutive_failures = 0

    def failure(self):
        """Increment failure counter"""
        self.consecutive_failures += 1

class MusicFolderHandler(FileSystemEventHandler):
    def __init__(self):
        self.artists_file = CONFIG_PATH
        self.last_update = time.time()
        self.update_cooldown = 5

    def on_any_event(self, event):
        if time.time() - self.last_update < self.update_cooldown:
            return
        
        if event.is_directory:
            self.last_update = time.time()
            logger.info(f"Directory change detected: {event.src_path}")
            update_artist_list()

def load_config():
    """Load environment variables"""
    update_interval = os.getenv('UPDATE_INTERVAL')
    discord_webhook = os.getenv('DISCORD_WEBHOOK')

    logger.info("Loading configuration...")
    if not all([update_interval, discord_webhook]):
        missing_vars = [var for var, val in {
            'UPDATE_INTERVAL': update_interval,
            'DISCORD_WEBHOOK': discord_webhook
        }.items() if not val]
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError("Missing required environment variables")

    logger.info(f"Configuration loaded successfully. Update interval set to: {update_interval}")
    music_path = "/music"

    return music_path, update_interval, discord_webhook

def make_musicbrainz_request(url, params, rate_limiter):
    """Make a rate-limited request to MusicBrainz API"""
    headers = {'User-Agent': USER_AGENT}
    max_retries = 3
    
    for attempt in range(max_retries):
        rate_limiter.wait()
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            rate_limiter.success()
            return response.json()
        except requests.exceptions.RequestException as e:
            rate_limiter.failure()
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                raise
    return None

def get_artist_id(artist_name, rate_limiter):
    """Get MusicBrainz ID for an artist"""
    url = f"{MUSICBRAINZ_BASE_URL}/artist"
    params = {
        'query': artist_name,
        'limit': 1,
        'fmt': 'json'
    }
    
    try:
        data = make_musicbrainz_request(url, params, rate_limiter)
        if data and data.get('artists'):
            return data['artists'][0]['id']
        return None
    except Exception as e:
        logger.error(f"Error getting MusicBrainz ID for {artist_name}: {str(e)}")
        return None

def update_artist_list():
    """Update the JSON list of artists from the music directory"""
    logger.info("Updating artist list...")
    music_path = "/music"
    rate_limiter = RateLimiter()
    
    try:
        artists = []
        for artist_name in [d for d in os.listdir(music_path) 
                          if os.path.isdir(os.path.join(music_path, d))]:
            artist_id = get_artist_id(artist_name, rate_limiter)
            if artist_id:
                artists.append({
                    'name': artist_name,
                    'id': artist_id
                })
            else:
                logger.warning(f"Could not find MusicBrainz ID for {artist_name}")
                artists.append({
                    'name': artist_name,
                    'id': None
                })
        
        logger.info(f"Found {len(artists)} artists in music directory")
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump({
                'artists': artists,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info("Artist list updated successfully")
        logger.debug(f"Artists found: {', '.join([a['name'] for a in artists])}")
    except Exception as e:
        logger.error(f"Error updating artist list: {str(e)}")
        raise

def send_discord_notification(release_info):
    """Send a Discord webhook notification about new releases"""
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    logger.info(f"Sending Discord notification for {release_info['artist']} - {release_info['title']}")
    
    embed = {
        "title": f"New Album Release!",
        "description": f"Artist: {release_info['artist']}\n"
                      f"Album: {release_info['title']}\n"
                      f"Release Date: {release_info['release_date']}",
        "color": 3447003  # Blue color
    }
    
    payload = {"embeds": [embed]}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {str(e)}")

def check_new_releases():
    """Check for new releases from tracked artists"""
    logger.info("Starting new release check...")
    rate_limiter = RateLimiter()
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            artists = data['artists']
            last_check = datetime.fromisoformat(data.get('last_updated', '2024-01-01T00:00:00'))
            logger.info(f"Loaded {len(artists)} artists from config. Last check: {last_check}")
    except FileNotFoundError:
        logger.warning("No artists.json found. Running initial scan...")
        update_artist_list()
        return
    except json.JSONDecodeError:
        logger.error("Error reading artists.json - file may be corrupted")
        return
    except Exception as e:
        logger.error(f"Unexpected error reading config: {str(e)}")
        return

    current_year = datetime.now().year
    
    for artist in artists:
        if not artist['id']:
            logger.warning(f"Skipping {artist['name']} - no MusicBrainz ID")
            continue
            
        logger.info(f"Checking releases for artist: {artist['name']}")
        try:
            url = f"{MUSICBRAINZ_BASE_URL}/release-group"
            params = {
                'artist': artist['id'],
                'type': 'album',
                'limit': 25,
                'offset': 0,
                'fmt': 'json'
            }
            
            release_data = make_musicbrainz_request(url, params, rate_limiter)
            
            for release_group in release_data.get('release-groups', []):
                try:
                    release_date = release_group.get('first-release-date', '')
                    if not release_date.startswith(str(current_year)):
                        continue
                        
                    album_title = release_group['title']
                    artist_folder = os.path.join('/music', artist['name'])
                    album_folder = os.path.join(artist_folder, album_title)
                    
                    if not os.path.exists(album_folder):
                        logger.info(f"Found new album for {artist['name']}: {album_title}")
                        release_info = {
                            'artist': artist['name'],
                            'title': album_title,
                            'release_date': release_date
                        }
                        send_discord_notification(release_info)
                        
                except Exception as e:
                    logger.error(f"Error processing release for {artist['name']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking releases for {artist['name']}: {e}")
            continue
    
    logger.info("Completed release check for all artists")

def main():
    """Main function to run the artist tracker"""
    logger.info("Starting Trackly...")
    
    # Load environment variables
    music_path, update_interval, _ = load_config()
    
    # Make sure config directory exists
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        logger.info(f"Config directory ensured at {os.path.dirname(CONFIG_PATH)}")
    except Exception as e:
        logger.error(f"Failed to create config directory: {str(e)}")
        raise
    
    # Initial scan of music directory
    logger.info("Performing initial music directory scan...")
    update_artist_list()
    
    # Set up file system monitoring
    logger.info("Setting up file system monitoring...")
    event_handler = MusicFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, music_path, recursive=False)
    observer.start()
    logger.info(f"File system monitoring active for: {music_path}")
    
    # Schedule regular checks based on update interval
    logger.info(f"Scheduling daily checks at {update_interval}")
    schedule.every().day.at(update_interval).do(check_new_releases)
    
    # Run initial check
    logger.info("Running initial release check...")
    check_new_releases()
    
    logger.info("Trackly startup complete")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
    except KeyboardInterrupt:
        logger.info("Shutting down Trackly...")
        observer.stop()
        observer.join()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()