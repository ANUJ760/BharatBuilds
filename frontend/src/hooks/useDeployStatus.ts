import { useState, useEffect, useRef } from 'react';
import { apiDeployStatus } from '../api/client';

export function useDeployStatus(appId: string | undefined) {
  const [status, setStatus] = useState<'pending' | 'building' | 'deployed' | 'failed' | null>(null);
  const [liveUrl, setLiveUrl] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!appId) return;

    let mounted = true;

    const poll = async () => {
      try {
        const data = await apiDeployStatus(appId);
        if (!mounted) return;

        setStatus(data.status as any);
        if (data.live_url) {
          setLiveUrl(data.live_url);
        }

        if (data.status === 'deployed' || data.status === 'failed') {
          setIsPolling(false);
          if (pollingRef.current) clearTimeout(pollingRef.current);
        } else {
          setIsPolling(true);
          pollingRef.current = setTimeout(poll, 3000); // Poll every 3s
        }
      } catch (err) {
        console.error('Failed to poll status', err);
        // Retry polling on error
        if (mounted) {
          pollingRef.current = setTimeout(poll, 5000);
        }
      }
    };

    poll();

    return () => {
      mounted = false;
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, [appId]);

  return { status, liveUrl, isPolling };
}
