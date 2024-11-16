import React from "react";
import { YearFilter, FilterPeriod } from "../ui/YearFilter";
import { Release, formatDate } from "../../lib/utils";

interface ReleaseListProps {
  releases: Release[];
  onLoadMore?: () => void;
  hasMore?: boolean;
  artistColors: Record<string, number>;
  filterPeriod: FilterPeriod;
  onFilterChange: (value: FilterPeriod) => void;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ReleaseList({ 
  releases, 
  onLoadMore, 
  hasMore = false, 
  artistColors, 
  filterPeriod,
  onFilterChange 
}: ReleaseListProps) {
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