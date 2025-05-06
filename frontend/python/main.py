import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
import logging
import random
import colorsys
import glob
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from croniter import croniter, CroniterNotAlphaError, CroniterBadCronError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DATA_DIR = "/data"
MUSIC_DIR = "/music"
ARTISTS_FILE_PATH: str = os.path.join(DATA_DIR, "artists.json")
STARTUP_FILE_PATH: str = os.path.join(DATA_DIR, "startup.json")
MUSICBRAINZ_BASE_URL: str = "https://musicbrainz.org/ws/2"
USER_AGENT: str = "Trackly/1.0.0 ( https://github.com/7eventy7/trackly )"
FILE_CHECK_INTERVAL: int = 480
MAX_RETRIES: int = 3
STALE_FILE_DAYS: int = 7

def get_notified_file_path(year: Optional[int] = None) -> str:
    target_year = year if year is not None else datetime.now().year
    return os.path.join(DATA_DIR, f"notified_{target_year}.json")

def ensure_notified_file(year: Optional[int] = None) -> None:
    file_path = get_notified_file_path(year)
    if not os.path.exists(file_path):
        logger.info(f"Creating new notified file for year {year or datetime.now().year}")
        safe_write_json(file_path, {'notified_albums': []})

def check_year_change() -> None:
    current_year = datetime.now().year
    ensure_notified_file(current_year)

