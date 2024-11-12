import os
import json
import time
from datetime import datetime
import schedule
import discogs_client
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "/config/artists.json"

class MusicFolderHandler(FileSystemEventHandler):
    def __init__(self):
        self.artists_file = CONFIG_PATH
        self.last_update = time.time()
        # Prevent multiple updates within 5 seconds
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
    discogs_token = os.getenv('DISCOGS_TOKEN')

    logger.info("Loading configuration...")
    if not all([update_interval, discord_webhook, discogs_token]):
        missing_vars = [var for var, val in {
            'UPDATE_INTERVAL': update_interval,
            'DISCORD_WEBHOOK': discord_webhook,
            'DISCOGS_TOKEN': discogs_token
        }.items() if not val]
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError("Missing required environment variables")

    logger.info(f"Configuration loaded successfully. Update interval set to: {update_interval}")
    # Use the mounted path directly
    music_path = "/music"

    return music_path, update_interval, discord_webhook

def update_artist_list():
    """Update the JSON list of artists from the music directory"""
    logger.info("Updating artist list...")
    music_path = "/music"
    try:
        artists = [d for d in os.listdir(music_path) 
                  if os.path.isdir(os.path.join(music_path, d))]
        
        logger.info(f"Found {len(artists)} artists in music directory")
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump({'artists': artists, 'last_updated': datetime.now().isoformat()}, f, indent=2)
        
        logger.info("Artist list updated successfully")
        logger.debug(f"Artists found: {', '.join(artists)}")
    except Exception as e:
        logger.error(f"Error updating artist list: {str(e)}")
        raise

def send_discord_notification(release_info):
    """Send a Discord webhook notification about new releases"""
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    logger.info(f"Sending Discord notification for {release_info['artist']} - {release_info['title']}")
    
    embed = {
        "title": f"New {release_info['type']} Release!",
        "description": f"Artist: {release_info['artist']}\n"
                      f"{release_info['type'].title()}: {release_info['title']}\n"
                      f"Release Date: {release_info['release_date']}",
        "color": 3447003,  # Blue color
        "thumbnail": {"url": release_info.get('thumb_url', '')}
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

    # Initialize Discogs client
    logger.info("Initializing Discogs client...")
    discogs = discogs_client.Client('TracklyBot/1.0', user_token=os.getenv('DISCOGS_TOKEN'))
    
    for artist in artists:
        logger.info(f"Checking releases for artist: {artist}")
        try:
            # Search for the artist on Discogs
            results = discogs.search(artist, type='artist')
            if not results:
                logger.warning(f"No Discogs results found for artist: {artist}")
                continue
            
            artist_id = results[0].id
            logger.info(f"Found Discogs ID for {artist}: {artist_id}")
            artist_releases = discogs.artist(artist_id).releases
            
            # Check recent releases
            releases_checked = 0
            for release in artist_releases:
                try:
                    release_date = datetime.strptime(release.release_date, '%Y-%m-%d')
                    releases_checked += 1
                    
                    if release_date > last_check:
                        logger.info(f"Found new release for {artist}: {release.title}")
                        # Determine release type
                        release_type = 'album'
                        if release.formats[0].get('quantity', '1') == '1':
                            if release.formats[0].get('descriptions', [''])[0] == 'Single':
                                release_type = 'track'
                            elif release.formats[0].get('descriptions', [''])[0] == 'EP':
                                release_type = 'ep'
                        
                        release_info = {
                            'type': release_type,
                            'artist': artist,
                            'title': release.title,
                            'release_date': release.release_date,
                            'thumb_url': release.thumb
                        }
                        
                        send_discord_notification(release_info)
                except (AttributeError, ValueError) as e:
                    logger.error(f"Error processing release for {artist}: {e}")
                    continue
            
            logger.info(f"Checked {releases_checked} releases for {artist}")
                    
        except Exception as e:
            logger.error(f"Error checking releases for {artist}: {e}")
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