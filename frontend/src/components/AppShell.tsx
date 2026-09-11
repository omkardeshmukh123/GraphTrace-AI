import { Link, useLocation } from 'react-router-dom';

export default function App({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isGraph = location.pathname.includes('/graph');

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="topbar-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <circle cx="12" cy="5" r="2" />
            <circle cx="5" cy="19" r="2" />
            <circle cx="19" cy="19" r="2" />
            <line x1="12" y1="7" x2="5" y2="17" />
            <line x1="12" y1="7" x2="19" y2="17" />
            <line x1="7" y1="19" x2="17" y2="19" />
          </svg>
          GraphTrace AI
        </Link>
        <nav className="topbar-nav">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Projects</Link>
        </nav>
        <div className="topbar-spacer" />
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          M4 · Phase 1
        </span>
      </header>
      <main style={isGraph ? {} : undefined}>
        {children}
      </main>
    </div>
  );
}
