import { useEffect, useState, useMemo } from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { Layout } from "./components/ui/Layout";
import { ArtistGrid } from "./components/artists/ArtistGrid";
import { ArtistDetail } from "./components/artists/ArtistDetail";
import { ReleaseList } from "./components/releases/ReleaseList";
import { Settings } from "./components/settings/Settings";
import { Artist, Release, Settings as SettingsType, DEFAULT_SETTINGS } from "./lib/utils";
import { loadArtistsConfig } from "./lib/utils/config";

function ArtistDetailWrapper({ artists }: { artists: Artist[] }) {
  const { name } = useParams();
  const [selectedYear, setSelectedYear] = useState(() => new Date().getFullYear());
  
  const artist = artists.find(a => a.name === name);
  
  if (!artist) {
    return <Navigate to="/artists" replace />;
  }

  // Calculate available years from artist's releases
  const availableYears = useMemo(() => {
    const years = new Set(artist.releases.map(release => 
      new Date(release.releaseDate).getFullYear()
    ));
    return Array.from(years).sort((a, b) => b - a); // Sort descending
  }, [artist.releases]);

  // If no years available, include current year
  if (availableYears.length === 0) {
    availableYears.push(new Date().getFullYear());
  }

  return (
    <ArtistDetail
      artist={artist}
      availableYears={availableYears}
      selectedYear={selectedYear}
      onYearChange={setSelectedYear}
    />
  );
}

export default function App() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<SettingsType>(() => {
    const saved = localStorage.getItem("trackly-settings");
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

  // Load artists from config on mount
  useEffect(() => {
    async function loadArtists() {
      try {
        setIsLoading(true);
        setError(null);
        const artistsData = await loadArtistsConfig();
        setArtists(artistsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load artists');
      } finally {
        setIsLoading(false);
      }
    }

    loadArtists();
  }, []);

  // Apply theme on mount and when it changes
  useEffect(() => {
    if (settings.theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [settings.theme]);

  // Save settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem("trackly-settings", JSON.stringify(settings));
  }, [settings]);

  const handleSettingsChange = (newSettings: Partial<SettingsType>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  const handleClearData = () => {
    setArtists([]);
  };

  const handleThemeToggle = () => {
    handleSettingsChange({
      theme: settings.theme === "light" ? "dark" : "light",
    });
  };

  // Get all releases across all artists
  const allReleases: Release[] = artists.flatMap((artist) =>
    artist.releases.map((release) => ({
      ...release,
      artist: artist.name,
    }))
  );

  // Sort releases by date (newest first)
  const sortedReleases = [...allReleases].sort(
    (a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime()
  );

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">Loading artists...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Layout theme={settings.theme} onThemeToggle={handleThemeToggle}>
        <Routes>
          <Route
            path="/"
            element={<Navigate to="/artists" replace />}
          />
          <Route
            path="/artists"
            element={
              <ArtistGrid
                artists={artists}
                defaultItemsPerRow={settings.itemsPerRow}
                onItemsPerRowChange={(value) =>
                  handleSettingsChange({ itemsPerRow: value })
                }
              />
            }
          />
          <Route
            path="/artists/:name"
            element={<ArtistDetailWrapper artists={artists} />}
          />
          <Route
            path="/releases"
            element={
              <ReleaseList
                releases={sortedReleases}
                hasMore={false}
                onLoadMore={() => {}}
              />
            }
          />
          <Route
            path="/settings"
            element={
              <Settings
                settings={settings}
                onSettingsChange={handleSettingsChange}
                onClearData={handleClearData}
              />
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}