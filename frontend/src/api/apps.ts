import { apiRequest } from './client';

export interface ClarifyResponse {
  needs_clarification: boolean;
  questions: Array<{
    question: string;
    suggested_default: string;
    why_it_matters: string;
  }>;
}

export const clarifyPrompt = (prompt: string) =>
  apiRequest<ClarifyResponse>('/apps/clarify', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
  });

export const createApp = (data: { prompt: string; owner_id: string; title?: string }) =>
  apiRequest<{ app_id: string; owner_id: string; title: string; prompt: string; status: string }>('/apps/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const getApp = (appId: string) =>
  apiRequest<any>(`/apps/${appId}`);

export const listApps = () =>
  apiRequest<{ apps: any[] }>('/apps/');
