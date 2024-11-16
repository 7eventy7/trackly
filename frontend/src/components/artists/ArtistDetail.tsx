import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronLeft, ChevronDown } from "lucide-react";
import { Artist, FALLBACK_BACKDROP, formatDate } from "../../lib/utils";

interface ArtistDetailProps {
  artist: Artist;
  availableYears: number[];
  selectedYear: number;
  onYearChange: (year: number) => void;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ArtistDetail({
  artist,
  availableYears,
  selectedYear,
  onYearChange,
}: ArtistDetailProps) {
  const [backdropError, setBackdropError] = useState(false);
  const [coverError, setCoverError] = useState(false);

  const backdropSrc = backdropError ? FALLBACK_BACKDROP : `/music/${encodeURIComponent(artist.name)}/backdrop.png`;
  const coverSrc = coverError 
    ? (artist.fallbackImage || '/icons/trackly.png')
    : `/music/${encodeURIComponent(artist.name)}/cover.png`;
  const colorHex = artist.color ? numberToHex(artist.color) : '#000000';

  // Filter releases for the selected year
  const filteredReleases = useMemo(() => {
    return artist.releases.filter(release => {
      const releaseYear = new Date(release.releaseDate).getFullYear();
      return releaseYear === selectedYear;
    });
  }, [artist.releases, selectedYear]);

  // Sort releases by date (newest first)
  const sortedReleases = useMemo(() => {
    return [...filteredReleases].sort(
      (a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime()
    );
  }, [filteredReleases]);

  return (
    <div className="min-h-screen">
      {/* Backdrop Container - Modified to handle overflow properly */}
      <div className="relative mx-auto" style={{ maxWidth: '622px' }}>
        {/* Backdrop Image Container */}
        <div className="h-[350px] overflow-hidden rounded-lg">
          <img
            src={backdropSrc}
            alt={`${artist.name}'s backdrop`}
            onError={() => setBackdropError(true)}
            className="h-full w-full object-cover"
          />
          <div 
            className="absolute inset-0"
            style={{
              background: `linear-gradient(to bottom, transparent 50%, var(--background) 100%),
                          linear-gradient(to right, var(--background) 0%, transparent 15%),
                          linear-gradient(to left, var(--background) 0%, transparent 15%)`
            }}
          />
        </div>

        {/* Navigation and Year Selection - Adjusted positioning */}
        <div className="absolute left-4 top-4">
          <Link
            to="/artists"
            className="flex items-center gap-1 rounded-lg bg-background/80 px-4 py-2 text-sm font-medium backdrop-blur-sm transition-colors hover:bg-background/90"
          >
            <ChevronLeft className="h-4 w-4" />
            Back
          </Link>
        </div>

        <div className="absolute right-4 top-4">
          <DropdownMenu.Root>
            <DropdownMenu.Trigger className="flex items-center gap-1 rounded-lg bg-background/80 px-4 py-2 text-sm font-medium backdrop-blur-sm transition-colors hover:bg-background/90">
              {selectedYear}
              <ChevronDown className="h-4 w-4" />
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content
                className="min-w-[8rem] rounded-lg bg-popover p-1 shadow-md"
                sideOffset={5}
              >
                {availableYears.map((year) => (
                  <DropdownMenu.Item
                    key={year}
                    className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
                    onSelect={() => onYearChange(year)}
                  >
                    {year}
                  </DropdownMenu.Item>
                ))}
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </div>

        {/* Profile Picture Container - Improved positioning */}
        <div className="absolute left-1/2 -translate-x-1/2" style={{ bottom: '-64px' }}>
          <div 
            className="relative h-32 w-32 overflow-hidden rounded-full border-4 shadow-lg"
            style={{ borderColor: colorHex }}
          >
            <img
              src={coverSrc}
              alt={`${artist.name}'s cover`}
              onError={() => setCoverError(true)}
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </div>

      {/* Content Section - Adjusted spacing to accommodate profile picture */}
      <div className="mt-24 text-center">
        <h1 className="text-3xl font-bold">{artist.name}</h1>
      </div>

      <div className="mx-auto mt-8 max-w-5xl px-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sortedReleases.map((release) => (
            <div
              key={release.id}
              className="rounded-lg p-4 shadow transition-shadow hover:shadow-md"
              style={{
                backgroundColor: `${colorHex}11`,
                borderColor: `${colorHex}22`,
                borderWidth: '1px'
              }}
            >
              <time className="text-sm text-muted-foreground">
                {formatDate(release.releaseDate)}
              </time>
              <h3 className="mt-1 font-medium">{release.title}</h3>
            </div>
          ))}
        </div>

        {sortedReleases.length === 0 && (
          <div className="flex min-h-[200px] items-center justify-center rounded-lg border border-dashed">
            <p className="text-muted-foreground">No releases found for {selectedYear}</p>
          </div>
        )}
      </div>
    </div>
  );
}