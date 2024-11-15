import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function getImageUrl(path: string, fallback: string): string {
  try {
    return new URL(path).toString();
  } catch {
    return fallback;
  }
}

export function calculateGridColumns(itemsPerRow: number): string {
  return `repeat(${Math.max(4, Math.min(16, itemsPerRow))}, minmax(0, 1fr))`;
}

export const FALLBACK_BACKDROP = "/placeholder-backdrop.jpg";

export interface Artist {
  name: string;
  coverImage: string;
  backdropImage: string;
  fallbackImage?: string;
  releases: Release[];
  color: number;
}

export interface Release {
  id: string;
  title: string;
  artist: string;
  releaseDate: string;
}

export interface Settings {
  theme: "light" | "dark";
  itemsPerRow: number;
}

export const DEFAULT_SETTINGS: Settings = {
  theme: "dark",
  itemsPerRow: 9,
};