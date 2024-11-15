import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/ui/Layout";
import { ArtistGrid } from "./components/artists/ArtistGrid";
import { ArtistDetail } from "./components/artists/ArtistDetail";
import { ReleaseList } from "./components/releases/ReleaseList";
import { Settings } from "./components/settings/Settings";
import { Artist, Release, Settings as SettingsType, DEFAULT_SETTINGS } from "./lib/utils";

export default function App() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [settings, setSettings] = useState<SettingsType>(() => {
    const saved = localStorage.getItem("trackly-settings");
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

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
    // You might want to clear other data as well
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
            element={
              <ArtistDetail
                artist={artists[0]} // This should be looked up by name
                availableYears={[2024, 2023, 2022]} // This should be computed from actual data
                selectedYear={2024}
                onYearChange={() => {}} // This should be implemented
              />
            }
          />
          <Route
            path="/releases"
            element={
              <ReleaseList
                releases={sortedReleases}
                hasMore={false}
                onLoadMore={() => {}} // Implement if needed
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