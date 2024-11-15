import { useState, useEffect } from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown } from "lucide-react";
import { Release, formatDate } from "../../lib/utils";

export type FilterPeriod = "all" | number;

interface ReleaseListProps {
  releases: Release[];
  onLoadMore?: () => void;
  hasMore?: boolean;
  artistColors: Record<string, number>;
  filterPeriod: FilterPeriod;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ReleaseFilter({ value, onChange, className }: { 
  value: FilterPeriod; 
  onChange: (value: FilterPeriod) => void;
  className?: string;
}) {
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  useEffect(() => {
    async function checkAvailableYears() {
      const currentYear = new Date().getFullYear();
      const years: number[] = [];
      
      for (let year = 2020; year <= currentYear; year++) {
        try {
          const response = await fetch(`/config/notified${year}.json`);
          if (response.ok) {
            years.push(year);
          }
        } catch (error) {
          console.error(`Error checking year ${year}:`, error);
        }
      }
      
      setAvailableYears(years.sort((a, b) => b - a));
    }

    checkAvailableYears();
  }, []);

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger className={`flex items-center gap-1 rounded-lg bg-card px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent ${className}`}>
        {value === "all" ? "All Time" : `${value}`}
        <ChevronDown className="h-4 w-4" />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[8rem] rounded-lg bg-popover p-1 shadow-md"
          sideOffset={5}
        >
          <DropdownMenu.Item
            className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
            onSelect={() => onChange("all")}
          >
            All Time
          </DropdownMenu.Item>
          {availableYears.map((year) => (
            <DropdownMenu.Item
              key={year}
              className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
              onSelect={() => onChange(year)}
            >
              {year}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}

export function ReleaseList({ releases, onLoadMore, hasMore = false, artistColors, filterPeriod }: ReleaseListProps) {
  const filterReleases = (releases: Release[], period: FilterPeriod) => {
    if (period === "all") return releases;

    const year = period as number;
    return releases.filter((release) => {
      const releaseDate = new Date(release.releaseDate);
      return releaseDate.getFullYear() === year;
    });
  };

  const filteredReleases = filterReleases(releases, filterPeriod);

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {filteredReleases.map((release) => {
          const artistColor = artistColors[release.artist];
          const borderColor = artistColor ? numberToHex(artistColor) : '#e2e8f0';
          
          return (
            <div
              key={release.id}
              className="relative rounded-lg bg-card p-4 shadow transition-shadow hover:shadow-md"
              style={{
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: `${borderColor}80`
              }}
            >
              <time className="text-sm text-muted-foreground">
                {formatDate(release.releaseDate)}
              </time>
              <h3 className="mt-1 font-medium">{release.title}</h3>
              <p className="text-sm text-muted-foreground">{release.artist}</p>
            </div>
          );
        })}
      </div>

      {filteredReleases.length === 0 && (
        <div className="flex min-h-[200px] items-center justify-center rounded-lg border border-dashed">
          <p className="text-muted-foreground">No releases found</p>
        </div>
      )}

      {hasMore && (
        <div className="flex justify-center">
          <button
            onClick={onLoadMore}
            className="rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}