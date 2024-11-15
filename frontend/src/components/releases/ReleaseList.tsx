import { useState } from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown } from "lucide-react";
import { Release, formatDate } from "../../lib/utils";

type FilterPeriod = "week" | "month" | "year" | "all";

interface ReleaseListProps {
  releases: Release[];
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export function ReleaseList({ releases, onLoadMore, hasMore = false }: ReleaseListProps) {
  const [filterPeriod, setFilterPeriod] = useState<FilterPeriod>("all");

  const filterReleases = (releases: Release[], period: FilterPeriod) => {
    const now = new Date();
    const msInDay = 86400000;
    const msInWeek = msInDay * 7;
    const msInMonth = msInDay * 30;
    const msInYear = msInDay * 365;

    return releases.filter((release) => {
      const releaseDate = new Date(release.releaseDate);
      const timeDiff = now.getTime() - releaseDate.getTime();

      switch (period) {
        case "week":
          return timeDiff <= msInWeek;
        case "month":
          return timeDiff <= msInMonth;
        case "year":
          return timeDiff <= msInYear;
        default:
          return true;
      }
    });
  };

  const isRecent = (date: string) => {
    const releaseDate = new Date(date);
    const now = new Date();
    const timeDiff = now.getTime() - releaseDate.getTime();
    return timeDiff <= 7 * 24 * 60 * 60 * 1000; // 7 days
  };

  const filteredReleases = filterReleases(releases, filterPeriod);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger className="flex items-center gap-1 rounded-lg bg-card px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent">
            {filterPeriod === "all" ? "All Time" : `Last ${filterPeriod}`}
            <ChevronDown className="h-4 w-4" />
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="min-w-[8rem] rounded-lg bg-popover p-1 shadow-md"
              sideOffset={5}
            >
              <DropdownMenu.Item
                className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
                onSelect={() => setFilterPeriod("all")}
              >
                All Time
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
                onSelect={() => setFilterPeriod("week")}
              >
                Last Week
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
                onSelect={() => setFilterPeriod("month")}
              >
                Last Month
              </DropdownMenu.Item>
              <DropdownMenu.Item
                className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
                onSelect={() => setFilterPeriod("year")}
              >
                Last Year
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredReleases.map((release) => (
          <div
            key={release.id}
            className="relative rounded-lg bg-card p-4 shadow transition-shadow hover:shadow-md"
          >
            {isRecent(release.releaseDate) && (
              <div className="absolute -right-1 -top-1 rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
                New
              </div>
            )}
            <time className="text-sm text-muted-foreground">
              {formatDate(release.releaseDate)}
            </time>
            <h3 className="mt-1 font-medium">{release.title}</h3>
            <p className="text-sm text-muted-foreground">{release.artist}</p>
          </div>
        ))}
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