import { useState } from "react";
import { Link } from "react-router-dom";
import { FALLBACK_COVER, cn } from "../../lib/utils";

interface ArtistCardProps {
  name: string;
  coverImage: string;
  className?: string;
}

export function ArtistCard({ name, coverImage, className }: ArtistCardProps) {
  const [imageError, setImageError] = useState(false);
  const imageSrc = imageError ? FALLBACK_COVER : coverImage;

  return (
    <Link
      to={`/artists/${encodeURIComponent(name)}`}
      className={cn(
        "group relative block overflow-hidden rounded-lg bg-card transition-all hover:scale-102 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
        className
      )}
    >
      <div className="aspect-square w-full overflow-hidden">
        <img
          src={imageSrc}
          alt={`${name}'s cover`}
          onError={() => setImageError(true)}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-4">
        <h3 className="text-center text-lg font-medium text-white">{name}</h3>
      </div>
      <div className="absolute inset-0 rounded-lg ring-1 ring-inset ring-black/10" />
    </Link>
  );
}