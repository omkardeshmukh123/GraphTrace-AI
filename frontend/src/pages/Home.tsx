import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { ProjectSummary } from '../api';
import UploadModal from '../components/UploadModal';

export default function Home() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
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

  return (
    <div className="page-content">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <h1 className="page-title">Projects</h1>
            <p className="page-subtitle">Upload a project ZIP or import a graph to start exploring.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <span>＋</span> New Project
          </button>
        </div>
      </div>

      {loading && <div className="loading"><div className="spinner" /> Loading projects…</div>}
      {error && <div className="error-box">⚠ {error}</div>}

      {!loading && !error && projects.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🗂️</div>
          <div className="empty-title">No projects yet</div>
          <div className="empty-sub">Upload a project ZIP and M1 will parse it into a knowledge graph.</div>
          <button className="btn btn-primary" style={{ marginTop: 8 }} onClick={() => setShowModal(true)}>
            Add your first project
          </button>
        </div>
      )}

      {!loading && projects.length > 0 && (
        <div className="project-grid">
          {projects.map((p) => (
            <div
              key={p.id}
              className="card clickable"
              onClick={() => navigate(`/projects/${p.id}`)}
            >
              <div className="project-card-name">
                <span style={{ fontSize: 18 }}>📦</span>
                {p.name}
              </div>
              <div className="project-card-id">{p.id}</div>
              <div className="project-card-stats">
                <div className="project-card-stat">
                  <span className="project-card-stat-val">{p.node_count}</span>
                  <span className="project-card-stat-lbl">Nodes</span>
                </div>
                <div className="project-card-stat">
                  <span className="project-card-stat-val">{p.relationship_count}</span>
                  <span className="project-card-stat-lbl">Edges</span>
                </div>
                <div className="project-card-stat">
                  <span className="project-card-stat-val">{Object.keys(p.counts).length}</span>
                  <span className="project-card-stat-lbl">Types</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && <UploadModal onClose={() => setShowModal(false)} onSuccess={onSuccess} />}
    </div>
  );
}
