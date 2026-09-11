import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { ProjectSummary } from '../api';
import { nodeColor, nodeIcon } from '../nodeColors';

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

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 80, gap: 12, color: 'var(--text-secondary)' }}>
          <div className="spinner" /> Loading project dashboard…
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="page-container">
        <div style={{ padding: 20, background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 12, color: '#fda4af' }}>
          ⚠️ Failed to load project: {error || 'Project not found'}
        </div>
      </div>
    );
  }

  const sortedTypes = Object.entries(project.counts || {}).sort(([, a], [, b]) => b - a);
  const totalCount = sortedTypes.reduce((acc, [, val]) => acc + val, 0);

  // Connectivity metric: edge-to-node ratio
  const connectivityRatio = project.node_count > 0 
    ? (project.relationship_count / project.node_count).toFixed(2) 
    : '0.00';

  return (
    <div className="page-container">
      {/* Top Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 24 }}>📦</span>
            <h1 className="page-title">{project.name}</h1>
            <span style={{ fontSize: 11, fontWeight: 700, background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary-light)', padding: '2px 8px', borderRadius: 999, border: '1px solid rgba(99, 102, 241, 0.3)' }}>
              {project.status || 'Ready'}
            </span>
          </div>
          <p className="page-subtitle" style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
            Project ID: {project.id} &bull; Source: {project.source}
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            ← All Projects
          </button>
          <button
            className="btn btn-primary"
            onClick={() => navigate(`/projects/${projectId}/graph`)}
          >
            <span>🔭</span> Launch Graph Observatory
          </button>
        </div>
      </div>

      {/* Top Stat Grid */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon">🧩</div>
          <div className="stat-label">Software Entities</div>
          <div className="stat-value">{project.node_count.toLocaleString()}</div>
          <div className="stat-desc">Classes, functions, files, packages</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🕸️</div>
          <div className="stat-label">Graph Edges</div>
          <div className="stat-value">{project.relationship_count.toLocaleString()}</div>
          <div className="stat-desc">Calls, defines, imports & traces</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-label">Connectivity Density</div>
          <div className="stat-value">{connectivityRatio}x</div>
          <div className="stat-desc">Average relationships per entity</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-label">Entity Categories</div>
          <div className="stat-value">{sortedTypes.length}</div>
          <div className="stat-desc">Distinct architectural types</div>
        </div>
      </div>

      {/* Feature Exploration Grid (Phase 2 Hub) */}
      <h2 style={{ fontSize: 18, fontWeight: 700, color: '#fff', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
        <span>⚡</span> Architectural Exploration Hub
      </h2>
      <div className="feature-grid">
        <div
          className="feature-card"
          style={{ cursor: 'pointer' }}
          onClick={() => navigate(`/projects/${projectId}/graph`)}
        >
          <div className="feature-icon-wrapper" style={{ color: '#818cf8' }}>
            🔭
          </div>
          <h3 className="feature-title">Knowledge Graph Observatory</h3>
          <p className="feature-desc">
            Explore 2D force-directed architecture with live particle flow, entity type filters, search and neighbor inspection.
          </p>
          <div className="feature-action">
            Open Graph Canvas <span>→</span>
          </div>
        </div>

        <div
          className="feature-card"
          style={{ cursor: 'pointer' }}
          onClick={() => navigate(`/projects/${projectId}/traceability`)}
        >
          <div className="feature-icon-wrapper" style={{ color: '#f43f5e' }}>
            📋
          </div>
          <h3 className="feature-title">Requirement Traceability</h3>
          <p className="feature-desc">
            Track SRS requirements directly to implementing classes, functions, and documentation with proof evidence paths.
          </p>
          <div className="feature-action">
            Open Traceability Matrix <span>→</span>
          </div>
        </div>

        <div
          className="feature-card"
          style={{ cursor: 'pointer' }}
          onClick={() => navigate(`/projects/${projectId}/dependencies`)}
        >
          <div className="feature-icon-wrapper" style={{ color: '#38bdf8' }}>
            🕸️
          </div>
          <h3 className="feature-title">Dependency & Impact Explorer</h3>
          <p className="feature-desc">
            Inspect upstream and downstream BFS dependency trees, calculate shortest paths, and analyze change ripple effects.
          </p>
          <div className="feature-action">
            Analyze Dependencies <span>→</span>
          </div>
        </div>

        <div
          className="feature-card"
          style={{ cursor: 'pointer' }}
          onClick={() => navigate(`/projects/${projectId}/ask`)}
        >
          <div className="feature-icon-wrapper" style={{ color: '#a855f7' }}>
            💬
          </div>
          <h3 className="feature-title">Ask GraphTrace AI</h3>
          <p className="feature-desc">
            Query the codebase using natural language. Get grounded explainable answers backed by verified graph traversals.
          </p>
          <div className="feature-action">
            Start AI Dialogue <span>→</span>
          </div>
        </div>
      </div>

      {/* Entity Breakdown Card */}
      <div className="glass-card" style={{ marginTop: 8 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#fff', marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>Entity Distribution Breakdown</span>
          <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-muted)' }}>
            {totalCount} total mapped entities
          </span>
        </h3>

        {/* Segmented Color Bar */}
        <div style={{ display: 'flex', height: 10, borderRadius: 999, overflow: 'hidden', background: 'var(--bg-raised)', marginBottom: 20 }}>
          {sortedTypes.map(([type, count]) => (
            <div
              key={type}
              title={`${type}: ${count}`}
              style={{
                width: `${(count / (totalCount || 1)) * 100}%`,
                background: nodeColor(type),
                transition: 'width 0.3s ease'
              }}
            />
          ))}
        </div>

        {/* Entity Type Table / Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
          {sortedTypes.map(([type, count]) => {
            const pct = totalCount > 0 ? ((count / totalCount) * 100).toFixed(1) : 0;
            return (
              <div
                key={type}
                onClick={() => navigate(`/projects/${projectId}/graph?nodeType=${type}`)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 10,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = nodeColor(type);
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 16 }}>{nodeIcon(type)}</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>{type}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{pct}% of graph</div>
                  </div>
                </div>
                <div style={{ fontSize: 16, fontWeight: 800, color: nodeColor(type) }}>
                  {count}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
