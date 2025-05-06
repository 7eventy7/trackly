import { useState, CSSProperties } from "react";
import { Link } from "react-router-dom";
import { cn } from "../../lib/utils";

interface ArtistCardProps {
  name: string;
  cover: string;
  className?: string;
  color?: number;
}

function numberToHex(num: number): string {
  return `#${num.toString(16).padStart(6, '0')}`;
}

export function ArtistCard({ name, cover, className, color }: ArtistCardProps) {
  const [imageError, setImageError] = useState(false);

  const imageSrc = imageError || !cover ? '/icons/trackly.png' : cover;

  const colorHex = color ? numberToHex(color) : '#000000';
  
  const gradientStyle: CSSProperties = {
    background: `linear-gradient(to top, ${colorHex}ff, ${colorHex}00 70%)`,
    transition: 'background 0.3s ease-in-out',
    paddingBottom: '0.75rem'
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
          onError={() => setImageError(true)}
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
