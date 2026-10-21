import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../api';
import type {
  ArchitectureView,
  ComponentSummary,
  ComponentDependencyView,
  TechStackView,
  GraphNode,
  GraphEdge,
} from '../api';
import { nodeColor, nodeGlow, nodeIcon, nodeSize } from '../nodeColors';

interface FGNode extends GraphNode {
  x?: number;
  y?: number;
  __highlighted?: boolean;
}

interface FGLink extends GraphEdge {
  __highlighted?: boolean;
}

type TabType = 'topology' | 'components' | 'techstack';

export default function Architecture() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // Data State
  const [archData, setArchData] = useState<ArchitectureView | null>(null);
  const [components, setComponents] = useState<ComponentSummary[]>([]);
  const [techStack, setTechStack] = useState<TechStackView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // UI State
  const [activeTab, setActiveTab] = useState<TabType>('topology');
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeTypes, setActiveTypes] = useState<Set<string>>(
    new Set(['SYSTEM', 'COMPONENT', 'SERVICE', 'TECHNOLOGY'])
  );
  const [isPhysicsPaused, setIsPhysicsPaused] = useState(false);

  // Drilldown / Inspection
  const [selectedCompId, setSelectedCompId] = useState<string | null>(null);
  const [compDep, setCompDep] = useState<ComponentDependencyView | null>(null);
  const [loadingDep, setLoadingDep] = useState(false);
  const [inspectedNode, setInspectedNode] = useState<GraphNode | null>(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  // Initial Load
  useEffect(() => {
    if (!projectId) return;
    setLoading(true);
    Promise.all([
      api.getArchitecture(projectId),
      api.getComponents(projectId),
      api.getTechnologies(projectId),
    ])
      .then(([arch, comps, tech]) => {
        setArchData(arch);
        setComponents(comps);
        setTechStack(tech);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  // Load Component Dependencies when clicked
  const handleInspectComponent = useCallback(
    (componentId: string) => {
      if (!projectId) return;
      setSelectedCompId(componentId);
      setLoadingDep(true);
      api.getComponentDependencies(projectId, componentId)
        .then((dep) => setCompDep(dep))
        .catch(() => setCompDep(null))
        .finally(() => setLoadingDep(false));
    },
    [projectId]
  );

  const closeDrawer = () => {
    setSelectedCompId(null);
    setCompDep(null);
    setInspectedNode(null);
  };

  // Filtered Topology Data
  const { nodes, links } = useMemo(() => {
    if (!archData) return { nodes: [], links: [] };

    const searchLower = search.toLowerCase();
    const filteredNodes = archData.nodes.filter((n) => {
      if (!activeTypes.has(n.type)) return false;
      if (!searchLower) return true;
      return (
        n.name.toLowerCase().includes(searchLower) ||
        String(n.properties?.category ?? '').toLowerCase().includes(searchLower) ||
        String(n.properties?.folder ?? '').toLowerCase().includes(searchLower)
      );
    });

    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredLinks = archData.relationships.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );

    return {
      nodes: filteredNodes as FGNode[],
      links: filteredLinks as FGLink[],
    };
  }, [archData, activeTypes, search]);

  // Filtered Components List
  const filteredComponents = useMemo(() => {
    const searchLower = search.toLowerCase();
    return components.filter((c) => {
      const matchCat =
        selectedCategory === 'all' ||
        c.category.toLowerCase() === selectedCategory.toLowerCase();
      const matchSearch =
        !searchLower ||
        c.name.toLowerCase().includes(searchLower) ||
        c.category.toLowerCase().includes(searchLower) ||
        (c.folder && c.folder.toLowerCase().includes(searchLower)) ||
        c.technologies.some((t) => t.toLowerCase().includes(searchLower));
      return matchCat && matchSearch;
    });
  }, [components, search, selectedCategory]);

  // Categories list for component filters
  const componentCategories = useMemo(() => {
    const set = new Set(components.map((c) => c.category));
    return ['all', ...Array.from(set)];
  }, [components]);

  // Custom Canvas Rendering for Topology
  const paintNode = useCallback(
    (node: FGNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const size = nodeSize(node.type) * 1.5;
      const color = nodeColor(node.type);
      const isSelected =
        selectedCompId === node.id || inspectedNode?.id === node.id;

      // Glow & Circle
      ctx.save();
      ctx.beginPath();
      ctx.arc(node.x ?? 0, node.y ?? 0, size, 0, 2 * Math.PI, false);

      if (isSelected) {
        ctx.shadowColor = '#fff';
        ctx.shadowBlur = 20;
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 3;
      } else {
        ctx.shadowColor = nodeGlow(node.type);
        ctx.shadowBlur = 12;
        ctx.strokeStyle = `${color}cc`;
        ctx.lineWidth = 1.8;
      }

      ctx.fillStyle = color;
      ctx.fill();
      ctx.stroke();
      ctx.restore();

      // Icon Glyph
      const icon = nodeIcon(node.type);
      ctx.font = `${Math.round(size * 1.1)}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(icon, node.x ?? 0, node.y ?? 0);

      // Label with Background Badge
      if (globalScale > 0.6 || isSelected) {
        const label = node.name;
        const fontSize = Math.max(10, Math.round(11 / Math.min(1.5, globalScale)));
        ctx.font = `600 ${fontSize}px var(--font-sans, sans-serif)`;
        const textWidth = ctx.measureText(label).width;
        const padX = 6;
        const padY = 3;
        const labelY = (node.y ?? 0) + size + 7;

        // Label pill background
        ctx.fillStyle = 'rgba(8, 10, 15, 0.85)';
        ctx.strokeStyle = isSelected ? '#fff' : `${color}66`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(
          (node.x ?? 0) - textWidth / 2 - padX,
          labelY,
          textWidth + padX * 2,
          fontSize + padY * 2,
          4
        );
        ctx.fill();
        ctx.stroke();

        // Label text
        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(label, node.x ?? 0, labelY + padY);
      }
    },
    [selectedCompId, inspectedNode]
  );

  // Link Styling
  const linkColor = useCallback((link: FGLink) => {
    switch (link.type) {
      case 'COMMUNICATES_WITH':
        return '#38bdf8'; // Sky cyan
      case 'CONTAINS':
        return 'rgba(129, 140, 248, 0.35)'; // Indigo
      case 'USES':
        return 'rgba(245, 158, 11, 0.5)'; // Amber
      case 'EXPOSES':
        return 'rgba(16, 185, 129, 0.45)'; // Emerald
      default:
        return 'rgba(255, 255, 255, 0.2)';
    }
  }, []);

  const linkWidth = useCallback((link: FGLink) => {
    return link.type === 'COMMUNICATES_WITH' ? 2.5 : 1.2;
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 80, gap: 12, color: 'var(--text-secondary)' }}>
          <div className="spinner" /> Loading Architecture Intelligence…
        </div>
      </div>
    );
  }

  if (error || !archData) {
    return (
      <div className="page-container">
        <div style={{ padding: 20, background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 12, color: '#fda4af' }}>
          ⚠️ Failed to load Architecture: {error || 'Data unavailable'}
        </div>
      </div>
    );
  }

  const stats = archData.stats;

  return (
    <div className="page-container" style={{ position: 'relative' }}>
      {/* Page Header */}
      <div className="page-header arch-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 26 }}>🏛️</span>
            <h1 className="page-title">Architecture Intelligence Explorer</h1>
            <span style={{ fontSize: 11, fontWeight: 700, background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', padding: '2px 9px', borderRadius: 999, border: '1px solid rgba(168, 85, 247, 0.3)' }}>
              Phase 4 System Topology
            </span>
          </div>
          <p className="page-subtitle">
            System components, microservice boundaries, inter-service API traffic, and tech stack detection
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div className="search-input-wrapper">
            <span className="search-icon-inside">🔍</span>
            <input
              type="text"
              placeholder="Search components, services, tech…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => navigate(`/projects/${projectId}/graph`)}
          >
            <span>🔭</span> Full Graph
          </button>
        </div>
      </div>

      {/* KPI Stats Bar */}
      <div className="arch-stats-grid">
        <div className="arch-stat-card">
          <div className="arch-stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            🏢
          </div>
          <div>
            <div className="arch-stat-val">{stats.total_systems}</div>
            <div className="arch-stat-lbl">Systems</div>
          </div>
        </div>

        <div
          className="arch-stat-card"
          style={{ cursor: 'pointer' }}
          onClick={() => setActiveTab('components')}
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
            🧩
          </div>
          <div>
            <div className="arch-stat-val">{stats.total_components}</div>
            <div className="arch-stat-lbl">Components</div>
          </div>
        </div>

        <div className="arch-stat-card">
          <div className="arch-stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>
            ⚙️
          </div>
          <div>
            <div className="arch-stat-val">{stats.total_services}</div>
            <div className="arch-stat-lbl">Services</div>
          </div>
        </div>

        <div
          className="arch-stat-card"
          style={{ cursor: 'pointer' }}
          onClick={() => setActiveTab('techstack')}
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            🛠️
          </div>
          <div>
            <div className="arch-stat-val">{stats.total_technologies}</div>
            <div className="arch-stat-lbl">Technologies</div>
          </div>
        </div>

        <div className="arch-stat-card">
          <div className="arch-stat-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
            ⚡
          </div>
          <div>
            <div className="arch-stat-val">{stats.total_communications}</div>
            <div className="arch-stat-lbl">Inter-Service Calls</div>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="arch-tabs">
        <button
          className={`arch-tab-btn ${activeTab === 'topology' ? 'active' : ''}`}
          onClick={() => setActiveTab('topology')}
        >
          <span>🌐</span> Topology Canvas
        </button>
        <button
          className={`arch-tab-btn ${activeTab === 'components' ? 'active' : ''}`}
          onClick={() => setActiveTab('components')}
        >
          <span>🧩</span> Component Catalog ({components.length})
        </button>
        <button
          className={`arch-tab-btn ${activeTab === 'techstack' ? 'active' : ''}`}
          onClick={() => setActiveTab('techstack')}
        >
          <span>🛠️</span> Technology Stack Matrix ({techStack?.all.length ?? 0})
        </button>
      </div>

      {/* TAB 1: TOPOLOGY CANVAS */}
      {activeTab === 'topology' && (
        <div
          style={{
            position: 'relative',
            height: 'calc(100vh - 340px)',
            minHeight: 520,
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            border: '1px solid var(--border-card)',
            background: '#080a0f',
          }}
        >
          {/* Controls Overlay */}
          <div
            style={{
              position: 'absolute',
              top: 16,
              left: 16,
              zIndex: 10,
              display: 'flex',
              gap: 8,
              alignItems: 'center',
              background: 'rgba(15, 18, 26, 0.85)',
              backdropFilter: 'blur(16px)',
              padding: '6px 12px',
              borderRadius: 999,
              border: '1px solid var(--border-subtle)',
            }}
          >
            {['SYSTEM', 'COMPONENT', 'SERVICE', 'TECHNOLOGY'].map((t) => {
              const active = activeTypes.has(t);
              const col = nodeColor(t);
              return (
                <button
                  key={t}
                  onClick={() => {
                    const next = new Set(activeTypes);
                    if (active) next.delete(t);
                    else next.add(t);
                    setActiveTypes(next);
                  }}
                  style={{
                    background: active ? `${col}22` : 'transparent',
                    border: `1px solid ${active ? col : 'rgba(255,255,255,0.1)'}`,
                    color: active ? '#fff' : 'var(--text-muted)',
                    padding: '4px 10px',
                    borderRadius: 999,
                    fontSize: 11,
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 5,
                    transition: 'all 0.15s ease',
                  }}
                >
                  <span>{nodeIcon(t)}</span>
                  <span>{t}</span>
                </button>
              );
            })}
          </div>

          {/* Action buttons (zoom / pause) */}
          <div
            style={{
              position: 'absolute',
              top: 16,
              right: 16,
              zIndex: 10,
              display: 'flex',
              gap: 6,
            }}
          >
            <button
              className="btn btn-secondary btn-sm"
              style={{ background: 'rgba(15, 18, 26, 0.85)', backdropFilter: 'blur(16px)' }}
              onClick={() => {
                setIsPhysicsPaused(!isPhysicsPaused);
                if (fgRef.current) {
                  if (!isPhysicsPaused) fgRef.current.pauseAnimation();
                  else fgRef.current.resumeAnimation();
                }
              }}
              title="Pause or Resume Layout Physics"
            >
              {isPhysicsPaused ? '▶ Resume' : '⏸ Pause'}
            </button>
            <button
              className="btn btn-secondary btn-sm"
              style={{ background: 'rgba(15, 18, 26, 0.85)', backdropFilter: 'blur(16px)' }}
              onClick={() => fgRef.current?.zoomToFit(400, 50)}
              title="Zoom to Fit Canvas"
            >
              ⛶ Fit View
            </button>
          </div>

          {/* Canvas */}
          <ForceGraph2D
            ref={fgRef}
            graphData={{ nodes, links }}
            nodeCanvasObject={paintNode}
            linkColor={linkColor}
            linkWidth={linkWidth}
            linkDirectionalParticles={(link: FGLink) => (link.type === 'COMMUNICATES_WITH' ? 4 : 0)}
            linkDirectionalParticleSpeed={0.007}
            linkDirectionalParticleWidth={3}
            linkDirectionalParticleColor={() => '#38bdf8'}
            backgroundColor="#080a0f"
            onNodeClick={(node: FGNode) => {
              if (node.type === 'COMPONENT') {
                handleInspectComponent(node.id);
              } else {
                setInspectedNode(node);
              }
            }}
            cooldownTicks={120}
          />

          {/* Legend Overlay */}
          <div
            style={{
              position: 'absolute',
              bottom: 16,
              left: 16,
              zIndex: 10,
              background: 'rgba(15, 18, 26, 0.85)',
              backdropFilter: 'blur(16px)',
              padding: '8px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              fontSize: 11,
              color: 'var(--text-secondary)',
              display: 'flex',
              gap: 16,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 16, height: 3, background: '#38bdf8', display: 'inline-block', borderRadius: 2 }} />
              <span>Inter-Service Call (COMMUNICATES_WITH)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 16, height: 2, background: '#818cf8', display: 'inline-block' }} />
              <span>Boundary (CONTAINS)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 16, height: 2, borderBottom: '2px dashed #f59e0b', display: 'inline-block' }} />
              <span>Tech Binding (USES)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 16, height: 2, borderBottom: '2px dotted #10b981', display: 'inline-block' }} />
              <span>Public API (EXPOSES)</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: COMPONENT CATALOG */}
      {activeTab === 'components' && (
        <div>
          {/* Category Filter Pills */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
            {componentCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  background: selectedCategory === cat ? 'var(--primary)' : 'var(--bg-raised)',
                  color: selectedCategory === cat ? '#fff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 999,
                  padding: '6px 14px',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                  transition: 'all 0.15s ease',
                }}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Components Grid */}
          <div className="arch-component-grid">
            {filteredComponents.map((comp) => {
              const catColor =
                comp.category === 'frontend'
                  ? '#38bdf8'
                  : comp.category === 'application'
                  ? '#a855f7'
                  : comp.category === 'service'
                  ? '#10b981'
                  : '#818cf8';

              return (
                <div key={comp.id} className="arch-component-card">
                  {/* Card Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div>
                      <div
                        className="arch-tag"
                        style={{
                          background: `${catColor}22`,
                          color: catColor,
                          border: `1px solid ${catColor}44`,
                          marginBottom: 6,
                          textTransform: 'uppercase',
                        }}
                      >
                        {comp.category}
                      </div>
                      <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff', wordBreak: 'break-word' }}>
                        {comp.name}
                      </h3>
                      {comp.folder && (
                        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 2 }}>
                          📁 /{comp.folder}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Metrics bar */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(3, 1fr)',
                      gap: 8,
                      background: 'var(--bg-raised)',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-sm)',
                      marginBottom: 16,
                      textAlign: 'center',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: '#22d3ee' }}>
                        {comp.service_count}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Services
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: '#a78bfa' }}>
                        {comp.file_count}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Files
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: '#fbbf24' }}>
                        {comp.technologies.length}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Tech Stack
                      </div>
                    </div>
                  </div>

                  {/* Technologies Used */}
                  {comp.technologies.length > 0 && (
                    <div style={{ marginBottom: 14 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                        Tech Stack
                      </div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {comp.technologies.map((t) => (
                          <span
                            key={t}
                            style={{
                              fontSize: 11,
                              padding: '2px 8px',
                              background: 'rgba(245, 158, 11, 0.1)',
                              color: '#fbbf24',
                              border: '1px solid rgba(245, 158, 11, 0.25)',
                              borderRadius: 6,
                              fontWeight: 600,
                            }}
                          >
                            🛠️ {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Exposed APIs preview */}
                  {comp.exposes.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                        Exposed Endpoints ({comp.exposes.length})
                      </div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {comp.exposes.slice(0, 3).map((ep) => (
                          <span
                            key={ep}
                            style={{
                              fontSize: 11,
                              fontFamily: 'var(--font-mono)',
                              padding: '2px 8px',
                              background: 'rgba(16, 185, 129, 0.1)',
                              color: '#34d399',
                              border: '1px solid rgba(16, 185, 129, 0.25)',
                              borderRadius: 6,
                            }}
                          >
                            {ep}
                          </span>
                        ))}
                        {comp.exposes.length > 3 && (
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', alignSelf: 'center' }}>
                            +{comp.exposes.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div style={{ marginTop: 'auto', paddingTop: 12 }}>
                    <button
                      className="btn btn-primary"
                      style={{ width: '100%', justifyContent: 'center' }}
                      onClick={() => handleInspectComponent(comp.id)}
                    >
                      <span>🔍</span> Inspect Dependencies & Calls
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 3: TECHNOLOGY STACK MATRIX */}
      {activeTab === 'techstack' && techStack && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 20 }}>
            {Object.entries(techStack.by_category).map(([category, items]) => (
              <div
                key={category}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: 22,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 18 }}>
                      {category === 'web-framework'
                        ? '🌐'
                        : category === 'database'
                        ? '🗄️'
                        : category === 'cache'
                        ? '⚡'
                        : category === 'ui-framework'
                        ? '🎨'
                        : category === 'task-queue'
                        ? '⏱️'
                        : '🛠️'}
                    </span>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#fff', textTransform: 'capitalize' }}>
                      {category.replace('-', ' ')}
                    </h3>
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-raised)', padding: '2px 8px', borderRadius: 999 }}>
                    {items.length}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {items.map((tech) => (
                    <div
                      key={tech.id}
                      style={{
                        background: 'var(--bg-raised)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '12px 14px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 6,
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                          {tech.name}
                        </span>
                        <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--primary-light)' }}>
                          {tech.tech_name}
                        </span>
                      </div>
                      {tech.used_by_components.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Used by:</span>
                          {tech.used_by_components.map((cName) => (
                            <span
                              key={cName}
                              style={{
                                fontSize: 10.5,
                                padding: '1px 7px',
                                borderRadius: 4,
                                background: 'rgba(99, 102, 241, 0.15)',
                                color: 'var(--primary-light)',
                                border: '1px solid rgba(99, 102, 241, 0.3)',
                              }}
                            >
                              {cName}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* COMPONENT DEPENDENCY MODAL / DRAWER */}
      {selectedCompId && (
        <div className="arch-drawer-backdrop" onClick={closeDrawer}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                {compDep && (
                  <div
                    className="drawer-type-badge"
                    style={{
                      background: 'rgba(168, 85, 247, 0.2)',
                      color: '#c084fc',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                    }}
                  >
                    <span>🧩</span>
                    <span>COMPONENT</span>
                  </div>
                )}
                <h2 className="drawer-node-name">
                  {compDep?.component.name ?? 'Component Dependencies'}
                </h2>
                {Boolean(compDep?.component.properties?.folder) && (
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
                    Folder: /{String(compDep?.component.properties?.folder)}
                  </div>
                )}
              </div>
              <button
                onClick={closeDrawer}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: 22,
                  cursor: 'pointer',
                  lineHeight: 1,
                }}
              >
                ✕
              </button>
            </div>

            {/* Body */}
            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 24 }}>
              {loadingDep ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40, gap: 10, color: 'var(--text-secondary)' }}>
                  <div className="spinner" /> Loading dependency graph…
                </div>
              ) : compDep ? (
                <>
                  {/* OUTBOUND CALLS */}
                  <div className="glass-card" style={{ padding: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                      <span style={{ fontSize: 16 }}>⚡</span>
                      <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        Outbound Service Calls ({compDep.calls.length})
                      </h4>
                    </div>
                    {compDep.calls.length === 0 ? (
                      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        No outbound microservice or API calls detected.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {compDep.calls.map((target) => (
                          <div
                            key={target.id}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              background: 'var(--bg-raised)',
                              padding: '8px 12px',
                              borderRadius: 6,
                              border: '1px solid var(--border-subtle)',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span style={{ color: '#38bdf8' }}>→</span>
                              <span style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>
                                {target.name}
                              </span>
                            </div>
                            <span
                              style={{
                                fontSize: 10,
                                background: `${nodeColor(target.type)}22`,
                                color: nodeColor(target.type),
                                padding: '2px 6px',
                                borderRadius: 4,
                                textTransform: 'uppercase',
                                fontWeight: 700,
                              }}
                            >
                              {target.type}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* INBOUND CALLS */}
                  <div className="glass-card" style={{ padding: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                      <span style={{ fontSize: 16 }}>📥</span>
                      <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        Inbound Callers ({compDep.called_by.length})
                      </h4>
                    </div>
                    {compDep.called_by.length === 0 ? (
                      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        Direct top-level entrypoint or isolated component.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {compDep.called_by.map((src) => (
                          <div
                            key={src.id}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              background: 'var(--bg-raised)',
                              padding: '8px 12px',
                              borderRadius: 6,
                              border: '1px solid var(--border-subtle)',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span style={{ color: '#c084fc' }}>←</span>
                              <span style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>
                                {src.name}
                              </span>
                            </div>
                            <span
                              style={{
                                fontSize: 10,
                                background: `${nodeColor(src.type)}22`,
                                color: nodeColor(src.type),
                                padding: '2px 6px',
                                borderRadius: 4,
                                textTransform: 'uppercase',
                                fontWeight: 700,
                              }}
                            >
                              {src.type}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* TECHNOLOGIES USED */}
                  <div className="glass-card" style={{ padding: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                      <span style={{ fontSize: 16 }}>🛠️</span>
                      <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        Technologies Bound ({compDep.uses.length})
                      </h4>
                    </div>
                    {compDep.uses.length === 0 ? (
                      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        No external technologies explicitly mapped.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                        {compDep.uses.map((tech) => (
                          <span
                            key={tech.id}
                            style={{
                              fontSize: 12,
                              padding: '4px 10px',
                              borderRadius: 6,
                              background: 'rgba(245, 158, 11, 0.15)',
                              color: '#fbbf24',
                              border: '1px solid rgba(245, 158, 11, 0.3)',
                              fontWeight: 600,
                            }}
                          >
                            🛠️ {tech.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* EXPOSED ENDPOINTS */}
                  <div className="glass-card" style={{ padding: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                      <span style={{ fontSize: 16 }}>🌐</span>
                      <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        Exposed Endpoints & Interfaces ({compDep.exposes.length})
                      </h4>
                    </div>
                    {compDep.exposes.length === 0 ? (
                      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        No public routes or endpoints detected.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {compDep.exposes.map((ep) => (
                          <div
                            key={ep.id}
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: 12,
                              padding: '6px 10px',
                              background: 'rgba(16, 185, 129, 0.1)',
                              color: '#34d399',
                              border: '1px solid rgba(16, 185, 129, 0.25)',
                              borderRadius: 6,
                            }}
                          >
                            {ep.name}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No details available.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* QUICK NODE INSPECTION DRAWER (For SYSTEM, SERVICE, TECHNOLOGY) */}
      {inspectedNode && !selectedCompId && (
        <div className="arch-drawer-backdrop" onClick={closeDrawer}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  className="drawer-type-badge"
                  style={{
                    background: `${nodeColor(inspectedNode.type)}22`,
                    color: nodeColor(inspectedNode.type),
                    border: `1px solid ${nodeColor(inspectedNode.type)}44`,
                  }}
                >
                  <span>{nodeIcon(inspectedNode.type)}</span>
                  <span>{inspectedNode.type}</span>
                </div>
                <h2 className="drawer-node-name">{inspectedNode.name}</h2>
              </div>
              <button
                onClick={closeDrawer}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: 22,
                  cursor: 'pointer',
                  lineHeight: 1,
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="glass-card" style={{ padding: 16 }}>
                <h4 style={{ fontSize: 13, fontWeight: 700, color: '#fff', marginBottom: 10 }}>
                  Properties
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {Object.entries(inspectedNode.properties || {}).map(([key, val]) => (
                    <div
                      key={key}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '6px 0',
                        borderBottom: '1px solid var(--border-subtle)',
                        fontSize: 12,
                      }}
                    >
                      <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                        {key.replace('_', ' ')}:
                      </span>
                      <span style={{ fontFamily: 'var(--font-mono)', color: '#fff' }}>
                        {String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
