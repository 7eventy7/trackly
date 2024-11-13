import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import logging
import random
import colorsys
from typing import Dict, List, Optional, Any
from pathlib import Path
from croniter import croniter, CroniterNotAlphaError, CroniterBadCronError

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration Constants
CONFIG_DIR = "/config"
ARTISTS_FILE_PATH = os.path.join(CONFIG_DIR, "artists.json")
NOTIFIED_FILE_PATH = os.path.join(CONFIG_DIR, "notified.json")
MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "Trackly/1.0.0 (https://github.com/7eventy7/trackly)"
FILE_CHECK_INTERVAL = 600  # 10 minutes in seconds
MAX_RETRIES = 3
STALE_FILE_DAYS = 7

def ensure_config_directory() -> None:
    """Ensure config directory exists and has proper permissions"""
    try:
        config_dir = Path(CONFIG_DIR)
        config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Config directory ensured at {config_dir}")
    except Exception as e:
        logger.error(f"Failed to create config directory: {str(e)}")
        raise

def safe_read_json(file_path: str) -> Optional[Dict]:
    """Safely read and parse a JSON file with proper error handling"""
    try:
        if not os.path.exists(file_path):
            logger.info(f"File not found: {file_path}")
            return None

        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return None

def safe_write_json(file_path: str, data: Dict) -> bool:
    """Safely write data to a JSON file with validation"""
    try:
        # Write to temporary file first
        temp_path = f"{file_path}.tmp"
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Validate the written data
        with open(temp_path, 'r') as f:
            json.load(f)

        # If validation successful, move temp file to actual file
        os.replace(temp_path, file_path)
        logger.info(f"Successfully wrote to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to {file_path}: {str(e)}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False

def generate_vibrant_color() -> int:
    """Generate a vibrant color using HSV color space"""
    hue = random.random()
    saturation = random.uniform(0.7, 1.0)
    value = random.uniform(0.8, 1.0)
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return int(rgb[0] * 255) << 16 | int(rgb[1] * 255) << 8 | int(rgb[2] * 255)

class RateLimiter:
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.consecutive_failures = 0

    def wait(self) -> None:
        now = time.time()
        delay = self.min_delay + random.random() * (self.max_delay - self.min_delay)
        if self.consecutive_failures > 0:
            delay *= (2 ** self.consecutive_failures)
            delay = min(delay, 30)
        
        time_since_last = now - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()

    def success(self) -> None:
        self.consecutive_failures = 0

    def failure(self) -> None:
        self.consecutive_failures += 1

def is_valid_artists_file() -> bool:
    """Check if artists.json exists and contains valid data"""
    data = safe_read_json(ARTISTS_FILE_PATH)
    if not data:
        return False

    try:
        required_keys = {'artists', 'last_updated'}
        if not all(key in data for key in required_keys):
            logger.warning("artists.json missing required keys")
            return False
            
        if not isinstance(data['artists'], list):
            logger.warning("artists.json 'artists' field is not a list")
            return False
            
        try:
            last_updated = datetime.fromisoformat(data['last_updated'])
            if (datetime.now() - last_updated).days > STALE_FILE_DAYS:
                logger.info(f"artists.json is stale (>{STALE_FILE_DAYS} days old)")
                return False
        except ValueError:
            logger.warning("Invalid last_updated date format in artists.json")
            return False
            
        logger.info(f"artists.json validated successfully. Contains {len(data['artists'])} artists")
        return True
    except Exception as e:
        logger.error(f"Error validating artists.json: {str(e)}")
        return False

def load_config() -> tuple:
    """Load environment variables with validation"""
    load_dotenv()
    
    required_vars = {
        'UPDATE_INTERVAL': os.getenv('UPDATE_INTERVAL'),
        'DISCORD_WEBHOOK': os.getenv('DISCORD_WEBHOOK')
    }

    logger.info("Loading configuration...")
    missing_vars = [var for var, val in required_vars.items() if not val]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Validate cron expression
    try:
        if not croniter.is_valid(required_vars['UPDATE_INTERVAL']):
            raise ValueError("Invalid cron expression")
        logger.info(f"Configuration loaded successfully. Update interval (cron): {required_vars['UPDATE_INTERVAL']}")
    except (CroniterNotAlphaError, CroniterBadCronError) as e:
        error_msg = f"Invalid cron expression in UPDATE_INTERVAL: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return "/music", required_vars['UPDATE_INTERVAL'], required_vars['DISCORD_WEBHOOK'], os.getenv('DISCORD_ROLE')

def make_musicbrainz_request(url: str, params: Dict, rate_limiter: RateLimiter) -> Optional[Dict]:
    """Make a rate-limited request to MusicBrainz API with retries"""
    headers = {'User-Agent': USER_AGENT}
    
    for attempt in range(MAX_RETRIES):
        rate_limiter.wait()
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            rate_limiter.success()
            return response.json()
        except requests.exceptions.RequestException as e:
            rate_limiter.failure()
            logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt == MAX_RETRIES - 1:
                raise
    return None

def get_artist_id(artist_name: str, rate_limiter: RateLimiter) -> Optional[str]:
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

def update_artist_list() -> bool:
    """Update the JSON list of artists from the music directory"""
    logger.info("Updating artist list...")
    music_path = "/music"
    rate_limiter = RateLimiter()
    
    try:
        artists = []
        for artist_name in [d for d in os.listdir(music_path) 
                          if os.path.isdir(os.path.join(music_path, d))]:
            artist_id = get_artist_id(artist_name, rate_limiter)
            artists.append({
                'name': artist_name,
                'id': artist_id,
                'color': generate_vibrant_color()
            })
            if not artist_id:
                logger.warning(f"Could not find MusicBrainz ID for {artist_name}")
        
        logger.info(f"Found {len(artists)} artists in music directory")
        
        return safe_write_json(ARTISTS_FILE_PATH, {
            'artists': artists,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error updating artist list: {str(e)}")
        return False

def format_release_date(date_str: str) -> str:
    """Format release date to a more readable format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_str

def is_album_notified(artist: str, album: str) -> bool:
    """Check if an album has already been notified"""
    data = safe_read_json(NOTIFIED_FILE_PATH)
    if not data:
        return False
    
    return any(n['artist'] == artist and n['album'] == album 
              for n in data.get('notified_albums', []))

def add_notified_album(artist: str, album: str, release_date: str) -> bool:
    """Add an album to the notified albums list with validation"""
    try:
        data = safe_read_json(NOTIFIED_FILE_PATH) or {'notified_albums': []}
        
        data['notified_albums'].append({
            'artist': artist,
            'album': album,
            'release_date': release_date,
            'notified_at': datetime.now().isoformat()
        })
        
        return safe_write_json(NOTIFIED_FILE_PATH, data)
    except Exception as e:
        logger.error(f"Error adding notified album: {str(e)}")
        return False

def send_discord_notification(release_info: Dict[str, str], artist_color: Optional[int]) -> None:
    """Send Discord notification for new release with rate limiting"""
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
        time.sleep(FILE_CHECK_INTERVAL)  # Wait before next check
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {str(e)}")

def check_year_change() -> None:
    """Check if the year has changed and clear notified.json if needed"""
    data = safe_read_json(NOTIFIED_FILE_PATH)
    if not data:
        return

    try:
        current_year = datetime.now().year
        for album in data.get('notified_albums', []):
            notified_at = datetime.fromisoformat(album['notified_at'])
            if notified_at.year < current_year:
                logger.info("Year has changed, clearing notified.json")
                safe_write_json(NOTIFIED_FILE_PATH, {'notified_albums': []})
                break
    except Exception as e:
        logger.error(f"Error checking year change: {str(e)}")

def check_new_releases() -> None:
    """Check for new releases from tracked artists with consolidated operations"""
    logger.info("Starting consolidated operations check...")
    
    # Step 1: Scan music directory and update artists.json
    logger.info("Updating artist list...")
    if not is_valid_artists_file():
        if not update_artist_list():
            logger.error("Failed to update artist list")
            return
    
    # Step 2: Check for year change
    logger.info("Checking for year change...")
    check_year_change()
    
    # Step 3: Check for new releases
    logger.info("Checking for new releases...")
    rate_limiter = RateLimiter()
    data = safe_read_json(ARTISTS_FILE_PATH)
    
    if not data:
        logger.error("Could not read artists config, skipping release check")
        return

    artists = data['artists']
    current_year = datetime.now().year
    logger.info(f"Checking releases for {len(artists)} artists")
    
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
            if not release_data:
                continue
            
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
                        
                        if add_notified_album(artist['name'], album_title, release_date):
                            send_discord_notification(release_info, artist.get('color'))
                        
                except Exception as e:
                    logger.error(f"Error processing release for {artist['name']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking releases for {artist['name']}: {str(e)}")
            continue
    
    logger.info("Completed consolidated operations check")

def main() -> None:
    """Main function to run the artist tracker with improved startup sequence"""
    logger.info("Starting Trackly...")
    
    try:
        # Step 1: Ensure config directory exists
        ensure_config_directory()
        
        # Step 2: Load environment variables
        music_path, cron_schedule, _, _ = load_config()
        
        # Step 3: Validate artists.json and perform initial scan if needed
        if not is_valid_artists_file():
            logger.info("Performing initial music directory scan...")
            if not update_artist_list():
                raise RuntimeError("Failed to perform initial artist list update")
        else:
            logger.info("Valid artists.json found, skipping initial scan")
        
        # Step 4: Run initial check
        logger.info("Running initial consolidated operations check...")
        check_new_releases()
        
        logger.info("Trackly startup complete")
        
        # Step 5: Set up cron-based scheduling
        cron = croniter(cron_schedule, datetime.now())
        
        while True:
            next_run = cron.get_next(datetime)
            now = datetime.now()
            
            # Sleep until next scheduled run
            sleep_seconds = (next_run - now).total_seconds()
            if sleep_seconds > 0:
                logger.info(f"Sleeping until next scheduled run at {next_run}")
                time.sleep(sleep_seconds)
            
            # Run the consolidated operations
            check_new_releases()
            
    except Exception as e:
        logger.error(f"Critical error during startup: {str(e)}")
        raise
    except KeyboardInterrupt:
        logger.info("Shutting down Trackly...")
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()