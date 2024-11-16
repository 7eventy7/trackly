import { useEffect, useState, useMemo } from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams, useLocation } from "react-router-dom";
import * as Slider from "@radix-ui/react-slider";
import { Layout } from "./components/ui/Layout";
import { ArtistGrid } from "./components/artists/ArtistGrid";
import { ArtistDetail } from "./components/artists/ArtistDetail";
import { ReleaseList } from "./components/releases/ReleaseList";
import { YearFilter, FilterPeriod } from "./components/ui/YearFilter";
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

  const availableYears = useMemo(() => {
    const years = new Set(artist.releases.map(release => 
      new Date(release.releaseDate).getFullYear()
    ));
    return Array.from(years).sort((a, b) => b - a);
  }, [artist.releases]);

  if (availableYears.length === 0) {
    availableYears.push(new Date().getFullYear());
  }

  return (
    <ArtistDetail
      artist={artist}
      availableYears={availableYears}
      selectedPeriod={selectedYear}
      onPeriodChange={setSelectedYear}
    />
  );
}

function GridSizeSlider({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm font-medium">Grid Size:</span>
      <Slider.Root
        className="relative flex h-5 w-[200px] touch-none items-center"
        defaultValue={[value]}
        min={4}
        max={16}
        step={1}
        onValueChange={(values) => onChange(values[0])}
      >
        <Slider.Track className="relative h-1 w-full grow rounded-full bg-secondary">
          <Slider.Range className="absolute h-full rounded-full bg-primary" />
        </Slider.Track>
        <Slider.Thumb
          className="block h-4 w-4 rounded-full bg-primary shadow transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          aria-label="Grid size"
        />
      </Slider.Root>
      <span className="min-w-[2rem] text-sm tabular-nums">
        {value}
      </span>
    </div>
  );
}

export default function App() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterPeriod, setFilterPeriod] = useState<FilterPeriod>("all");
  const [settings, setSettings] = useState<SettingsType>(() => {
    const saved = localStorage.getItem("trackly-settings");
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

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

  useEffect(() => {
    if (settings.theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [settings.theme]);

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

  const allReleases: Release[] = artists.flatMap((artist) =>
    artist.releases.map((release) => ({
      ...release,
      artist: artist.name,
    }))
  );

  const sortedReleases = [...allReleases].sort(
    (a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime()
  );

  const artistColors = useMemo(() => {
    const colorMap: Record<string, number> = {};
    artists.forEach(artist => {
      colorMap[artist.name] = artist.color;
    });
    return colorMap;
  }, [artists]);

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

  const getHeaderExtra = (pathname: string) => {
    if (pathname === "/artists") {
      return (
        <GridSizeSlider
          value={settings.itemsPerRow}
          onChange={(value) => handleSettingsChange({ itemsPerRow: value })}
        />
      );
    }
    if (pathname === "/releases") {
      return (
        <YearFilter
          value={filterPeriod}
          onChange={setFilterPeriod}
          checkYearsFromFiles={true}
          className="bg-background hover:bg-accent/80"
        />
      );
    }
    return null;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout
              theme={settings.theme}
              onThemeToggle={handleThemeToggle}
              headerExtra={getHeaderExtra("/")}
            >
              <Navigate to="/artists" replace />
            </Layout>
          }
        />
        <Route
          path="/artists"
          element={
            <Layout
              theme={settings.theme}
              onThemeToggle={handleThemeToggle}
              headerExtra={getHeaderExtra("/artists")}
            >
              <ArtistGrid
                artists={artists}
                defaultItemsPerRow={settings.itemsPerRow}
                onItemsPerRowChange={(value) =>
                  handleSettingsChange({ itemsPerRow: value })
                }
              />
            </Layout>
          }
        />
        <Route
          path="/artists/:name"
          element={
            <Layout theme={settings.theme} onThemeToggle={handleThemeToggle}>
              <ArtistDetailWrapper artists={artists} />
            </Layout>
          }
        />
        <Route
          path="/releases"
          element={
            <Layout
              theme={settings.theme}
              onThemeToggle={handleThemeToggle}
              headerExtra={getHeaderExtra("/releases")}
            >
              <ReleaseList
                releases={sortedReleases}
                hasMore={false}
                onLoadMore={() => {}}
                artistColors={artistColors}
                filterPeriod={filterPeriod}
                onFilterChange={setFilterPeriod}
              />
            </Layout>
          }
        />
        <Route
          path="/settings"
          element={
            <Layout theme={settings.theme} onThemeToggle={handleThemeToggle}>
              <Settings
                settings={settings}
                onSettingsChange={handleSettingsChange}
                onClearData={handleClearData}
              />
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}