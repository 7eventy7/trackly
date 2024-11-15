import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { Moon, Sun, Trash2 } from "lucide-react";
import { Settings as SettingsType } from "../../lib/utils";

interface SettingsProps {
  settings: SettingsType;
  onSettingsChange: (settings: Partial<SettingsType>) => void;
  onClearData: () => void;
}

export function Settings({ settings, onSettingsChange, onClearData }: SettingsProps) {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState("");

  const handleThemeToggle = () => {
    const newTheme = settings.theme === "light" ? "dark" : "light";
    onSettingsChange({ theme: newTheme });
    document.documentElement.classList.toggle("dark");
  };

  const handleClearData = () => {
    if (deleteConfirmation === "DELETE") {
      onClearData();
      setIsDeleteDialogOpen(false);
      setDeleteConfirmation("");
    }
  };

  return (
    <div className="space-y-8">
      <div className="settings-section">
        <h3 className="settings-title">Theme</h3>
        <div className="mt-4 flex items-center gap-4">
          <button
            onClick={handleThemeToggle}
            className="flex items-center gap-2 rounded-lg bg-card px-4 py-2 shadow-sm transition-colors hover:bg-accent"
          >
            {settings.theme === "light" ? (
              <>
                <Sun className="h-4 w-4" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon className="h-4 w-4" />
                <span>Dark</span>
              </>
            )}
          </button>
          <div className="text-sm text-muted-foreground">
            Current theme: {settings.theme}
          </div>
        </div>
      </div>

      <div className="settings-section">
        <h3 className="settings-title">Data Management</h3>
        <div className="mt-4">
          <Dialog.Root open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
            <Dialog.Trigger asChild>
              <button className="flex items-center gap-2 rounded-lg bg-destructive px-4 py-2 text-destructive-foreground shadow-sm transition-colors hover:bg-destructive/90">
                <Trash2 className="h-4 w-4" />
                Clear Data
              </button>
            </Dialog.Trigger>
            <Dialog.Portal>
              <Dialog.Overlay className="fixed inset-0 bg-black/50" />
              <Dialog.Content className="confirmation-dialog">
                <div className="dialog-content">
                  <Dialog.Title className="dialog-title">
                    Clear All Data
                  </Dialog.Title>
                  <Dialog.Description className="dialog-description">
                    This action will remove all release history. Type 'DELETE' to confirm.
                  </Dialog.Description>
                  <input
                    type="text"
                    value={deleteConfirmation}
                    onChange={(e) => setDeleteConfirmation(e.target.value)}
                    className="dialog-input rounded-md border bg-transparent px-3 py-2"
                    placeholder="Type DELETE"
                  />
                  <div className="dialog-buttons">
                    <button
                      onClick={() => setIsDeleteDialogOpen(false)}
                      className="rounded-lg bg-secondary px-4 py-2 font-medium transition-colors hover:bg-secondary/80"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleClearData}
                      disabled={deleteConfirmation !== "DELETE"}
                      className="rounded-lg bg-destructive px-4 py-2 font-medium text-destructive-foreground transition-colors hover:bg-destructive/90 disabled:opacity-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </Dialog.Content>
            </Dialog.Portal>
          </Dialog.Root>
        </div>
      </div>
    </div>
  );
}