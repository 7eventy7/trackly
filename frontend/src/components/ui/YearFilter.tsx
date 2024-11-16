import React, { useState, useEffect } from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown } from "lucide-react";

export type FilterPeriod = "all" | number;

interface YearFilterProps {
  value: FilterPeriod;
  onChange: (value: FilterPeriod) => void;
  availableYears?: number[];
  className?: string;
  checkYearsFromFiles?: boolean;
}

export function YearFilter({ 
  value, 
  onChange, 
  availableYears: propAvailableYears,
  className,
  checkYearsFromFiles = false 
}: YearFilterProps) {
  const [availableYears, setAvailableYears] = useState<number[]>(propAvailableYears || []);
  const [loading, setLoading] = useState(checkYearsFromFiles);

  useEffect(() => {
    if (propAvailableYears) {
      setAvailableYears(propAvailableYears);
      return;
    }

    if (!checkYearsFromFiles) return;

    async function checkAvailableYears() {
      try {
        setLoading(true);
        const years: number[] = [];
        const yearChecks: Promise<void>[] = [];
        
        const checkYear = async (year: number) => {
          try {
            const response = await fetch(`/data/notified_${year}.json`);
            if (response.ok) {
              years.push(year);
            }
          } catch {}
        };

        const currentYear = new Date().getFullYear();
        const futureYears = 10;
        const pastYears = 10;

        for (let year = currentYear; year <= currentYear + futureYears; year++) {
          yearChecks.push(checkYear(year));
        }

        for (let year = currentYear - 1; year >= currentYear - pastYears; year--) {
          yearChecks.push(checkYear(year));
        }

        await Promise.all(yearChecks);

        if (years.length > 0) {
          const minYear = Math.min(...years);
          const maxYear = Math.max(...years);

          const earlierChecks = [];
          for (let year = minYear - 1; year >= minYear - 5; year--) {
            earlierChecks.push(checkYear(year));
          }

          const laterChecks = [];
          for (let year = maxYear + 1; year <= maxYear + 5; year++) {
            laterChecks.push(checkYear(year));
          }

          await Promise.all([...earlierChecks, ...laterChecks]);
        }
        
        setAvailableYears(years.sort((a, b) => b - a));
      } catch (error) {
        console.error("Error checking available years:", error);
      } finally {
        setLoading(false);
      }
    }

    checkAvailableYears();
  }, [checkYearsFromFiles, propAvailableYears]);

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger 
        className={`flex items-center gap-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${className}`}
        disabled={loading}
      >
        {loading ? (
          "Loading years..."
        ) : (
          <>
            {value === "all" ? "All Time" : `${value}`}
            <ChevronDown className="h-4 w-4" />
          </>
        )}
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="z-[60] min-w-[8rem] rounded-lg bg-popover p-1 shadow-md"
          sideOffset={5}
          align="end"
          alignOffset={-5}
        >
          <DropdownMenu.Item
            className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
            onSelect={() => onChange("all")}
          >
            All Time
          </DropdownMenu.Item>
          {availableYears.map((year) => (
            <DropdownMenu.Item
              key={year}
              className="relative flex cursor-pointer select-none items-center rounded-md px-6 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
              onSelect={() => onChange(year)}
            >
              {year}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}