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
import { nodeColor, nodeIcon } from '../nodeColors';

interface FGNode extends GraphNode {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  __highlighted?: boolean;
}

interface FGLink extends GraphEdge {
  __highlighted?: boolean;
}

function getEntityId(ref: unknown): string {
  if (!ref) return '';
  if (typeof ref === 'object' && ref !== null && 'id' in ref) {
    return String((ref as { id: unknown }).id);
  }
  return String(ref);
}

type TabType = 'topology' | 'components' | 'services' | 'calls' | 'techstack';

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
  const [showParticles, setShowParticles] = useState(true);

  // Hover & Selection State for Canvas
  const [hoveredNode, setHoveredNode] = useState<FGNode | null>(null);
  const [hoveredLink, setHoveredLink] = useState<FGLink | null>(null);

  // Drilldown Drawers
  const [selectedCompId, setSelectedCompId] = useState<string | null>(null);
  const [compDep, setCompDep] = useState<ComponentDependencyView | null>(null);
  const [loadingDep, setLoadingDep] = useState(false);

  const [selectedService, setSelectedService] = useState<GraphNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<GraphEdge | null>(null);
  const [inspectedGenericNode, setInspectedGenericNode] = useState<GraphNode | null>(null);

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

  // Configure d3 force physics for spacious layout
  useEffect(() => {
    if (fgRef.current && archData) {
      fgRef.current.d3Force('charge')?.strength(-380);
      fgRef.current.d3Force('link')?.distance(85);
    }
  }, [archData, activeTab]);

  // Fast Lookups
  const nodeMap = useMemo(() => {
    const map = new Map<string, GraphNode>();
    if (!archData) return map;
    for (const n of archData.nodes) {
      map.set(n.id, n);
    }
    return map;
  }, [archData]);

  // Derived: Service details & connections
  const { allServices, serviceParentMap, serviceOutgoingCalls, serviceIncomingCallers, allCalls } = useMemo(() => {
    if (!archData) {
      return {
        allServices: [] as GraphNode[],
        serviceParentMap: new Map<string, GraphNode>(),
        serviceOutgoingCalls: new Map<string, GraphNode[]>(),
        serviceIncomingCallers: new Map<string, GraphNode[]>(),
        allCalls: [] as GraphEdge[],
      };
    }

    const services = archData.nodes.filter((n) => n.type === 'SERVICE');
    const parentMap = new Map<string, GraphNode>();
    const outCalls = new Map<string, GraphNode[]>();
    const inCallers = new Map<string, GraphNode[]>();
    const calls: GraphEdge[] = [];

    // Initialize maps
    for (const s of services) {
      outCalls.set(s.id, []);
      inCallers.set(s.id, []);
    }

    // Process relationships
    for (const rel of archData.relationships) {
      const srcId = getEntityId(rel.source);
      const tgtId = getEntityId(rel.target);
      const srcNode = nodeMap.get(srcId);
      const tgtNode = nodeMap.get(tgtId);

      // Parent component mapping
      if (rel.type === 'CONTAINS' || rel.type === 'EXPOSES') {
        if (srcNode?.type === 'COMPONENT' && tgtNode?.type === 'SERVICE') {
          parentMap.set(tgtNode.id, srcNode);
        }
      }

      // Calls mapping
      if (rel.type === 'COMMUNICATES_WITH') {
        calls.push(rel);

        if (srcNode && tgtNode) {
          if (!outCalls.has(srcNode.id)) outCalls.set(srcNode.id, []);
          outCalls.get(srcNode.id)!.push(tgtNode);

          if (!inCallers.has(tgtNode.id)) inCallers.set(tgtNode.id, []);
          inCallers.get(tgtNode.id)!.push(srcNode);
        }
      }
    }

    return {
      allServices: services,
      serviceParentMap: parentMap,
      serviceOutgoingCalls: outCalls,
      serviceIncomingCallers: inCallers,
      allCalls: calls,
    };
  }, [archData, nodeMap]);

  // Handlers for click drilldowns
  const handleInspectComponent = useCallback(
    (componentId: string) => {
      if (!projectId) return;
      setSelectedCompId(componentId);
      setSelectedService(null);
      setSelectedLink(null);
      setInspectedGenericNode(null);
      setLoadingDep(true);
      api.getComponentDependencies(projectId, componentId)
        .then((dep) => setCompDep(dep))
        .catch(() => setCompDep(null))
        .finally(() => setLoadingDep(false));
    },
    [projectId]
  );

  const handleInspectService = useCallback(
    (service: GraphNode) => {
      setSelectedService(service);
      setSelectedCompId(null);
      setCompDep(null);
      setSelectedLink(null);
      setInspectedGenericNode(null);
    },
    []
  );

  const handleInspectLink = useCallback(
    (link: GraphEdge) => {
      setSelectedLink(link);
      setSelectedCompId(null);
      setCompDep(null);
      setSelectedService(null);
      setInspectedGenericNode(null);
    },
    []
  );

  const handleInspectGenericNode = useCallback(
    (node: GraphNode) => {
      setInspectedGenericNode(node);
      setSelectedCompId(null);
      setCompDep(null);
      setSelectedService(null);
      setSelectedLink(null);
    },
    []
  );

  const handleNodeClick = useCallback(
    (node: FGNode) => {
      if (node.type === 'COMPONENT') {
        handleInspectComponent(node.id);
      } else if (node.type === 'SERVICE') {
        handleInspectService(node);
      } else {
        handleInspectGenericNode(node);
      }
    },
    [handleInspectComponent, handleInspectService, handleInspectGenericNode]
  );

  const closeAllDrawers = () => {
    setSelectedCompId(null);
    setCompDep(null);
    setSelectedService(null);
    setSelectedLink(null);
    setInspectedGenericNode(null);
  };

  // Focus on node in Topology Canvas
  const focusNodeInCanvas = useCallback(
    (nodeId: string) => {
      setActiveTab('topology');
      setTimeout(() => {
        if (!fgRef.current || !archData) return;
        const targetNode = archData.nodes.find((n) => n.id === nodeId) as FGNode | undefined;
        if (targetNode && typeof targetNode.x === 'number' && typeof targetNode.y === 'number') {
          fgRef.current.centerAt(targetNode.x, targetNode.y, 600);
          fgRef.current.zoom(1.8, 600);
        }
      }, 100);
    },
    [archData]
  );

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
        String(n.properties?.folder ?? '').toLowerCase().includes(searchLower) ||
        String(n.properties?.service_name ?? '').toLowerCase().includes(searchLower)
      );
    });

    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredLinks = archData.relationships
      .filter((e) => {
        const s = getEntityId(e.source);
        const t = getEntityId(e.target);
        return nodeIds.has(s) && nodeIds.has(t);
      })
      .map((e) => ({
        ...e,
        source: getEntityId(e.source),
        target: getEntityId(e.target),
      }));

    return {
      nodes: filteredNodes as FGNode[],
      links: filteredLinks as FGLink[],
    };
  }, [archData, activeTypes, search]);

  // Neighborhood IDs for hover dimming
  const highlightedNodeIds = useMemo(() => {
    const focal = hoveredNode;
    if (!focal) return null;
    const set = new Set<string>([focal.id]);
    for (const link of links) {
      const srcId = getEntityId(link.source);
      const tgtId = getEntityId(link.target);
      if (srcId === focal.id) set.add(tgtId);
      if (tgtId === focal.id) set.add(srcId);
    }
    return set;
  }, [hoveredNode, links]);

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

  // Filtered Services List
  const filteredServices = useMemo(() => {
    const searchLower = search.toLowerCase();
    return allServices.filter((s) => {
      if (!searchLower) return true;
      const parent = serviceParentMap.get(s.id);
      return (
        s.name.toLowerCase().includes(searchLower) ||
        String(s.properties?.service_name ?? '').toLowerCase().includes(searchLower) ||
        (parent && parent.name.toLowerCase().includes(searchLower))
      );
    });
  }, [allServices, search, serviceParentMap]);

  // Filtered Calls List
  const filteredCalls = useMemo(() => {
    const searchLower = search.toLowerCase();
    return allCalls.filter((c) => {
      if (!searchLower) return true;
      const src = nodeMap.get(getEntityId(c.source));
      const tgt = nodeMap.get(getEntityId(c.target));
      return (
        (src && src.name.toLowerCase().includes(searchLower)) ||
        (tgt && tgt.name.toLowerCase().includes(searchLower)) ||
        c.type.toLowerCase().includes(searchLower)
      );
    });
  }, [allCalls, search, nodeMap]);

  // Categories list for component filters
  const componentCategories = useMemo(() => {
    const set = new Set(components.map((c) => c.category));
    return ['all', ...Array.from(set)];
  }, [components]);

  // ── High-End Custom Canvas Node Painter ──
  const paintNode = useCallback(
    (node: FGNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const isHovered = hoveredNode?.id === node.id;
      const isDimmed = highlightedNodeIds !== null && !highlightedNodeIds.has(node.id);
      const isSelected =
        selectedCompId === node.id ||
        selectedService?.id === node.id ||
        inspectedGenericNode?.id === node.id;

      ctx.save();
      if (isDimmed) {
        ctx.globalAlpha = 0.18;
      }

      const col = nodeColor(node.type);

      // ── SYSTEM NODE: Planetary Orbital Hub ──
      if (node.type === 'SYSTEM') {
        const radius = 24;

        // Outer planetary orbit ring
        ctx.save();
        ctx.beginPath();
        ctx.arc(x, y, radius + 8, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(129, 140, 248, 0.45)';
        ctx.setLineDash([5, 4]);
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();

        // Glowing core
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.shadowColor = isHovered || isSelected ? '#fff' : col;
        ctx.shadowBlur = isHovered || isSelected ? 28 : 16;
        const grad = ctx.createRadialGradient(x, y, 4, x, y, radius);
        grad.addColorStop(0, '#818cf8');
        grad.addColorStop(0.7, '#4f46e5');
        grad.addColorStop(1, '#312e81');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = '#c7d2fe';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Icon
        ctx.font = '700 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🌐', x, y);
      }
      // ── COMPONENT NODE: Cyber Squircle Capsule ──
      else if (node.type === 'COMPONENT') {
        const width = 36;
        const height = 30;
        const rx = 8;

        ctx.beginPath();
        ctx.roundRect(x - width / 2, y - height / 2, width, height, rx);
        ctx.shadowColor = isHovered || isSelected ? '#fff' : col;
        ctx.shadowBlur = isHovered || isSelected ? 24 : 12;

        const compGrad = ctx.createLinearGradient(x, y - height / 2, x, y + height / 2);
        compGrad.addColorStop(0, 'rgba(168, 85, 247, 0.9)');
        compGrad.addColorStop(1, 'rgba(107, 33, 168, 0.95)');
        ctx.fillStyle = compGrad;
        ctx.fill();

        ctx.strokeStyle = isSelected ? '#fff' : 'rgba(216, 180, 254, 0.8)';
        ctx.lineWidth = isSelected ? 2.5 : 1.8;
        ctx.stroke();

        // Icon
        ctx.font = '700 15px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🧩', x, y);
      }
      // ── SERVICE NODE: Glowing Cyber Pod with Live Beacon ──
      else if (node.type === 'SERVICE') {
        const radius = 15;

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.shadowColor = isHovered || isSelected ? '#fff' : col;
        ctx.shadowBlur = isHovered || isSelected ? 22 : 10;

        const svcGrad = ctx.createRadialGradient(x, y, 2, x, y, radius);
        svcGrad.addColorStop(0, '#22d3ee');
        svcGrad.addColorStop(0.8, '#0891b2');
        svcGrad.addColorStop(1, '#164e63');
        ctx.fillStyle = svcGrad;
        ctx.fill();

        ctx.strokeStyle = isSelected ? '#fff' : '#67e8f9';
        ctx.lineWidth = isSelected ? 2.5 : 1.6;
        ctx.stroke();

        // Icon
        ctx.font = '700 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚡', x, y);

        // Live status ping beacon on top-right
        ctx.beginPath();
        ctx.arc(x + 11, y - 11, 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = '#10b981'; // Emerald
        ctx.shadowColor = '#10b981';
        ctx.shadowBlur = 8;
        ctx.fill();
      }
      // ── TECHNOLOGY NODE: Amber Hex Crystalline Chip ──
      else {
        const radius = 13;

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.shadowColor = isHovered || isSelected ? '#fff' : col;
        ctx.shadowBlur = isHovered || isSelected ? 20 : 8;

        const techGrad = ctx.createRadialGradient(x, y, 2, x, y, radius);
        techGrad.addColorStop(0, '#fbbf24');
        techGrad.addColorStop(0.8, '#d97706');
        techGrad.addColorStop(1, '#78350f');
        ctx.fillStyle = techGrad;
        ctx.fill();

        ctx.strokeStyle = isSelected ? '#fff' : '#fde68a';
        ctx.lineWidth = isSelected ? 2.2 : 1.4;
        ctx.stroke();

        // Icon
        ctx.font = '700 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🛠️', x, y);
      }

      // ── LABEL WITH SLEEK CONTRAST BADGE ──
      if (globalScale > 0.55 || isHovered || isSelected) {
        const label = node.name;
        const fontSize = Math.max(10, Math.min(13, Math.round(11 / Math.min(1.4, globalScale))));
        ctx.font = `600 ${fontSize}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        const textWidth = ctx.measureText(label).width;
        const padX = 7;
        const padY = 3.5;
        const nodeOffset = node.type === 'SYSTEM' ? 32 : node.type === 'COMPONENT' ? 22 : 19;
        const labelY = y + nodeOffset;

        // Label Pill
        ctx.beginPath();
        ctx.roundRect(
          x - textWidth / 2 - padX,
          labelY,
          textWidth + padX * 2,
          fontSize + padY * 2,
          5
        );
        ctx.fillStyle = isSelected
          ? 'rgba(30, 41, 59, 0.95)'
          : isHovered
          ? 'rgba(15, 23, 42, 0.92)'
          : 'rgba(8, 10, 15, 0.82)';
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#fff' : isHovered ? col : 'rgba(255, 255, 255, 0.12)';
        ctx.lineWidth = isSelected ? 1.5 : 1;
        ctx.stroke();

        // Label Text
        ctx.fillStyle = isSelected ? '#fff' : isHovered ? '#f8fafc' : '#e2e8f0';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(label, x, labelY + padY);
      }

      ctx.restore();
    },
    [hoveredNode, highlightedNodeIds, selectedCompId, selectedService, inspectedGenericNode]
  );

  // Link Styling
  const linkColor = useCallback((link: FGLink) => {
    switch (link.type) {
      case 'COMMUNICATES_WITH':
        return '#38bdf8'; // Electric Sky Cyan
      case 'CONTAINS':
        return 'rgba(167, 139, 250, 0.4)'; // Soft Lavender
      case 'USES':
        return 'rgba(245, 158, 11, 0.5)'; // Amber
      case 'EXPOSES':
        return 'rgba(16, 185, 129, 0.5)'; // Emerald
      default:
        return 'rgba(255, 255, 255, 0.2)';
    }
  }, []);

  const linkWidth = useCallback((link: FGLink) => {
    return link.type === 'COMMUNICATES_WITH' ? 2.8 : 1.4;
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
      {/* ── Page Header ── */}
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
            Interactive microservice radar, inter-service API traffic, service boundaries & technology stacks
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div className="search-input-wrapper">
            <span className="search-icon-inside">🔍</span>
            <input
              type="text"
              placeholder="Search components, services, APIs…"
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

      {/* ── KPI Stats Cards (All Clickable with Interactive Navigation) ── */}
      <div className="arch-stats-grid">
        {/* Systems */}
        <div
          id="kpi-systems"
          className={`arch-stat-card clickable ${activeTab === 'topology' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('topology');
            const sys = archData.nodes.find((n) => n.type === 'SYSTEM');
            if (sys) focusNodeInCanvas(sys.id);
          }}
          title="Click to view System Hub on Topology Radar"
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            🏢
          </div>
          <div style={{ flex: 1 }}>
            <div className="arch-stat-val">{stats.total_systems}</div>
            <div className="arch-stat-lbl">Systems</div>
            <div style={{ fontSize: 11, color: 'var(--primary-light)', fontWeight: 600, marginTop: 4 }}>
              Radar View ↗
            </div>
          </div>
        </div>

        {/* Components */}
        <div
          id="kpi-components"
          className={`arch-stat-card clickable ${activeTab === 'components' ? 'active' : ''}`}
          onClick={() => setActiveTab('components')}
          title="Click to browse Component Catalog"
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
            🧩
          </div>
          <div style={{ flex: 1 }}>
            <div className="arch-stat-val">{stats.total_components}</div>
            <div className="arch-stat-lbl">Components</div>
            <div style={{ fontSize: 11, color: '#c084fc', fontWeight: 600, marginTop: 4 }}>
              Browse Catalog ↗
            </div>
          </div>
        </div>

        {/* Services */}
        <div
          id="kpi-services"
          className={`arch-stat-card clickable ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
          title="Click to inspect Services & Microservices Directory"
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>
            ⚙️
          </div>
          <div style={{ flex: 1 }}>
            <div className="arch-stat-val">{stats.total_services}</div>
            <div className="arch-stat-lbl">Services</div>
            <div style={{ fontSize: 11, color: '#22d3ee', fontWeight: 600, marginTop: 4 }}>
              Directory ↗
            </div>
          </div>
        </div>

        {/* Technologies */}
        <div
          id="kpi-tech"
          className={`arch-stat-card clickable ${activeTab === 'techstack' ? 'active' : ''}`}
          onClick={() => setActiveTab('techstack')}
          title="Click to view Technology Stack Matrix"
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            🛠️
          </div>
          <div style={{ flex: 1 }}>
            <div className="arch-stat-val">{stats.total_technologies}</div>
            <div className="arch-stat-lbl">Technologies</div>
            <div style={{ fontSize: 11, color: '#fbbf24', fontWeight: 600, marginTop: 4 }}>
              Tech Matrix ↗
            </div>
          </div>
        </div>

        {/* Inter-Service Calls */}
        <div
          id="kpi-calls"
          className={`arch-stat-card clickable ${activeTab === 'calls' ? 'active' : ''}`}
          onClick={() => setActiveTab('calls')}
          title="Click to view Inter-Service Communication Flow"
        >
          <div className="arch-stat-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
            ⚡
          </div>
          <div style={{ flex: 1 }}>
            <div className="arch-stat-val">{stats.total_communications}</div>
            <div className="arch-stat-lbl">Inter-Service Calls</div>
            <div style={{ fontSize: 11, color: '#38bdf8', fontWeight: 600, marginTop: 4 }}>
              Live Traffic Flow ↗
            </div>
          </div>
        </div>
      </div>

      {/* ── Tab Navigation ── */}
      <div className="arch-tabs">
        <button
          id="tab-topology"
          className={`arch-tab-btn ${activeTab === 'topology' ? 'active' : ''}`}
          onClick={() => setActiveTab('topology')}
        >
          <span>🌐</span> Topology Radar
        </button>
        <button
          id="tab-components"
          className={`arch-tab-btn ${activeTab === 'components' ? 'active' : ''}`}
          onClick={() => setActiveTab('components')}
        >
          <span>🧩</span> Components ({components.length})
        </button>
        <button
          id="tab-services"
          className={`arch-tab-btn ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
        >
          <span>⚙️</span> Services Directory ({allServices.length})
        </button>
        <button
          id="tab-calls"
          className={`arch-tab-btn ${activeTab === 'calls' ? 'active' : ''}`}
          onClick={() => setActiveTab('calls')}
        >
          <span>⚡</span> Inter-Service Traffic ({allCalls.length})
        </button>
        <button
          id="tab-techstack"
          className={`arch-tab-btn ${activeTab === 'techstack' ? 'active' : ''}`}
          onClick={() => setActiveTab('techstack')}
        >
          <span>🛠️</span> Tech Stack ({techStack?.all.length ?? 0})
        </button>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          TAB 1: TOPOLOGY RADAR CANVAS
         ───────────────────────────────────────────────────────────── */}
      {activeTab === 'topology' && (
        <div className="arch-canvas-container">
          {/* Top-Left: Filter Pills */}
          <div className="arch-hud-top-left">
            {['SYSTEM', 'COMPONENT', 'SERVICE', 'TECHNOLOGY'].map((t) => {
              const active = activeTypes.has(t);
              const col = nodeColor(t);
              const count = archData.nodes.filter((n) => n.type === t).length;
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
                    background: active ? `${col}26` : 'transparent',
                    border: `1px solid ${active ? col : 'rgba(255,255,255,0.1)'}`,
                    color: active ? '#fff' : 'var(--text-muted)',
                    padding: '4px 10px',
                    borderRadius: 999,
                    fontSize: 11,
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    transition: 'all 0.15s ease',
                  }}
                >
                  <span style={{ width: 6, height: 6, borderRadius: '50%', background: active ? col : 'rgba(255,255,255,0.3)' }} />
                  <span>{nodeIcon(t)}</span>
                  <span>{t}</span>
                  <span style={{ fontSize: 10, opacity: 0.75 }}>({count})</span>
                </button>
              );
            })}
          </div>

          {/* Top-Right: Camera & Physics Controls */}
          <div className="arch-hud-top-right">
            <button
              className="arch-hud-btn"
              onClick={() => setShowParticles(!showParticles)}
              title="Toggle Animated Particle Stream on Interservice Calls"
            >
              <span>⚡</span> {showParticles ? 'Traffic Flow: ON' : 'Traffic Flow: OFF'}
            </button>
            <button
              className="arch-hud-btn"
              onClick={() => {
                setIsPhysicsPaused(!isPhysicsPaused);
                if (fgRef.current) {
                  if (!isPhysicsPaused) fgRef.current.pauseAnimation();
                  else fgRef.current.resumeAnimation();
                }
              }}
              title="Pause or Resume Layout Physics"
            >
              {isPhysicsPaused ? '▶ Resume Physics' : '⏸ Pause Physics'}
            </button>
            <button
              className="arch-hud-btn"
              onClick={() => fgRef.current?.zoomToFit(400, 50)}
              title="Zoom to Fit Canvas"
            >
              ⛶ Fit View
            </button>
          </div>

          {/* Force Graph 2D */}
          <ForceGraph2D
            ref={fgRef}
            graphData={{ nodes, links }}
            nodeCanvasObject={paintNode}
            linkColor={linkColor}
            linkWidth={linkWidth}
            linkCurvature={(link: FGLink) => (link.type === 'COMMUNICATES_WITH' ? 0.2 : 0)}
            linkDirectionalArrowLength={(link: FGLink) =>
              link.type === 'COMMUNICATES_WITH' || link.type === 'EXPOSES' ? 5.5 : 0
            }
            linkDirectionalArrowRelPos={0.8}
            linkDirectionalParticles={(link: FGLink) =>
              showParticles && link.type === 'COMMUNICATES_WITH' ? 5 : 0
            }
            linkDirectionalParticleSpeed={0.012}
            linkDirectionalParticleWidth={3.5}
            linkDirectionalParticleColor={() => '#38bdf8'}
            backgroundColor="transparent"
            onNodeClick={handleNodeClick}
            onNodeHover={(node) => setHoveredNode(node as FGNode | null)}
            onLinkClick={(link) => handleInspectLink(link as GraphEdge)}
            onLinkHover={(link) => setHoveredLink(link as FGLink | null)}
            cooldownTicks={140}
          />

          {/* Bottom HUD: Live Hover / Focus Inspector */}
          {(hoveredNode || hoveredLink) && (
            <div className="arch-hud-bottom-info">
              {hoveredNode ? (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 16 }}>{nodeIcon(hoveredNode.type)}</span>
                    <span style={{ fontWeight: 700, color: '#fff' }}>{hoveredNode.name}</span>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 6px',
                        borderRadius: 4,
                        background: `${nodeColor(hoveredNode.type)}22`,
                        color: nodeColor(hoveredNode.type),
                      }}
                    >
                      {hoveredNode.type}
                    </span>
                  </div>
                  <span style={{ color: 'var(--text-muted)' }}>|</span>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ padding: '3px 10px', fontSize: 11 }}
                    onClick={() => handleNodeClick(hoveredNode)}
                  >
                    Click to Inspect ↗
                  </button>
                </>
              ) : hoveredLink ? (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 13, color: 'var(--primary-light)' }}>
                      {nodeMap.get(getEntityId(hoveredLink.source))?.name ?? getEntityId(hoveredLink.source)}
                    </span>
                    <span style={{ color: '#38bdf8', fontWeight: 700 }}>
                      ──[{hoveredLink.type}]──►
                    </span>
                    <span style={{ fontSize: 13, color: 'var(--primary-light)' }}>
                      {nodeMap.get(getEntityId(hoveredLink.target))?.name ?? getEntityId(hoveredLink.target)}
                    </span>
                  </div>
                  <span style={{ color: 'var(--text-muted)' }}>|</span>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ padding: '3px 10px', fontSize: 11 }}
                    onClick={() => handleInspectLink(hoveredLink)}
                  >
                    Inspect Channel ↗
                  </button>
                </>
              ) : null}
            </div>
          )}

          {/* Bottom-Left: Interactive Link Legend */}
          <div
            style={{
              position: 'absolute',
              bottom: 18,
              left: 20,
              zIndex: 10,
              background: 'rgba(12, 15, 24, 0.85)',
              backdropFilter: 'blur(20px)',
              padding: '10px 16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              fontSize: 11,
              color: 'var(--text-secondary)',
              display: 'flex',
              gap: 16,
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6)',
            }}
          >
            <div
              style={{ display: 'flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}
              onClick={() => setActiveTab('calls')}
              title="Click to view all interservice calls"
            >
              <span style={{ width: 16, height: 3.5, background: '#38bdf8', display: 'inline-block', borderRadius: 2 }} />
              <span style={{ color: '#fff', fontWeight: 600 }}>COMMUNICATES_WITH (Clickable ↗)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ width: 16, height: 2, background: '#818cf8', display: 'inline-block' }} />
              <span>CONTAINS</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ width: 16, height: 2, borderBottom: '2px dashed #f59e0b', display: 'inline-block' }} />
              <span>USES</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ width: 16, height: 2, borderBottom: '2px dotted #10b981', display: 'inline-block' }} />
              <span>EXPOSES</span>
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 2: COMPONENT CATALOG
         ───────────────────────────────────────────────────────────── */}
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

              // Contained services in this component
              const containedServices = allServices.filter(
                (s) => serviceParentMap.get(s.id)?.id === comp.id
              );

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

                  {/* Contained Services (Clickable Chips!) */}
                  {containedServices.length > 0 && (
                    <div style={{ marginBottom: 14 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                        Contained Microservices ({containedServices.length})
                      </div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {containedServices.map((svc) => (
                          <button
                            key={svc.id}
                            className="arch-chip-interactive"
                            onClick={() => handleInspectService(svc)}
                            style={{
                              background: 'rgba(6, 182, 212, 0.15)',
                              color: '#22d3ee',
                              border: '1px solid rgba(6, 182, 212, 0.3)',
                            }}
                            title="Click to inspect this service"
                          >
                            <span>⚡</span>
                            <span>{svc.name}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

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

                  {/* Exposed APIs */}
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

                  <div style={{ marginTop: 'auto', paddingTop: 12, display: 'flex', gap: 8 }}>
                    <button
                      className="btn btn-primary"
                      style={{ flex: 1, justifyContent: 'center' }}
                      onClick={() => handleInspectComponent(comp.id)}
                    >
                      <span>🔍</span> Inspect Dependencies
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '8px 12px' }}
                      onClick={() => focusNodeInCanvas(comp.id)}
                      title="Locate on Topology Canvas"
                    >
                      🌐
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 3: SERVICES & MICROSERVICES DIRECTORY
         ───────────────────────────────────────────────────────────── */}
      {activeTab === 'services' && (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
              Every active microservice, container, and code service with incoming/outgoing traffic links. Click any card to inspect.
            </p>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Showing {filteredServices.length} of {allServices.length} services
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 18 }}>
            {filteredServices.map((svc) => {
              const parentComp = serviceParentMap.get(svc.id);
              const outList = serviceOutgoingCalls.get(svc.id) || [];
              const inList = serviceIncomingCallers.get(svc.id) || [];

              return (
                <div
                  key={svc.id}
                  className="arch-service-card"
                  onClick={() => handleInspectService(svc)}
                >
                  {/* Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: 20 }}>⚙️</span>
                        <h3 style={{ fontSize: 17, fontWeight: 700, color: '#fff' }}>
                          {svc.name}
                        </h3>
                      </div>
                      <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--primary-light)' }}>
                        ID: {String(svc.properties?.service_name ?? svc.name)}
                      </div>
                    </div>
                    <span
                      style={{
                        fontSize: 10.5,
                        fontWeight: 700,
                        background: 'rgba(16, 185, 129, 0.15)',
                        color: '#34d399',
                        padding: '3px 8px',
                        borderRadius: 999,
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 5,
                      }}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981' }} />
                      ONLINE
                    </span>
                  </div>

                  {/* Parent Component */}
                  {parentComp && (
                    <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Component:</span>
                      <button
                        className="arch-chip-interactive"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleInspectComponent(parentComp.id);
                        }}
                        style={{
                          background: 'rgba(168, 85, 247, 0.15)',
                          color: '#c084fc',
                          border: '1px solid rgba(168, 85, 247, 0.3)',
                        }}
                      >
                        <span>🧩</span>
                        <span>{parentComp.name}</span>
                      </button>
                    </div>
                  )}

                  {/* Calls Grid */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: 8,
                      background: 'var(--bg-raised)',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-sm)',
                      marginBottom: 14,
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>
                        Outbound Calls
                      </div>
                      <div style={{ fontSize: 15, fontWeight: 800, color: '#38bdf8' }}>
                        {outList.length} targets
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2 }}>
                        Inbound Callers
                      </div>
                      <div style={{ fontSize: 15, fontWeight: 800, color: '#a78bfa' }}>
                        {inList.length} clients
                      </div>
                    </div>
                  </div>

                  {/* Quick Outbound Calls Preview */}
                  {outList.length > 0 && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: 10.5, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 5 }}>
                        Calls Downstream:
                      </div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {outList.map((target) => (
                          <span
                            key={target.id}
                            style={{
                              fontSize: 11,
                              padding: '2px 7px',
                              borderRadius: 4,
                              background: 'rgba(56, 189, 248, 0.1)',
                              color: '#38bdf8',
                              border: '1px solid rgba(56, 189, 248, 0.25)',
                            }}
                          >
                            → {target.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div style={{ marginTop: 'auto', paddingTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 12, color: 'var(--primary-light)', fontWeight: 600 }}>
                      Inspect Service Details →
                    </span>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        focusNodeInCanvas(svc.id);
                      }}
                      title="View on Canvas"
                    >
                      🌐 Focus
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 4: INTER-SERVICE COMMUNICATION TRAFFIC FLOW
         ───────────────────────────────────────────────────────────── */}
      {activeTab === 'calls' && (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
              Full cross-service call traffic matrix and communication bridges detected across code and containers.
            </p>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Showing {filteredCalls.length} communication paths
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filteredCalls.map((call, idx) => {
              const srcId = getEntityId(call.source);
              const tgtId = getEntityId(call.target);
              const srcNode = nodeMap.get(srcId);
              const tgtNode = nodeMap.get(tgtId);

              return (
                <div
                  key={`${srcId}-${tgtId}-${idx}`}
                  className="arch-call-card"
                  onClick={() => handleInspectLink(call)}
                >
                  {/* Source Entity */}
                  <div style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: 10,
                        background: srcNode ? `${nodeColor(srcNode.type)}22` : 'var(--bg-raised)',
                        color: srcNode ? nodeColor(srcNode.type) : '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 18,
                        flexShrink: 0,
                      }}
                    >
                      {srcNode ? nodeIcon(srcNode.type) : '●'}
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        {srcNode?.name ?? srcId}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        {srcNode?.type ?? 'UNKNOWN'}
                      </div>
                    </div>
                  </div>

                  {/* Flow Arrow & Protocol */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 20px', minWidth: 200 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: '#38bdf8', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 3 }}>
                      HTTP / REST API
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: 4 }}>
                      <div style={{ height: 2, flex: 1, background: 'linear-gradient(90deg, rgba(56, 189, 248, 0.2), #38bdf8)' }} />
                      <span style={{ color: '#38bdf8', fontSize: 14, fontWeight: 800 }}>►</span>
                    </div>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                      COMMUNICATES_WITH
                    </span>
                  </div>

                  {/* Target Entity */}
                  <div style={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                        {tgtNode?.name ?? tgtId}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        {tgtNode?.type ?? 'UNKNOWN'}
                      </div>
                    </div>
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: 10,
                        background: tgtNode ? `${nodeColor(tgtNode.type)}22` : 'var(--bg-raised)',
                        color: tgtNode ? nodeColor(tgtNode.type) : '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 18,
                        flexShrink: 0,
                      }}
                    >
                      {tgtNode ? nodeIcon(tgtNode.type) : '●'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 5: TECHNOLOGY STACK MATRIX
         ───────────────────────────────────────────────────────────── */}
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

      {/* ─────────────────────────────────────────────────────────────
          DRAWER 1: COMPONENT DEPENDENCY DRILLDOWN
         ───────────────────────────────────────────────────────────── */}
      {selectedCompId && (
        <div className="arch-drawer-backdrop" onClick={closeAllDrawers}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
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
                onClick={closeAllDrawers}
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
                              cursor: target.type === 'SERVICE' ? 'pointer' : 'default',
                            }}
                            onClick={() => {
                              if (target.type === 'SERVICE') handleInspectService(target);
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
                              cursor: src.type === 'SERVICE' ? 'pointer' : 'default',
                            }}
                            onClick={() => {
                              if (src.type === 'SERVICE') handleInspectService(src);
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

      {/* ─────────────────────────────────────────────────────────────
          DRAWER 2: SERVICE INSPECTOR
         ───────────────────────────────────────────────────────────── */}
      {selectedService && (
        <div className="arch-drawer-backdrop" onClick={closeAllDrawers}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  className="drawer-type-badge"
                  style={{
                    background: 'rgba(6, 182, 212, 0.2)',
                    color: '#22d3ee',
                    border: '1px solid rgba(6, 182, 212, 0.4)',
                  }}
                >
                  <span>⚡</span>
                  <span>SERVICE / MICROSERVICE</span>
                </div>
                <h2 className="drawer-node-name">{selectedService.name}</h2>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
                  ID: {selectedService.id}
                </div>
              </div>
              <button
                onClick={closeAllDrawers}
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

            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* Host Component */}
              {serviceParentMap.get(selectedService.id) && (
                <div className="glass-card" style={{ padding: 16 }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                    Parent Architecture Component
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 18 }}>🧩</span>
                      <span style={{ fontSize: 15, fontWeight: 700, color: '#fff' }}>
                        {serviceParentMap.get(selectedService.id)!.name}
                      </span>
                    </div>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleInspectComponent(serviceParentMap.get(selectedService.id)!.id)}
                    >
                      Inspect Component ↗
                    </button>
                  </div>
                </div>
              )}

              {/* Outbound Calls */}
              <div className="glass-card" style={{ padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 16 }}>⚡</span>
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                    Calls Outbound to Services ({(serviceOutgoingCalls.get(selectedService.id) || []).length})
                  </h4>
                </div>
                {(serviceOutgoingCalls.get(selectedService.id) || []).length === 0 ? (
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    No outbound microservice calls detected from this service.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {(serviceOutgoingCalls.get(selectedService.id) || []).map((target) => (
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
                          cursor: 'pointer',
                        }}
                        onClick={() => handleInspectService(target)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ color: '#38bdf8' }}>→</span>
                          <span style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>
                            {target.name}
                          </span>
                        </div>
                        <span style={{ fontSize: 11, color: 'var(--primary-light)' }}>
                          Inspect →
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Inbound Callers */}
              <div className="glass-card" style={{ padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 16 }}>📥</span>
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                    Invoked Inbound By ({(serviceIncomingCallers.get(selectedService.id) || []).length})
                  </h4>
                </div>
                {(serviceIncomingCallers.get(selectedService.id) || []).length === 0 ? (
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Entrypoint service or called indirectly via load balancer.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {(serviceIncomingCallers.get(selectedService.id) || []).map((caller) => (
                      <div
                        key={caller.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          background: 'var(--bg-raised)',
                          padding: '8px 12px',
                          borderRadius: 6,
                          border: '1px solid var(--border-subtle)',
                          cursor: 'pointer',
                        }}
                        onClick={() => handleInspectService(caller)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ color: '#c084fc' }}>←</span>
                          <span style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>
                            {caller.name}
                          </span>
                        </div>
                        <span style={{ fontSize: 11, color: 'var(--primary-light)' }}>
                          Inspect →
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Action Button */}
              <button
                className="btn btn-primary"
                style={{ justifyContent: 'center' }}
                onClick={() => focusNodeInCanvas(selectedService.id)}
              >
                <span>🌐</span> Focus on Topology Radar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          DRAWER 3: INTER-SERVICE CALL / LINK INSPECTOR
         ───────────────────────────────────────────────────────────── */}
      {selectedLink && (
        <div className="arch-drawer-backdrop" onClick={closeAllDrawers}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  className="drawer-type-badge"
                  style={{
                    background: 'rgba(56, 189, 248, 0.2)',
                    color: '#38bdf8',
                    border: '1px solid rgba(56, 189, 248, 0.4)',
                  }}
                >
                  <span>⚡</span>
                  <span>{selectedLink.type}</span>
                </div>
                <h2 className="drawer-node-name">Inter-Service Communication</h2>
              </div>
              <button
                onClick={closeAllDrawers}
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

            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* Visual Flow Representation */}
              {(() => {
                const srcId = getEntityId(selectedLink.source);
                const tgtId = getEntityId(selectedLink.target);
                const src = nodeMap.get(srcId);
                const tgt = nodeMap.get(tgtId);

                return (
                  <>
                    <div
                      style={{
                        background: 'var(--bg-raised)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-lg)',
                        padding: 20,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 16,
                        alignItems: 'center',
                      }}
                    >
                      {/* Source Node Card */}
                      <div
                        style={{
                          width: '100%',
                          background: 'var(--bg-surface)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 8,
                          padding: '12px 16px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          cursor: 'pointer',
                        }}
                        onClick={() => {
                          if (src?.type === 'SERVICE') handleInspectService(src);
                          else if (src?.type === 'COMPONENT') handleInspectComponent(src.id);
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: 18 }}>
                            {nodeIcon(src?.type ?? 'SERVICE')}
                          </span>
                          <div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                              Source Client
                            </div>
                            <div style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                              {src?.name ?? srcId}
                            </div>
                          </div>
                        </div>
                        <span style={{ fontSize: 11, color: 'var(--primary-light)' }}>Inspect ↗</span>
                      </div>

                      {/* Arrow Flow */}
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <span style={{ fontSize: 11, fontWeight: 700, color: '#38bdf8' }}>
                          HTTP / REST API CALL
                        </span>
                        <div style={{ fontSize: 20, color: '#38bdf8' }}>↓</div>
                      </div>

                      {/* Target Node Card */}
                      <div
                        style={{
                          width: '100%',
                          background: 'var(--bg-surface)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 8,
                          padding: '12px 16px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          cursor: 'pointer',
                        }}
                        onClick={() => {
                          if (tgt?.type === 'SERVICE') handleInspectService(tgt);
                          else if (tgt?.type === 'COMPONENT') handleInspectComponent(tgt.id);
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ fontSize: 18 }}>
                            {nodeIcon(tgt?.type ?? 'SERVICE')}
                          </span>
                          <div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                              Target Destination
                            </div>
                            <div style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                              {tgt?.name ?? tgtId}
                            </div>
                          </div>
                        </div>
                        <span style={{ fontSize: 11, color: 'var(--primary-light)' }}>Inspect ↗</span>
                      </div>
                    </div>

                    {/* Relationship Metadata */}
                    <div className="glass-card" style={{ padding: 16 }}>
                      <h4 style={{ fontSize: 13, fontWeight: 700, color: '#fff', marginBottom: 12 }}>
                        Communication Metadata
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Relationship:</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{selectedLink.type}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Provenance:</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: '#fff' }}>
                            {String(selectedLink.properties?.provenance ?? 'Static AST / Compose')}
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Protocol:</span>
                          <span style={{ fontFamily: 'var(--font-mono)', color: '#34d399' }}>RESTful JSON / HTTP</span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 10 }}>
                      <button
                        className="btn btn-secondary"
                        style={{ flex: 1, justifyContent: 'center' }}
                        onClick={() => focusNodeInCanvas(srcId)}
                      >
                        Locate Source 🌐
                      </button>
                      <button
                        className="btn btn-primary"
                        style={{ flex: 1, justifyContent: 'center' }}
                        onClick={() => focusNodeInCanvas(tgtId)}
                      >
                        Locate Target 🌐
                      </button>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          DRAWER 4: GENERIC NODE INSPECTOR (SYSTEM, TECHNOLOGY)
         ───────────────────────────────────────────────────────────── */}
      {inspectedGenericNode && (
        <div className="arch-drawer-backdrop" onClick={closeAllDrawers}>
          <div className="arch-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  className="drawer-type-badge"
                  style={{
                    background: `${nodeColor(inspectedGenericNode.type)}22`,
                    color: nodeColor(inspectedGenericNode.type),
                    border: `1px solid ${nodeColor(inspectedGenericNode.type)}44`,
                  }}
                >
                  <span>{nodeIcon(inspectedGenericNode.type)}</span>
                  <span>{inspectedGenericNode.type}</span>
                </div>
                <h2 className="drawer-node-name">{inspectedGenericNode.name}</h2>
              </div>
              <button
                onClick={closeAllDrawers}
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
                  {Object.entries(inspectedGenericNode.properties || {}).map(([key, val]) => (
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

              <button
                className="btn btn-primary"
                style={{ justifyContent: 'center' }}
                onClick={() => focusNodeInCanvas(inspectedGenericNode.id)}
              >
                <span>🌐</span> Focus on Topology Canvas
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
