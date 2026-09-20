import { apiRequest } from './client';

export interface TimelineStep {
  app_id: string;
  step_id: string;
  parent_step_id: string | null;
  step_type: string;
  input_text: string | null;
  reasoning: string | null;
  code_snapshot: string | null;
  code_diff: string | null;
  latency_ms: number | null;
  token_usage: number | null;
  status: string;
  error_message: string | null;
  created_at: string;
}

export const getTimeline = (appId: string) =>
  apiRequest<{ app_id: string; step_count: number; steps: TimelineStep[] }>(
    `/apps/${appId}/timeline`
  );

export const getTimelineStep = (appId: string, stepId: string) =>
  apiRequest<TimelineStep>(
    `/apps/${appId}/timeline/${stepId}`
  );

export const revertToStep = (appId: string, stepId: string) =>
  apiRequest<{
    app_id: string;
    reverted_to_step: string;
    revert_step_id: string;
    live_url: string;
    status: string;
  }>(`/apps/${appId}/revert/${stepId}`, { method: 'POST' });
