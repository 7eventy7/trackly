import { useState, CSSProperties } from "react";
import { Link } from "react-router-dom";
import { FALLBACK_COVER, cn } from "../../lib/utils";

interface ArtistCardProps {
  name: string;
  coverImage: string;
  className?: string;
  color?: number;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ArtistCard({ name, coverImage, className, color }: ArtistCardProps) {
  const [imageError, setImageError] = useState(false);
  const imageSrc = imageError ? FALLBACK_COVER : coverImage;
  const colorHex = color ? numberToHex(color) : '#000000';

  const gradientStyle: CSSProperties = {
    background: `linear-gradient(to top, ${colorHex}cc, transparent)`,
    paddingBottom: '1.5rem'
  };

  const borderStyle: CSSProperties = {
    borderColor: `${colorHex}1a`
  };

  return (
    <Link
      to={`/artists/${encodeURIComponent(name)}`}
      className={cn(
        "group relative block overflow-hidden rounded-lg bg-card transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
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
      <div 
        className="absolute inset-x-0 bottom-0 p-4"
        style={gradientStyle}
      >
        <h3 className="text-center text-lg font-medium text-white drop-shadow-md">
          {name}
        </h3>
      </div>
      <div 
        className="absolute inset-0 rounded-lg ring-1 ring-inset"
        style={borderStyle}
      />
    </Link>
  );
}