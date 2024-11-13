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
import colorsys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "/config/artists.json"
NOTIFIED_ALBUMS_PATH = "/config/notified_albums.json"
MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "Trackly/1.0.0 (https://github.com/7eventy7/trackly)"

def generate_vibrant_color():
    """Generate a vibrant color using HSV color space"""
    hue = random.random()
    saturation = random.uniform(0.7, 1.0)
    value = random.uniform(0.8, 1.0)
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    color = int(rgb[0] * 255) << 16 | int(rgb[1] * 255) << 8 | int(rgb[2] * 255)
    return color

class RateLimiter:
    def __init__(self, min_delay=1.0, max_delay=3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.consecutive_failures = 0

    def wait(self):
        now = time.time()
        delay = self.min_delay + random.random() * (self.max_delay - self.min_delay)
        if self.consecutive_failures > 0:
            delay *= (2 ** self.consecutive_failures)
            delay = min(delay, 30)
        
        time_since_last = now - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()

    def success(self):
        self.consecutive_failures = 0

    def failure(self):
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
            validate_and_update_artist_list()

def is_valid_artists_file():
    """Check if artists.json exists and contains valid data"""
    try:
        if not os.path.exists(CONFIG_PATH):
            logger.info("artists.json not found")
            return False

        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            
        required_keys = {'artists', 'last_updated'}
        if not all(key in data for key in required_keys):
            logger.warning("artists.json missing required keys")
            return False
            
        if not isinstance(data['artists'], list):
            logger.warning("artists.json 'artists' field is not a list")
            return False
            
        try:
            last_updated = datetime.fromisoformat(data['last_updated'])
            if (datetime.now() - last_updated).days > 7:  # Consider file stale after 7 days
                logger.info("artists.json is stale (>7 days old)")
                return False
        except ValueError:
            logger.warning("Invalid last_updated date format in artists.json")
            return False
            
        logger.info(f"artists.json validated successfully. Contains {len(data['artists'])} artists")
        return True
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error validating artists.json: {str(e)}")
        return False

def load_config():
    """Load environment variables"""
    update_interval = os.getenv('UPDATE_INTERVAL')
    discord_webhook = os.getenv('DISCORD_WEBHOOK')
    discord_role = os.getenv('DISCORD_ROLE')

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

    return music_path, update_interval, discord_webhook, discord_role

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

def validate_and_update_artist_list():
    """Check if artists.json needs updating and update if necessary"""
    if not is_valid_artists_file():
        logger.info("Updating artist list due to invalid or missing file")
        update_artist_list()
        return True
    return False

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
                    'id': artist_id,
                    'color': generate_vibrant_color()
                })
            else:
                logger.warning(f"Could not find MusicBrainz ID for {artist_name}")
                artists.append({
                    'name': artist_name,
                    'id': None,
                    'color': generate_vibrant_color()
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

def format_release_date(date_str):
    """Format release date to a more readable format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_str

def is_album_notified(artist, album):
    """Check if an album has already been notified"""
    try:
        with open(NOTIFIED_ALBUMS_PATH, 'r') as f:
            data = json.load(f)
            return any(n['artist'] == artist and n['album'] == album for n in data['notified_albums'])
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def add_notified_album(artist, album, release_date):
    """Add an album to the notified albums list"""
    try:
        try:
            with open(NOTIFIED_ALBUMS_PATH, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {'notified_albums': []}
        
        data['notified_albums'].append({
            'artist': artist,
            'album': album,
            'release_date': release_date,
            'notified_at': datetime.now().isoformat()
        })
        
        with open(NOTIFIED_ALBUMS_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error adding notified album: {str(e)}")

def send_discord_notification(release_info, artist_color):
    """Send Discord notification for new release"""
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    discord_role = os.getenv('DISCORD_ROLE')
    
    logger.info(f"Sending Discord notification for {release_info['artist']} - {release_info['title']}")
    
    try:
        color = int(artist_color) if artist_color is not None else 0x9B59B6
    except (ValueError, TypeError):
        color = 0x9B59B6
    
    formatted_date = format_release_date(release_info['release_date'])
    role_mention = f"<@&{discord_role}>" if discord_role else ""
    
    embed = {
        "title": "New Album Release!",
        "description": f"{release_info['artist']}\n> {release_info['title']}",
        "color": color,
        "footer": {
            "text": f"Release Date: {formatted_date}"
        }
    }
    
    payload = {
        "content": role_mention,
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
        time.sleep(600)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {str(e)}")

def check_new_releases():
    """Check for new releases from tracked artists"""
    logger.info("Starting new release check...")
    
    # Update artist list before checking releases
    if validate_and_update_artist_list():
        logger.info("Artist list was updated before release check")
    
    rate_limiter = RateLimiter()
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            artists = data['artists']
            last_check = datetime.fromisoformat(data.get('last_updated', '2024-01-01T00:00:00'))
            logger.info(f"Loaded {len(artists)} artists from config. Last check: {last_check}")
    except Exception as e:
        logger.error(f"Error reading config, skipping release check: {str(e)}")
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
                    
                    if not os.path.exists(album_folder) and not is_album_notified(artist['name'], album_title):
                        logger.info(f"Found new album for {artist['name']}: {album_title}")
                        release_info = {
                            'artist': artist['name'],
                            'title': album_title,
                            'release_date': release_date
                        }
                        
                        send_discord_notification(release_info, artist.get('color'))
                        add_notified_album(artist['name'], album_title, release_date)
                        
                except Exception as e:
                    logger.error(f"Error processing release for {artist['name']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking releases for {artist['name']}: {str(e)}")
            continue
    
    logger.info("Completed release check for all artists")

def main():
    """Main function to run the artist tracker"""
    logger.info("Starting Trackly...")
    
    # Load environment variables
    music_path, update_interval, _, _ = load_config()
    
    # Make sure config directory exists
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(NOTIFIED_ALBUMS_PATH), exist_ok=True)
        logger.info(f"Config directory ensured at {os.path.dirname(CONFIG_PATH)}")
    except Exception as e:
        logger.error(f"Failed to create config directory: {str(e)}")
        raise
    
    # Only perform initial scan if necessary
    if not is_valid_artists_file():
        logger.info("Performing initial music directory scan...")
        update_artist_list()
    else:
        logger.info("Valid artists.json found, skipping initial scan")
    
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
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Trackly...")
        observer.stop()
        observer.join()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()