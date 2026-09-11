import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { ProjectSummary } from '../api';
import UploadModal from './UploadModal';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract project ID from pathname (e.g. /projects/demo/graph -> demo)
  const pathMatch = location.pathname.match(/\/projects\/([^/]+)/);
  const currentProjectId = pathMatch ? pathMatch[1] : null;

  const [health, setHealth] = useState<{ status: string; store: string } | null>(null);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: 'offline', store: 'none' }));
    api.listProjects().then(setProjects).catch(() => {});
  }, [location.pathname]);

  function handleUploadSuccess(newProject: ProjectSummary) {
    setShowUploadModal(false);
    navigate(`/projects/${newProject.id}`);
  }

  const isGraph = location.pathname.includes('/graph');

  return (
    <div className="app-shell">
      <header className="topbar">
        {/* Brand */}
        <Link to="/" className="topbar-brand">
          <div className="brand-logo-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="5" r="2.5" />
              <circle cx="5" cy="19" r="2.5" />
              <circle cx="19" cy="19" r="2.5" />
              <line x1="12" y1="7.5" x2="5" y2="16.5" />
              <line x1="12" y1="7.5" x2="19" y2="16.5" />
              <line x1="7.5" y1="19" x2="16.5" y2="19" />
            </svg>
          </div>
          <span>GraphTrace <span style={{ color: 'var(--primary-light)' }}>AI</span></span>
          <span className="brand-title-badge">Phase 2</span>
        </Link>

        {/* Project Switcher Selector */}
        {currentProjectId && (
          <div className="project-selector" title="Switch active project">
            <span style={{ color: 'var(--text-muted)' }}>Project:</span>
            <select
              value={currentProjectId}
              onChange={(e) => {
                const targetId = e.target.value;
                if (targetId === '__home__') {
                  navigate('/');
                } else {
                  // Keep current subview (e.g. /graph or /traceability) if switching
                  const subview = location.pathname.replace(`/projects/${currentProjectId}`, '');
                  navigate(`/projects/${targetId}${subview || ''}`);
                }
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#fff',
                fontWeight: 600,
                fontSize: 13,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id} style={{ background: '#0f121a', color: '#fff' }}>
                  {p.name}
                </option>
              ))}
              <option value="__home__" style={{ background: '#0f121a', color: '#94a3b8' }}>
                📂 All Projects…
              </option>
            </select>
          </div>
        )}

        {/* Navigation Tabs */}
        <nav className="topbar-nav">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Projects
          </Link>

          {currentProjectId && (
            <>
              <Link
                to={`/projects/${currentProjectId}`}
                className={`nav-link ${location.pathname === `/projects/${currentProjectId}` ? 'active' : ''}`}
              >
                📊 Dashboard
              </Link>
              <Link
                to={`/projects/${currentProjectId}/graph`}
                className={`nav-link ${location.pathname.includes('/graph') ? 'active' : ''}`}
              >
                🔭 Knowledge Graph
              </Link>
              <Link
                to={`/projects/${currentProjectId}/traceability`}
                className={`nav-link ${location.pathname.includes('/traceability') ? 'active' : ''}`}
              >
                📋 Traceability
              </Link>
              <Link
                to={`/projects/${currentProjectId}/dependencies`}
                className={`nav-link ${location.pathname.includes('/dependencies') ? 'active' : ''}`}
              >
                🕸️ Dependencies
              </Link>
              <Link
                to={`/projects/${currentProjectId}/ask`}
                className={`nav-link ${location.pathname.includes('/ask') ? 'active' : ''}`}
              >
                💬 Ask AI
              </Link>
            </>
          )}
        </nav>

        <div className="topbar-spacer" />

        {/* Engine Status Pill */}
        {health && (
          <div className="engine-status" title={`Active Store: ${health.store}`}>
            <span className="status-pulse" />
            <span>{health.store === 'neo4j' ? 'Neo4j Cloud' : 'Local Engine'}</span>
          </div>
        )}

        {/* Upload Project Action */}
        <button
          className="btn btn-primary btn-sm"
          onClick={() => setShowUploadModal(true)}
        >
          <span>＋</span> Upload Project
        </button>
      </header>

      {/* Main Content */}
      <main className="main-content" style={isGraph ? { height: 'calc(100vh - var(--topbar-h))', overflow: 'hidden' } : undefined}>
        {children}
      </main>

      {/* Global Upload Modal */}
      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onSuccess={handleUploadSuccess}
        />
      )}
    </div>
  );
}
