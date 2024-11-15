import { useEffect, useState } from "react";
import * as Slider from "@radix-ui/react-slider";
import { Artist, calculateGridColumns } from "../../lib/utils";
import { ArtistCard } from "./ArtistCard";

interface ArtistGridProps {
  artists: Artist[];
  defaultItemsPerRow?: number;
  onItemsPerRowChange?: (value: number) => void;
}

export function ArtistGrid({
  artists,
  defaultItemsPerRow = 10,
  onItemsPerRowChange,
}: ArtistGridProps) {
  const [itemsPerRow, setItemsPerRow] = useState(defaultItemsPerRow);

  useEffect(() => {
    setItemsPerRow(defaultItemsPerRow);
  }, [defaultItemsPerRow]);

  const handleSliderChange = (value: number[]) => {
    const newValue = value[0];
    setItemsPerRow(newValue);
    onItemsPerRowChange?.(newValue);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 rounded-lg bg-card p-4">
        <span className="text-sm font-medium">Grid Size:</span>
        <Slider.Root
          className="relative flex h-5 w-[200px] touch-none items-center"
          defaultValue={[itemsPerRow]}
          min={4}
          max={16}
          step={1}
          onValueChange={handleSliderChange}
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
          {itemsPerRow}
        </span>
      </div>

      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: calculateGridColumns(itemsPerRow),
        }}
      >
        {artists.map((artist) => (
          <ArtistCard
            key={artist.name}
            name={artist.name}
            coverImage={artist.coverImage}
          />
        ))}
      </div>

      {artists.length === 0 && (
        <div className="flex min-h-[200px] items-center justify-center rounded-lg border border-dashed">
          <p className="text-muted-foreground">No artists found</p>
        </div>
      )}
    </div>
  );
}