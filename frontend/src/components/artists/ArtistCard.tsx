import { useState, CSSProperties } from "react";
import { Link } from "react-router-dom";
import { cn } from "../../lib/utils";

interface ArtistCardProps {
  name: string;
  coverImage: string;
  fallbackImage?: string;
  className?: string;
  color?: number;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ArtistCard({ name, coverImage, fallbackImage, className, color }: ArtistCardProps) {
  const [localImageError, setLocalImageError] = useState(false);
  const [fallbackImageError, setFallbackImageError] = useState(false);

  // Determine which image source to use
  const imageSrc = localImageError 
    ? (fallbackImage && !fallbackImageError ? fallbackImage : '/icons/trackly.png')
    : `/music/${encodeURIComponent(name)}/cover.png`;

  const colorHex = color ? numberToHex(color) : '#000000';

  const gradientStyle: CSSProperties = {
    background: `linear-gradient(to top, ${colorHex}cc, transparent)`,
    paddingBottom: '2rem' // Increased padding to move name down
  };

  const borderStyle: CSSProperties = {
    borderColor: colorHex // Using the full color instead of semi-transparent
  };

  const handleImageError = () => {
    if (!localImageError) {
      // First error - try fallback image
      setLocalImageError(true);
    } else if (!fallbackImageError && fallbackImage) {
      // Second error - mark fallback as failed too
      setFallbackImageError(true);
    }
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
          onError={handleImageError}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <div 
        className="absolute inset-x-0 bottom-0 p-4"
        style={gradientStyle}
      >
        <h3 className="text-center text-lg font-medium text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.5)]">
          {name}
        </h3>
      </div>
      <div 
        className="absolute inset-0 rounded-lg ring-2 ring-inset"
        style={borderStyle}
      />
    </Link>
  );
}