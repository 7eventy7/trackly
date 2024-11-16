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
    background: `linear-gradient(to top, ${colorHex}ff, ${colorHex}00 70%)`,
    transition: 'background 0.3s ease-in-out',
    paddingBottom: '0.75rem'
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
        "group relative block rounded-lg bg-card transition-all focus:outline-none border-4 z-10",
        className
      )}
      style={{ borderColor: colorHex }}
    >
      <div className="aspect-square w-full">
        <img
          src={imageSrc}
          alt={`${name}'s cover`}
          onError={handleImageError}
          className="h-full w-full object-cover transition-transform duration-300"
        />
      </div>
      <div 
        className="absolute inset-x-0 bottom-0 px-4 pb-3 pt-12 transition-all duration-300 group-hover:pt-24"
        style={gradientStyle}
      >
        <h3 className="text-center text-lg font-bold text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
          {name}
        </h3>
      </div>
    </Link>
  );
}