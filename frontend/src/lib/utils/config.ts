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

async function findAvailableYears(): Promise<number[]> {
  const years: number[] = [];
  const currentYear = new Date().getFullYear();
  const checkPromises: Promise<void>[] = [];

  // Helper function to check a specific year
  const checkYear = async (year: number) => {
    try {
      const response = await fetch(`/data/notified_${year}.json`);
      if (response.ok) {
        years.push(year);
      }
    } catch {
      // Silently ignore missing year files
    }
  };

  // Check current year and future years (up to 10 years ahead)
  for (let year = currentYear; year <= currentYear + 10; year++) {
    checkPromises.push(checkYear(year));
  }

  // Check past years (up to 10 years back)
  for (let year = currentYear - 1; year >= currentYear - 10; year--) {
    checkPromises.push(checkYear(year));
  }

  await Promise.all(checkPromises);

  // If we found any years, expand the search in both directions
  if (years.length > 0) {
    const minYear = Math.min(...years);
    const maxYear = Math.max(...years);

    const additionalChecks: Promise<void>[] = [];

    // Check 5 more years before the earliest found year
    for (let year = minYear - 1; year >= minYear - 5; year--) {
      additionalChecks.push(checkYear(year));
    }

    // Check 5 more years after the latest found year
    for (let year = maxYear + 1; year <= maxYear + 5; year++) {
      additionalChecks.push(checkYear(year));
    }

    await Promise.all(additionalChecks);
  }

  return years.sort((a, b) => b - a); // Sort years in descending order
}

async function loadReleasesForYear(year: number): Promise<NotifiedAlbum[]> {
  try {
    const fileName = `notified_${year}.json`;
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
    
    // Find all available years
    const availableYears = await findAvailableYears();
    
    // Load releases for all available years in parallel
    const releasePromises = availableYears.map(year => loadReleasesForYear(year));
    const releasesPerYear = await Promise.all(releasePromises);
    
    // Combine all releases
    const allReleases = releasesPerYear.flat();
    
    // Transform and combine the data
    return data.artists.map(artist => ({
      name: artist.name,
      coverImage: `/music/${artist.name}/backdrop.png`,
      backdropImage: `/music/${artist.name}/backdrop.png`,
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
      throw new Error('Failed to load startup config');
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading startup config:', error);
    return { initial_startup_complete: false };
  }
}