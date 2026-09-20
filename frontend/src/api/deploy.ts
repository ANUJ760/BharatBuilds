import { apiRequest } from './client';

export const deployApp = (appId: string, data: {
  prompt: string;
  owner_id: string;
  title?: string;
  clarifications?: Record<string, string>;
}) =>
  apiRequest<{ app_id: string; live_url: string; status: string; steps_logged: number }>(
    `/deploy/${appId}`,
    { method: 'POST', body: JSON.stringify(data) }
  );

export const getDeployStatus = (appId: string) =>
  apiRequest<{ app_id: string; status: string; live_url: string | null }>(
    `/deploy/${appId}/status`
  );
