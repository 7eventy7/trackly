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

class MusicFolderHandler(FileSystemEventHandler):
    def __init__(self, artists_file):
        self.artists_file = artists_file
        self.last_update = time.time()
        # Prevent multiple updates within 5 seconds
        self.update_cooldown = 5

    def on_any_event(self, event):
        if time.time() - self.last_update < self.update_cooldown:
            return
        
        if event.is_directory:
            self.last_update = time.time()
            update_artist_list()

def load_config():
    """Load environment variables"""
    music_path = os.getenv('MUSIC_PATH')
    update_interval = os.getenv('UPDATE_INTERVAL')
    discord_webhook = os.getenv('DISCORD_WEBHOOK')

    if not all([music_path, update_interval, discord_webhook]):
        raise ValueError("Missing required environment variables")

    return music_path, update_interval, discord_webhook

def update_artist_list():
    """Update the JSON list of artists from the music directory"""
    music_path = os.getenv('MUSIC_PATH')
    artists = [d for d in os.listdir(music_path) 
              if os.path.isdir(os.path.join(music_path, d))]
    
    with open('artists.json', 'w') as f:
        json.dump({'artists': artists, 'last_updated': datetime.now().isoformat()}, f, indent=2)

def send_discord_notification(release_info):
    """Send a Discord webhook notification about new releases"""
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    embed = {
        "title": f"New {release_info['type']} Release!",
        "description": f"Artist: {release_info['artist']}\n"
                      f"{release_info['type'].title()}: {release_info['title']}\n"
                      f"Release Date: {release_info['release_date']}",
        "color": 3447003,  # Blue color
        "thumbnail": {"url": release_info.get('thumb_url', '')}
    }
    
    payload = {"embeds": [embed]}
    requests.post(webhook_url, json=payload)

def check_new_releases():
    """Check for new releases from tracked artists"""
    try:
        with open('artists.json', 'r') as f:
            data = json.load(f)
            artists = data['artists']
            last_check = datetime.fromisoformat(data.get('last_updated', '2024-01-01T00:00:00'))
    except FileNotFoundError:
        print("No artists.json found. Running initial scan...")
        update_artist_list()
        return

    # Initialize Discogs client
    discogs = discogs_client.Client('ArtistTrackerBot/1.0')
    
    for artist in artists:
        try:
            # Search for the artist on Discogs
            results = discogs.search(artist, type='artist')
            if not results:
                continue
            
            artist_id = results[0].id
            artist_releases = discogs.artist(artist_id).releases
            
            # Check recent releases
            for release in artist_releases:
                try:
                    release_date = datetime.strptime(release.release_date, '%Y-%m-%d')
                    if release_date > last_check:
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
                    print(f"Error processing release for {artist}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error checking releases for {artist}: {e}")
            continue

def main():
    """Main function to run the artist tracker"""
    # Load environment variables
    music_path, update_interval, _ = load_config()
    
    # Initial scan of music directory
    update_artist_list()
    
    # Set up file system monitoring
    event_handler = MusicFolderHandler('artists.json')
    observer = Observer()
    observer.schedule(event_handler, music_path, recursive=False)
    observer.start()
    
    # Schedule regular checks based on update interval
    schedule.every().day.at(update_interval).do(check_new_releases)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()