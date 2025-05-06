interface ConfigArtist {
  name: string;
  id: string;
  color: number;
  backdrop?: string;
  cover?: string;
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

export const APP_VERSION = '1.1.0.3';

async function findAvailableYears(): Promise<number[]> {
  const years: number[] = [];
  const currentYear = new Date().getFullYear();
  const checkPromises: Promise<void>[] = [];

  const checkYear = async (year: number) => {
    try {
      const response = await fetch(`/data/notified_${year}.json`, { method: 'HEAD' });
      if (response.ok) {
        years.push(year);
      }
    } catch {
      // Silently skip errors
    }
  };

  // Check current year and ±5 years
  for (let year = currentYear - 5; year <= currentYear + 5; year++) {
    checkPromises.push(checkYear(year));
  }

  await Promise.all(checkPromises);
  return years.sort((a, b) => b - a);
}

async function loadReleasesForYear(year: number): Promise<NotifiedAlbum[]> {
  try {
    const response = await fetch(`/data/notified_${year}.json`);
    if (!response.ok) {
      return [];
    }
    const data: NotifiedConfig = await response.json();
    return data.notified_albums || [];
  } catch (error) {
    console.warn(`No releases found for ${year}:`, error);
    return [];
  }
}

export async function loadArtistsConfig() {
  try {
    const response = await fetch('/data/artists.json');
    if (!response.ok) {
      console.error('Failed to load artists.json:', response.status);
      return [];
    }
    const data: ArtistsConfig = await response.json();
    
    const availableYears = await findAvailableYears();
    const releasePromises = availableYears.map(year => loadReleasesForYear(year));
    const releasesPerYear = await Promise.all(releasePromises);
    const allReleases = releasesPerYear.flat();
    
    return data.artists.map(artist => ({
      name: artist.name,
      cover: artist.cover || null,
      backdrop: artist.backdrop || null,
      fallbackImage: '/icons/trackly.png',
      color: artist.color,
      releases: allReleases
        .filter(release => release.artist === artist.name)
        .map(release => ({
          id: `${release.artist}-${release.album}`,
          title: release.album,
          artist: release.artist,
          releaseDate: release.release_date
        }))
        .sort((a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime())
    }));
  } catch (error) {
    console.error('Error loading artists config:', error);
    return [];
  }
}

export async function loadStartupConfig() {
  try {
    const response = await fetch('/data/startup.json');
    if (!response.ok) {
      console.error('Failed to load startup.json:', response.status);
      return { initial_startup_complete: false };
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading startup config:', error);
    return { initial_startup_complete: false };
  }
}
