// ── Central API client ──────────────────────────────────────────────────────
// All backend calls go through here so auth headers are always injected.
// The Vite proxy forwards /apps /deploy /share to http://127.0.0.1:8000

const BASE = '';          // Vite proxy handles this
const API_URL = BASE;

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
if (isLocalhost) {
  // Force login on every hard refresh during dev by clearing storage on initial load
  localStorage.removeItem('bb_token');
  localStorage.removeItem('bb_user');
  sessionStorage.removeItem('bb_token');
  sessionStorage.removeItem('bb_user');
}

function getToken(): string | null {
  return localStorage.getItem('bb_token') || sessionStorage.getItem('bb_token');
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders?: Record<string, string>,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  };

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let msg = `API error ${res.status}`;
    try {
      const err = await res.json();
      msg = err.message || err.detail || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

// ── Apps ─────────────────────────────────────────────────────────────────────
export interface ClarifyResponse {
  questions: Array<{ id: string; text: string; options: string[]; default: string }>;
  needs_clarification: boolean;
}

export async function apiClarify(prompt: string): Promise<ClarifyResponse> {
  return request('POST', '/apps/clarify', { prompt });
}

export interface CreateAppResponse {
  app_id: string;
  owner_id: string;
  title: string;
  prompt: string;
  status: string;
}

export async function apiCreateApp(
  prompt: string,
  owner_id: string,
  title = '',
): Promise<CreateAppResponse> {
  return request('POST', '/apps/', { prompt, owner_id, title });
}

export async function apiGetApp(appId: string) {
  return request('GET', `/apps/${appId}`);
}

export async function apiListApps(ownerId: string) {
  return request<{ apps: any[] }>('GET', `/apps/?owner_id=${ownerId}`);
}

export async function apiDeleteApp(appId: string) {
  return request('DELETE', `/apps/${appId}`);
}

export async function apiUpdateApp(appId: string, title: string) {
  return request('PUT', `/apps/${appId}`, { title });
}

// ── Deploy ────────────────────────────────────────────────────────────────────
export interface DeployResponse {
  app_id: string;
  live_url: string;
  status: string;
  steps_logged: number;
}

export async function apiDeploy(
  appId: string,
  prompt: string,
  owner_id: string,
  title = '',
  clarifications: Record<string, string> | null = null,
): Promise<DeployResponse> {
  return request('POST', `/deploy/${appId}`, {
    prompt,
    owner_id,
    title,
    clarifications,
  });
}

export async function apiDeployStatus(appId: string) {
  return request<{ app_id: string; status: string; live_url: string | null }>(
    'GET',
    `/deploy/${appId}/status`,
  );
}

// ── Timeline ──────────────────────────────────────────────────────────────────
export async function apiGetTimeline(appId: string) {
  return request<{ steps: any[] }>('GET', `/apps/${appId}/timeline`);
}

// ── Share ─────────────────────────────────────────────────────────────────────
export async function apiInvite(appId: string, email: string, role = 'viewer') {
  return request('POST', `/apps/${appId}/invite`, { email, role });
}

export async function apiListCollaborators(appId: string) {
  return request<{ collaborators: any[] }>('GET', `/apps/${appId}/collaborators`);
}

export async function apiRemoveCollaborator(appId: string, email: string) {
  return request('DELETE', `/apps/${appId}/collaborators/${email}`);
}

export async function apiUpdateCollaboratorRole(appId: string, email: string, role: string) {
  return request('PUT', `/apps/${appId}/collaborators/${email}`, { role });
}

// ── Health ────────────────────────────────────────────────────────────────────
export async function apiHealth() {
  return request<{ status: string }>('GET', '/health');
}