def ensure_config_directory() -> None:
    try:
        data_dir = Path(DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ensured at {data_dir}")
    except Exception as e:
        logger.error(f"Failed to create data directory: {str(e)}")
        raise

def load_config() -> Tuple[str, str, str, Optional[str], bool]:
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

    try:
        if not croniter.is_valid(required_vars['UPDATE_INTERVAL']):
            raise ValueError("Invalid cron expression")
        logger.info(f"Configuration loaded successfully. Update interval (cron): {required_vars['UPDATE_INTERVAL']}")
    except (CroniterNotAlphaError, CroniterBadCronError) as e:
        error_msg = f"Invalid cron expression in UPDATE_INTERVAL: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    notify_on_scan = os.getenv('NOTIFY_ON_SCAN', 'false').lower() == 'true'

    return (
        MUSIC_DIR,
        required_vars['UPDATE_INTERVAL'],
        required_vars['DISCORD_WEBHOOK'],
        os.getenv('DISCORD_ROLE'),
        notify_on_scan
    )

def is_first_startup() -> bool:
    startup_data = safe_read_json(STARTUP_FILE_PATH)
    return startup_data is None or not startup_data.get('initial_startup_complete', False)

def mark_startup_complete() -> None:
    safe_write_json(STARTUP_FILE_PATH, {
        'initial_startup_complete': True,
        'first_startup_time': datetime.now().isoformat()
    })

def send_startup_notification(webhook_url: str, discord_role: Optional[str]) -> None:
    logger.info("Sending initial startup notification to Discord")
    
    embed = {
        "title": "🎵 Trackly Started Successfully!",
        "description": "The Trackly container has been initialized and is now monitoring for new releases.",
        "color": 0x00FF00,
        "footer": {
            "text": f"First Startup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    
    role_mention = f"<@&{discord_role}>" if discord_role else ""
    
    payload = {
        "content": role_mention,
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Startup notification sent successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send startup notification: {str(e)}")

def safe_read_json(file_path: str) -> Optional[Dict[str, Any]]:
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

def safe_write_json(file_path: str, data: Dict[str, Any]) -> bool:
    try:
        temp_path = f"{file_path}.tmp"
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)

        with open(temp_path, 'r') as f:
            json.load(f)

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

def artists_file_exists() -> bool:
    return os.path.exists(ARTISTS_FILE_PATH)

class RateLimiter:
    def __init__(self, min_delay: float = 1.0, max_delay: float = 2.0):
        self.min_delay: float = min_delay
        self.max_delay: float = max_delay
        self.last_request_time: float = 0
        self.consecutive_failures: int = 0
        self.requests_this_second: int = 0
        self.last_second: int = 0

    def wait(self) -> None:
        current_time = time.time()
        current_second = int(current_time)

        if current_second != self.last_second:
            self.requests_this_second = 0
            self.last_second = current_second

        if self.requests_this_second >= 50:
            sleep_time = 1.0 - (current_time - current_second)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.requests_this_second = 0
            self.last_second = int(time.time())

        delay = self.min_delay + random.random() * (self.max_delay - self.min_delay)
        
        if self.consecutive_failures > 0:
            delay *= (2 ** self.consecutive_failures)
            delay = min(delay, 30)
        
        time_since_last = current_time - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()
        self.requests_this_second += 1

    def success(self) -> None:
        self.consecutive_failures = 0

    def failure(self) -> None:
        self.consecutive_failures += 1

def make_musicbrainz_request(url: str, params: Dict[str, Any], rate_limiter: RateLimiter) -> Optional[Dict[str, Any]]:
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    
    for attempt in range(MAX_RETRIES):
        rate_limiter.wait()
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 503:
                logger.warning("Rate limited by MusicBrainz API, backing off...")
                rate_limiter.failure()
                continue
                
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

def generate_vibrant_color() -> int:
    hue = random.random()
    saturation = random.uniform(0.7, 1.0)
    value = random.uniform(0.8, 1.0)
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return int(rgb[0] * 255) << 16 | int(rgb[1] * 255) << 8 | int(rgb[2] * 255)

def find_image(artist_path: str, base_name: str, extensions: List[str]) -> Optional[str]:
    for ext in extensions:
        for case in [ext.lower(), ext.upper()]:
            path = os.path.join(artist_path, f'{base_name}{case}')
            if os.path.exists(path):
                return path
    return None

def update_artist_list() -> bool:
    logger.info("Updating artist list...")
    rate_limiter = RateLimiter()

    try:
        artists = []
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp']  # Supported image formats
        for artist_name in [d for d in os.listdir(MUSIC_DIR) 
                          if os.path.isdir(os.path.join(MUSIC_DIR, d))]:
            artist_path = os.path.join(MUSIC_DIR, artist_name)
            backdrop = None
            cover = None
            # Check for backdrop with pattern backdrop*.{ext}
            for ext in image_extensions:
                backdrop_matches = glob.glob(os.path.join(artist_path, f'backdrop*{ext}'))
                if backdrop_matches:
                    backdrop = backdrop_matches[0]  # Use the first match
                    break
            # Check for cover, prioritizing 'cover' but falling back to 'folder'
            for ext in image_extensions:
                cover_path = os.path.join(artist_path, f'cover{ext}')
                folder_path = os.path.join(artist_path, f'folder{ext}')
                if cover is None and os.path.exists(cover_path):
                    cover = cover_path
                elif cover is None and os.path.exists(folder_path):
                    cover = folder_path
            # Include artist regardless of images
            artist_id = get_artist_id(artist_name, rate_limiter)
            artists.append({
                'name': artist_name,
                'id': artist_id,
                'color': generate_vibrant_color(),
                'backdrop': backdrop,
                'cover': cover
            })
            if not artist_id:
                logger.warning(f"Could not find MusicBrainz ID for {artist_name}")
            if not backdrop or not cover:
                logger.info(f"Including {artist_name} with missing images: backdrop={backdrop}, cover={cover}")

        logger.info(f"Found {len(artists)} artists in music directory")
        
        return safe_write_json(ARTISTS_FILE_PATH, {
            'artists': artists,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error updating artist list: {str(e)}")
        return False

def is_valid_artists_file() -> bool:
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

def format_release_date(date_str: str) -> str:
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_str

def is_album_notified(artist: str, album: str) -> bool:
    try:
        release_year = datetime.now().year
        notified_file = get_notified_file_path(release_year)
        ensure_notified_file(release_year)
        
        data = safe_read_json(notified_file)
        if not data:
            return False
        
        return any(n['artist'] == artist and n['album'] == album 
                  for n in data.get('notified_albums', []))
    except Exception as e:
        logger.error(f"Error checking notified album: {str(e)}")
        return False

def add_notified_album(artist: str, album: str, release_date: str) -> bool:
    try:
        release_year = datetime.now().year
        notified_file = get_notified_file_path(release_year)
        ensure_notified_file(release_year)
        
        data = safe_read_json(notified_file) or {'notified_albums': []}
        
        data['notified_albums'].append({
            'artist': artist,
            'album': album,
            'release_date': release_date,
            'notified_at': datetime.now().isoformat()
        })
        
        return safe_write_json(notified_file, data)
    except Exception as e:
        logger.error(f"Error adding notified album: {str(e)}")
        return False

def send_discord_notification(release_info: Dict[str, str], artist_color: Optional[int], is_scan_notification: bool = False) -> None:
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    discord_role = os.getenv('DISCORD_ROLE')
    
    if is_scan_notification:
        logger.info("Sending scan completion notification")
        embed = {
            "title": "🔍 Trackly Scan Completed",
            "description": "No new releases found",
            "color": 0x808080,
            "footer": {
                "text": f"Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
    else:
        logger.info(f"Sending Discord notification for {release_info['artist']} - {release_info['title']}")
        try:
            color = int(artist_color) if artist_color is not None else 0x9B59B6
        except (ValueError, TypeError):
            color = 0x9B59B6
        
        formatted_date = format_release_date(release_info['release_date'])
        
        embed = {
            "title": "New Album Release!",
            "description": f"{release_info['artist']}\n> {release_info['title']}",
            "color": color,
            "footer": {
                "text": f"Release Date: {formatted_date}"
            }
        }
    
    role_mention = f"<@&{discord_role}>" if discord_role else ""
    
    payload = {
        "content": role_mention,
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
        if not is_scan_notification:
            time.sleep(FILE_CHECK_INTERVAL)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {str(e)}")

def process_release_group(
    release_group: Dict[str, Any],
    artist_name: str,
    artist_color: Optional[int],
    current_year: int
) -> None:
    release_date = release_group.get('first-release-date', '')
    if not release_date.startswith(str(current_year)):
        return

    album_title = release_group['title']
    artist_folder = os.path.join(MUSIC_DIR, artist_name)
    album_folder = os.path.join(artist_folder, album_title)

    if not os.path.exists(album_folder) and not is_album_notified(artist_name, album_title):
        logger.info(f"Found new album for {artist_name}: {album_title}")
        release_info = {
            'artist': artist_name,
            'title': album_title,
            'release_date': release_date
        }

        if add_notified_album(artist_name, album_title, release_date):
            send_discord_notification(release_info, artist_color)

def check_artist_releases(artist: Dict[str, Any], rate_limiter: RateLimiter, current_year: int) -> None:
    if not artist['id']:
        logger.warning(f"Skipping {artist['name']} - no MusicBrainz ID")
        return

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
            return

        for release_group in release_data.get('release-groups', []):
            try:
                process_release_group(release_group, artist['name'], artist.get('color'), current_year)
            except Exception as e:
                logger.error(f"Error processing release for {artist['name']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error checking releases for {artist['name']}: {str(e)}")

def check_new_releases(notify_on_scan: bool = False) -> None:
    logger.info("Starting the scheduled scan...")
    
    if not artists_file_exists():
        logger.info("artists.json not found, creating it...")
        if not update_artist_list():
            logger.error("Failed to create artists.json")
            return
    elif not is_valid_artists_file():
        logger.info("artists.json exists but is invalid, updating it...")
        if not update_artist_list():
            logger.error("Failed to update artists.json")
            return
    
    check_year_change()
    
    logger.info("Checking for new releases...")
    rate_limiter = RateLimiter()
    data = safe_read_json(ARTISTS_FILE_PATH)
    
    if not data:
        logger.error("Could not read artists config, skipping release check")
        return

    artists = data['artists']
    current_year = datetime.now().year
    logger.info(f"Checking releases for {len(artists)} artists")
    
    new_releases_found = False
    for artist in artists:
        check_artist_releases(artist, rate_limiter, current_year)
        if new_releases_found:
            break
    
    if notify_on_scan and not new_releases_found:
        send_discord_notification({}, None, True)
    
    logger.info("Completed the scheduled scan")

def should_perform_release_scan(initial_scan: bool) -> bool:
    current_year = datetime.now().year
    notified_file_path = get_notified_file_path(current_year)
    
    if initial_scan:
        logger.info("Checking if release scan is needed during initial scan...")
        if not os.path.exists(notified_file_path):
            logger.info(f"notified_{current_year}.json not found during initial scan - will perform release scan")
            return True
        else:
            logger.info(f"notified_{current_year}.json exists during initial scan - skipping release scan")
            return False
    return True

def main() -> None:
    logger.info("Starting Trackly...")
    
    try:
        ensure_config_directory()
        music_path, cron_schedule, webhook_url, discord_role, notify_on_scan = load_config()
        
        initial_scan = is_first_startup()
        if initial_scan:
            send_startup_notification(webhook_url, discord_role)
            mark_startup_complete()
        
        artists_update_needed = False
        if not artists_file_exists():
            logger.info("artists.json not found, performing initial scan...")
            artists_update_needed = True
            if not update_artist_list():
                raise RuntimeError("Failed to perform initial artist list update")
        elif not is_valid_artists_file():
            logger.info("artists.json exists but is invalid, updating it...")
            artists_update_needed = True
            if not update_artist_list():
                raise RuntimeError("Failed to update artists.json")
        else:
            logger.info("Valid artists.json found, proceeding with normal operation")
        
        if artists_update_needed:
            if should_perform_release_scan(True):
                logger.info("Performing initial release scan...")
                check_new_releases(notify_on_scan)
                ensure_notified_file()
            else:
                logger.info("Skipping initial release scan as notified file exists")
        
        logger.info("Trackly startup complete - configuration validated")
        
        cron = croniter(cron_schedule, datetime.now())
        
        while True:
            next_run = cron.get_next(datetime)
            now = datetime.now()
            
            sleep_seconds = (next_run - now).total_seconds()
            if sleep_seconds > 0:
                logger.info(f"Sleeping until next scheduled run at {next_run}")
                time.sleep(sleep_seconds)
            
            check_new_releases(notify_on_scan)
            
    except Exception as e:
        logger.error(f"Critical error during startup: {str(e)}")
        raise
    except KeyboardInterrupt:
        logger.info("Shutting down Trackly...")
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()
