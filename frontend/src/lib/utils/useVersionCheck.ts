import { useState, useEffect } from 'react';
import { APP_VERSION } from './config';

type VersionStatus = {
  emoji: string;
  tooltip: string;
};

export function useVersionCheck(): VersionStatus {
  const [status, setStatus] = useState<VersionStatus>({
    emoji: '⏳',
    tooltip: 'Checking version...'
  });

  useEffect(() => {
    const checkVersion = async () => {
      try {
        const response = await fetch('https://api.github.com/repos/7eventy7/trackly/releases/latest');
        
        if (!response.ok) {
          throw new Error('Failed to fetch latest version');
        }
        
        const data = await response.json();
        const latestVersion = data.tag_name.replace('v', '');
        
        const current = APP_VERSION.split('.').map(Number);
        const latest = latestVersion.split('.').map(Number);
        
        for (let i = 0; i < 3; i++) {
          if (current[i] > latest[i]) {
            setStatus({
              emoji: '⚠️',
              tooltip: `You are ahead of the latest release (${latestVersion})`
            });
            return;
          }
          if (current[i] < latest[i]) {
            setStatus({
              emoji: '❌',
              tooltip: `Update available! Latest version: ${latestVersion}`
            });
            return;
          }
        }
        
        setStatus({
          emoji: '✅',
          tooltip: 'You are up to date!'
        });
      } catch (error) {
        console.error('Version check error:', error);
        setStatus({
          emoji: '⚠️',
          tooltip: 'Failed to check version'
        });
      }
    };

    checkVersion();
  }, []);

  return status;
}