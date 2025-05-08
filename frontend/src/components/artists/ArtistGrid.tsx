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

  const sortedArtists = [...artists].sort((a, b) => 
    a.name.localeCompare(b.name)
  );

  return (
    <div className="space-y-6">
      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: calculateGridColumns(itemsPerRow),
        }}
      >
        {sortedArtists.map((artist) => (
          <ArtistCard
            key={artist.name}
            name={artist.name}
            cover={artist.cover || '/icons/trackly.png'}
            color={artist.color}
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
