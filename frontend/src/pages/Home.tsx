import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { ProjectSummary } from '../api';
import UploadModal from '../components/UploadModal';
import { nodeColor } from '../nodeColors';

export default function Home() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    api.listProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function onSuccess(project: ProjectSummary) {
    setShowModal(false);
    navigate(`/projects/${project.id}`);
  }

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalNodesAcrossProjects = projects.reduce((acc, p) => acc + p.node_count, 0);
  const totalEdgesAcrossProjects = projects.reduce((acc, p) => acc + p.relationship_count, 0);

  return (
    <div className="page-container">
      {/* Hero Header */}
      <div className="hero-banner">
        <div className="hero-content">
          <div className="hero-tag">
            <span>⚡</span> Software Knowledge Graph Platform
          </div>
          <h1 className="hero-title">
            Deep Architectural Understanding & <span>Explainable Intelligence</span>
          </h1>
          <p className="hero-desc">
            GraphTrace AI connects source code, AST entities, requirements, and documentation into a unified, queryable software knowledge graph with real-time traceability and dependency analysis.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              <span>＋</span> Upload Repository
            </button>
            {projects.some((p) => p.id === 'demo') ? (
              <button
                className="btn btn-secondary"
                onClick={() => navigate('/projects/demo/graph')}
              >
                <span>🔭</span> Launch Demo Graph Explorer
              </button>
            ) : null}
          </div>
        </div>
      </div>

      {/* Global Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-label">Active Projects</div>
          <div className="stat-value">{projects.length}</div>
          <div className="stat-desc">Ingested repositories</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🧩</div>
          <div className="stat-label">Total Knowledge Entities</div>
          <div className="stat-value">{totalNodesAcrossProjects.toLocaleString()}</div>
          <div className="stat-desc">Nodes indexed in graph</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🕸️</div>
          <div className="stat-label">Active Relationships</div>
          <div className="stat-value">{totalEdgesAcrossProjects.toLocaleString()}</div>
          <div className="stat-desc">Calls, defines, imports & traces</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-label">Analysis Speed</div>
          <div className="stat-value">&lt; 1.2s</div>
          <div className="stat-desc">Multi-language AST parser</div>
        </div>
      </div>

      {/* Projects Section Header */}
      <div className="page-header" style={{ alignItems: 'center', marginTop: 12 }}>
        <div>
          <h2 className="page-title" style={{ fontSize: 20 }}>
            <span>📂</span> Projects Repository
          </h2>
          <p className="page-subtitle">Select a project to explore its architecture and knowledge graph</p>
        </div>

        {/* Search Bar */}
        <div className="search-input-wrapper">
          <span className="search-icon-inside">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search projects by name or ID…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60, gap: 12, color: 'var(--text-secondary)' }}>
          <div className="spinner" /> Loading project knowledge base…
        </div>
      )}

      {error && (
        <div style={{ padding: '16px 20px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 12, color: '#fda4af', marginBottom: 24 }}>
          ⚠️ Backend error: {error}
        </div>
      )}

      {!loading && !error && projects.length === 0 && (
        <div style={{ padding: '64px 24px', textAlign: 'center', background: 'var(--bg-surface)', border: '1px dashed var(--border-card)', borderRadius: 'var(--radius-xl)' }}>
          <div style={{ fontSize: 44, marginBottom: 16 }}>🗂️</div>
          <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff', marginBottom: 6 }}>No projects loaded yet</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, maxWidth: 460, margin: '0 auto 20px' }}>
            Upload a software repository ZIP archive. Member 1's AST parser will automatically extract software entities and build the knowledge graph.
          </p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            Upload your first project
          </button>
        </div>
      )}

      {!loading && projects.length > 0 && (
        <div className="project-grid">
          {filteredProjects.map((p) => {
            const sortedCounts = Object.entries(p.counts || {}).sort(([, a], [, b]) => b - a);
            const totalCount = sortedCounts.reduce((acc, [, val]) => acc + val, 0);

            return (
              <div key={p.id} className="project-card">
                <div className="project-card-header">
                  <div>
                    <h3 className="project-name">{p.name}</h3>
                    <div style={{ marginTop: 4 }}>
                      <span className="project-id-tag">{p.id}</span>
                    </div>
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--primary-light)', background: 'var(--primary-dim)', padding: '3px 8px', borderRadius: 999 }}>
                    {p.source}
                  </span>
                </div>

                {/* Mini Stats Bar */}
                <div className="project-mini-stats">
                  <div>
                    <div className="mini-stat-val">{p.node_count}</div>
                    <div className="mini-stat-lbl">Entities</div>
                  </div>
                  <div>
                    <div className="mini-stat-val">{p.relationship_count}</div>
                    <div className="mini-stat-lbl">Edges</div>
                  </div>
                  <div>
                    <div className="mini-stat-val">{sortedCounts.length}</div>
                    <div className="mini-stat-lbl">Types</div>
                  </div>
                </div>

                {/* Entity Distribution Bar */}
                <div style={{ marginBottom: 18 }}>
                  <div style={{ display: 'flex', height: 6, borderRadius: 999, overflow: 'hidden', background: 'var(--bg-raised)', marginBottom: 8 }}>
                    {sortedCounts.map(([type, count]) => (
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
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {sortedCounts.slice(0, 4).map(([type, count]) => (
                      <span key={type} style={{ fontSize: 11, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: nodeColor(type) }} />
                        {type}: <strong style={{ color: '#fff' }}>{count}</strong>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 'auto' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => navigate(`/projects/${p.id}`)}
                  >
                    📊 Dashboard
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => navigate(`/projects/${p.id}/graph`)}
                  >
                    🔭 Explore Graph
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && <UploadModal onClose={() => setShowModal(false)} onSuccess={onSuccess} />}
    </div>
  );
}
