interface ConfigArtist {
  name: string;
  id: string;
  color: number;
}

interface ArtistsConfig {
  artists: ConfigArtist[];
  last_updated: string;
}

interface NotifiedAlbum {
  artist: string;
  album: string;
  release_date: string;
  notified_at: string;
}

interface NotifiedConfig {
  notified_albums: NotifiedAlbum[];
}

// Function to get online fallback image URL
function getOnlineFallbackImage(artistName: string): string {
  // Remove special characters and spaces for the search query
  const searchQuery = encodeURIComponent(artistName.replace(/[^\w\s]/gi, ''));
  return `https://source.unsplash.com/400x400/?musician,${searchQuery}`;
}

async function loadReleasesForYear(year: number): Promise<NotifiedAlbum[]> {
  try {
    const fileName = year === new Date().getFullYear() 
      ? 'notified.json' 
      : `notified${year}.json`;
    
    const response = await fetch(`/data/${fileName}`);
    if (!response.ok) {
      if (response.status === 404) {
        return []; // No releases for this year
      }
      throw new Error(`Failed to load releases for ${year}`);
    }
    const data: NotifiedConfig = await response.json();
    return data.notified_albums;
  } catch (error) {
    console.error(`Error loading releases for ${year}:`, error);
    return [];
  }
}

export async function loadArtistsConfig() {
  try {
    // Load artists data
    const response = await fetch('/data/artists.json');
    if (!response.ok) {
      throw new Error('Failed to load artists config');
    }
    const data: ArtistsConfig = await response.json();
    
    // Load current year releases
    const currentYear = new Date().getFullYear();
    const currentReleases = await loadReleasesForYear(currentYear);
    
    // Load previous year releases
    const previousYear = currentYear - 1;
    const previousReleases = await loadReleasesForYear(previousYear);
    
    // Combine all releases
    const allReleases = [...currentReleases, ...previousReleases];
    
    // Transform and combine the data
    return data.artists.map(artist => ({
      name: artist.name,
      // Use the mounted /music path with .png extension
      coverImage: `/music/${artist.name}/backdrop.png`,
      backdropImage: `/music/${artist.name}/backdrop.png`,
      // Set online fallback image
      fallbackImage: getOnlineFallbackImage(artist.name),
      color: artist.color,
      releases: allReleases
        .filter(release => release.artist === artist.name)
        .map(release => ({
          id: `${release.artist}-${release.album}`,
          title: release.album,
          artist: release.artist,
          releaseDate: release.release_date
        }))
    }));
  } catch (error) {
    console.error('Error loading artists config:', error);
    return [];
  }
}

export async function loadNotifiedConfig() {
  try {
    const response = await fetch('/data/notified.json');
    if (!response.ok) {
      throw new Error('Failed to load notified config');
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading notified config:', error);
    return { notified_albums: [] };
  }
}

export async function loadStartupConfig() {
  try {
    const response = await fetch('/data/startup.json');
    if (!response.ok) {
      throw new Error('Failed to load startup config');
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading startup config:', error);
    return { initial_startup_complete: false };
  }
}