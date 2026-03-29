/**
 * Typed API client — uses /api proxy via Next.js rewrites.
 * No NEXT_PUBLIC_ environment variables needed.
 */
const API_BASE = '';

export async function apiCall<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => apiCall<T>('GET', path),
  post: <T>(path: string, body: unknown) => apiCall<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => apiCall<T>('PUT', path, body),
  delete: <T>(path: string) => apiCall<T>('DELETE', path),
};
