/* ───────────────────────────────────────────────
   GraphTrace AI — API Client
   Typed against M3 REST API specifications
   ─────────────────────────────────────────────── */

const BASE = '/api';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/* ── Shared types (mirrors backend/app/models.py) ── */

export interface ProjectSummary {
  id: string;
  name: string;
  node_count: number;
  relationship_count: number;
  counts: Record<string, number>;
  status?: string;
  source: string;
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties?: Record<string, unknown>;
}

export interface GraphView {
  project_id: string;
  nodes: GraphNode[];
  relationships: GraphEdge[];
}

export interface DependencyView {
  project_id: string;
  root: string;
  direction: 'upstream' | 'downstream';
  nodes: GraphNode[];
  relationships: GraphEdge[];
  distances: Record<string, number>;
  depth_limited: boolean;
}

export interface PathView {
  project_id: string;
  found: boolean;
  node_ids: string[];
  relationships: GraphEdge[];
  max_depth: number;
  directed: boolean;
}

export interface RequirementSummary {
  requirement: GraphNode;
  mapping_status: 'mapped' | 'unmapped';
  implementation_count: number;
}

export interface TraceabilityView {
  project_id: string;
  nodes: GraphNode[];
  relationships: GraphEdge[];
  requirement: GraphNode;
  mapping_status: 'mapped' | 'unmapped';
  implementation_ids: string[];
  evidence_paths: string[][];
  depth_limited: boolean;
  note?: string;
}

/* ── Endpoints ── */

export const api = {
  health: () => req<{ status: string; store: string; parser_configured: boolean }>('/health'),

  listProjects: () => req<ProjectSummary[]>('/projects'),

  getProject: (id: string) => req<ProjectSummary>(`/projects/${id}`),

  analyzeProject: (formData: FormData) =>
    fetch(`${BASE}/projects/analyze`, { method: 'POST', body: formData })
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.error?.message ?? `HTTP ${res.status}`);
        }
        return res.json() as Promise<ProjectSummary>;
      }),

  importProject: (graph: unknown) =>
    req<ProjectSummary>('/projects/import', {
      method: 'POST',
      body: JSON.stringify(graph),
    }),

  getGraph: (
    projectId: string,
    opts?: { nodeTypes?: string[]; search?: string }
  ) => {
    const params = new URLSearchParams();
    opts?.nodeTypes?.forEach((t) => params.append('node_type', t));
    if (opts?.search) params.set('search', opts.search);
    const qs = params.toString() ? `?${params}` : '';
    return req<GraphView>(`/projects/${projectId}/graph${qs}`);
  },

  getDependencies: (
    projectId: string,
    nodeId: string,
    direction: 'upstream' | 'downstream' = 'downstream',
    maxDepth = 3
  ) =>
    req<DependencyView>(
      `/projects/${projectId}/dependencies/${nodeId}?direction=${direction}&max_depth=${maxDepth}`
    ),

  getPaths: (
    projectId: string,
    source: string,
    target: string,
    maxDepth = 6,
    directed = true
  ) =>
    req<PathView>(
      `/projects/${projectId}/paths?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}&max_depth=${maxDepth}&directed=${directed}`
    ),

  getRequirements: (projectId: string) =>
    req<RequirementSummary[]>(`/projects/${projectId}/requirements`),

  getTraceability: (projectId: string, requirementId: string, maxDepth = 5) =>
    req<TraceabilityView>(
      `/projects/${projectId}/traceability/${encodeURIComponent(requirementId)}?max_depth=${maxDepth}`
    ),
};
