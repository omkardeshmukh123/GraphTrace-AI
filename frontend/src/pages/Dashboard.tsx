import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { ProjectSummary } from '../api';
import { nodeColor } from '../nodeColors';

export default function Dashboard() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!projectId) return;
    api.getProject(projectId)
      .then(setProject)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <div className="page-content"><div className="loading"><div className="spinner" /> Loading…</div></div>;
  if (error) return <div className="page-content"><div className="error-box">⚠ {error}</div></div>;
  if (!project) return null;

  const totalCount = Object.values(project.counts).reduce((a, b) => a + b, 0);
  const sortedTypes = Object.entries(project.counts).sort(([, a], [, b]) => b - a);

  return (
    <div className="page-content">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <h1 className="page-title">📦 {project.name}</h1>
            <p className="page-subtitle" style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{project.id}</p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost" onClick={() => navigate('/')}>← Projects</button>
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/projects/${projectId}/graph`)}
            >
              🔭 Explore Graph
            </button>
          </div>
        </div>
      </div>

      {/* Top stats */}
      <div className="stat-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-label">Nodes</div>
          <div className="stat-value">{project.node_count.toLocaleString()}</div>
          <div className="stat-sub">Entities in the graph</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Relationships</div>
          <div className="stat-value">{project.relationship_count.toLocaleString()}</div>
          <div className="stat-sub">Edges in the graph</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Node types</div>
          <div className="stat-value">{sortedTypes.length}</div>
          <div className="stat-sub">Distinct entity types</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Source</div>
          <div className="stat-value" style={{ fontSize: 16, paddingTop: 6 }}>{project.source}</div>
          <div className="stat-sub">Ingestion method</div>
        </div>
      </div>

      {/* Type breakdown */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="section-header" style={{ marginBottom: 12 }}>
            <span className="section-title">Node Types</span>
          </div>
          <div className="type-list">
            {sortedTypes.map(([type, count]) => {
              const pct = totalCount > 0 ? (count / totalCount) * 100 : 0;
              const color = nodeColor(type);
              return (
                <div key={type} className="type-row">
                  <div className="type-dot" style={{ background: color }} />
                  <div className="type-name">{type}</div>
                  <div className="type-bar-wrap">
                    <div className="type-bar" style={{ width: `${pct}%`, background: color }} />
                  </div>
                  <div className="type-count">{count}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="section-title">Quick Actions</div>
          <button
            className="btn btn-primary"
            style={{ justifyContent: 'center', padding: '12px' }}
            onClick={() => navigate(`/projects/${projectId}/graph`)}
          >
            🔭 Open Graph Explorer
          </button>
          <button
            className="btn btn-ghost"
            style={{ justifyContent: 'center', padding: '12px' }}
            onClick={() => navigate(`/projects/${projectId}/graph?nodeType=REQUIREMENT`)}
          >
            📋 Browse Requirements
          </button>
          <button
            className="btn btn-ghost"
            style={{ justifyContent: 'center', padding: '12px' }}
            onClick={() => navigate(`/projects/${projectId}/graph?nodeType=CLASS`)}
          >
            🧩 Browse Classes
          </button>

          <div className="divider" />
          <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.7 }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Next steps</strong><br/>
            Click "Explore Graph" to see all entities and their relationships.
            Click any node to see its connections and properties.
          </div>
        </div>
      </div>
    </div>
  );
}
