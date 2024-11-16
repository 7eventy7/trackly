import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { Album, Grid, Settings as SettingsIcon, Moon, Sun } from "lucide-react";
import { cn } from "../../lib/utils";

interface LayoutProps {
  children: ReactNode;
  theme: "light" | "dark";
  onThemeToggle: () => void;
  headerExtra?: ReactNode;
}

export function Layout({ children, theme, onThemeToggle, headerExtra }: LayoutProps) {
  const location = useLocation();

  const navigation = [
    {
      name: "Tracked Artists",
      path: "/artists",
      icon: Grid,
    },
    {
      name: "New Releases",
      path: "/releases",
      icon: Album,
    },
    {
      name: "Settings",
      path: "/settings",
      icon: SettingsIcon,
    },
  ];

  const getCurrentPageTitle = () => {
    const currentRoute = navigation.find((item) => item.path === location.pathname);
    return currentRoute?.name || "Trackly";
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="fixed bottom-0 left-0 top-0 z-20 w-64 border-r bg-card px-3 py-4 lg:relative">
        <div className="mb-8 flex items-center gap-2 px-3">
          <img src="/icons/trackly.png" alt="Trackly" className="h-8 w-8" />
          <span className="text-xl font-bold text-primary">Trackly</span>
        </div>

        <nav className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? theme === "dark"
                      ? "bg-primary/20 text-primary"
                      : "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-16 items-center justify-between px-6">
            <div className="flex items-center gap-6">
              <h1 className="text-xl font-semibold text-primary">{getCurrentPageTitle()}</h1>
              <div className="relative">
                {headerExtra}
              </div>
            </div>
            <button
              onClick={onThemeToggle}
              className="rounded-lg p-2 hover:bg-accent"
              aria-label="Toggle theme"
            >
              {theme === "light" ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}