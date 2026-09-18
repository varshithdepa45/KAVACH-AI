// Optional live-backend client.
//
// The UI runs standalone on the baked mock-data layer (lib/data.ts) so the
// judge demo always works offline. When the FastAPI backend is running, these
// helpers let the same components read live endpoints instead — the contract
// (paths + shapes) is identical, so swapping the source is a one-line change.

const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface HealthResponse {
  status: string;
  mode: string;
  version: string;
}

async function get<T>(path: string, timeoutMs = 2500): Promise<T> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE}${path}`, { signal: ctrl.signal, cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

export const api = {
  base: BASE,
  health: () => get<HealthResponse>("/api/health"),
  systemStatus: () => get<any>("/api/system/status"),
  documents: () => get<any>("/api/documents"),
  models: () => get<any>("/api/models"),
  knowledge: () => get<any>("/api/knowledge"),
  runs: () => get<any>("/api/agents/runs"),
  auditLogs: () => get<any>("/api/audit-logs"),
  deliverables: () => get<any>("/api/deliverables"),
  runDemo: () =>
    fetch(`${BASE}/api/demo/run`, { method: "POST" }).then((r) => r.json()),
};
