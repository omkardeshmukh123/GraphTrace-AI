import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../api';
import type { GraphNode, GraphEdge, GraphView } from '../api';
import { nodeColor, nodeSize } from '../nodeColors';
import NodeCard from '../components/NodeCard';

interface FGNode extends GraphNode {
  x?: number;
  y?: number;
  __highlighted?: boolean;
}

interface FGLink extends GraphEdge {
  __highlighted?: boolean;
}

export default function GraphExplorer() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [graphData, setGraphData] = useState<GraphView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoverNode, setHoverNode] = useState<GraphNode | null>(null);
  const [search, setSearch] = useState('');
  const [activeTypes, setActiveTypes] = useState<Set<string>>(new Set());
  const [isPhysicsPaused, setIsPhysicsPaused] = useState(false);
  const [focusNeighborsMode, setFocusNeighborsMode] = useState(false);
  const [showLabels, setShowLabels] = useState(true);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  // Load Graph Data
  useEffect(() => {
    if (!projectId) return;
    const nodeType = searchParams.get('nodeType');
    api.getGraph(projectId, nodeType ? { nodeTypes: [nodeType] } : undefined)
      .then((data) => {
        setGraphData(data);
        setActiveTypes(new Set(data.nodes.map((n) => n.type)));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId, searchParams]);

  // Derived: Active filtered nodes and links
  const { nodes, links } = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    const searchLower = search.toLowerCase();
    const filtered = graphData.nodes.filter(
      (n) =>
        activeTypes.has(n.type) &&
        (!searchLower ||
          n.name.toLowerCase().includes(searchLower) ||
          String(n.properties?.path ?? '').toLowerCase().includes(searchLower))
    );
    const filteredIds = new Set(filtered.map((n) => n.id));

    const filteredLinks = graphData.relationships.filter(
      (e) => filteredIds.has(e.source) && filteredIds.has(e.target)
    );

    return { nodes: filtered as FGNode[], links: filteredLinks as FGLink[] };
  }, [graphData, activeTypes, search]);

  // Highlight neighborhood on selection
  const highlightedIds = useMemo(() => {
    if (!selectedNode && !hoverNode) return new Set<string>();
    const focal = selectedNode || hoverNode;
    if (!focal) return new Set<string>();

    const ids = new Set<string>([focal.id]);
    for (const e of links) {
      if (e.source === focal.id) ids.add(e.target as string);
      if (e.target === focal.id) ids.add(e.source as string);
    }
    return ids;
  }, [selectedNode, hoverNode, links]);

  const handleNodeClick = useCallback(
    (node: FGNode) => {
      const match = graphData?.nodes.find((n) => n.id === node.id);
      setSelectedNode(match ?? null);
    },
    [graphData]
  );

  const handleNodeClickById = useCallback(
    (id: string) => {
      const match = graphData?.nodes.find((n) => n.id === id);
      setSelectedNode(match ?? null);
      const fgNode = nodes.find((n) => n.id === id);
      if (fgNode?.x !== undefined && fgRef.current?.centerAt) {
        fgRef.current.centerAt(fgNode.x, fgNode.y, 600);
        fgRef.current.zoom(2.2, 600);
      }
    },
    [graphData, nodes]
  );

  const allTypes = useMemo(() => {
    if (!graphData) return [];
    return Array.from(new Set(graphData.nodes.map((n) => n.type))).sort();
  }, [graphData]);

  function toggleType(type: string) {
    setActiveTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }

  // Camera Actions
  const handleZoomIn = () => {
    if (fgRef.current?.zoom) {
      fgRef.current.zoom(fgRef.current.zoom() * 1.3, 300);
    }
  };
  const handleZoomOut = () => {
    if (fgRef.current?.zoom) {
      fgRef.current.zoom(fgRef.current.zoom() / 1.3, 300);
    }
  };
  const handleFitView = () => {
    if (fgRef.current?.zoomToFit) {
      fgRef.current.zoomToFit(400, 50);
    }
  };
  const handleTogglePhysics = () => {
    if (fgRef.current?.pauseAnimation && fgRef.current?.resumeAnimation) {
      if (isPhysicsPaused) fgRef.current.resumeAnimation();
      else fgRef.current.pauseAnimation();
      setIsPhysicsPaused(!isPhysicsPaused);
    }
  };

  // Custom Node Canvas Renderer
  const paintNode = useCallback(
    (node: FGNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const { x = 0, y = 0, type, name } = node;
      const baseRadius = nodeSize(type);
      const isSelected = selectedNode?.id === node.id;
      const isHovered = hoverNode?.id === node.id;
      const isHighlighted = highlightedIds.has(node.id);
      const dim = focusNeighborsMode && selectedNode && !isHighlighted;

      ctx.save();
      ctx.globalAlpha = dim ? 0.15 : 1;

      const color = nodeColor(type);

      // Outer halo for selected or hovered
      if (isSelected || isHovered) {
        ctx.beginPath();
        ctx.arc(x, y, baseRadius + 4, 0, 2 * Math.PI, false);
        ctx.fillStyle = `${color}44`;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = color;
        ctx.stroke();
      }

      // Core Circle
      ctx.beginPath();
      ctx.arc(x, y, baseRadius, 0, 2 * Math.PI, false);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(255,255,255,0.4)';
      ctx.stroke();

      // Node Label (Visible when zoomed in or selected/hovered)
      if (showLabels && (globalScale > 0.8 || isSelected || isHovered)) {
        const fontSize = Math.max(10 / globalScale, 3);
        ctx.font = `${isSelected ? 'bold ' : ''}${fontSize}px "Plus Jakarta Sans", system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Text background badge for clarity
        const textWidth = ctx.measureText(name).width;
        ctx.fillStyle = 'rgba(8, 10, 15, 0.85)';
        ctx.fillRect(x - textWidth / 2 - 3, y + baseRadius + 3, textWidth + 6, fontSize + 4);

        ctx.fillStyle = isSelected ? '#fff' : '#cbd5e1';
        ctx.fillText(name, x, y + baseRadius + 3 + fontSize / 2 + 1);
      }

      ctx.restore();
    },
    [selectedNode, hoverNode, highlightedIds, focusNeighborsMode, showLabels]
  );

  return (
    <div className="graph-observatory">
      {/* Floating Top Control Toolbar */}
      <div className="floating-toolbar">
        {/* Left: Project title & Node count */}
        <div className="toolbar-group">
          <div className="glass-pill-bar">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => navigate(`/projects/${projectId}`)}
              style={{ color: '#fff', fontWeight: 700 }}
            >
              ← Dashboard
            </button>
            <span style={{ color: 'var(--border-card)' }}>|</span>
            <span style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
              Showing <strong style={{ color: '#fff' }}>{nodes.length}</strong> nodes, <strong style={{ color: '#fff' }}>{links.length}</strong> links
            </span>
          </div>

          {/* Neighborhood Dim Mode Toggle */}
          <button
            className={`btn btn-sm ${focusNeighborsMode ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFocusNeighborsMode(!focusNeighborsMode)}
            title="Dim nodes not directly connected to the selected entity"
          >
            🎯 Neighbor Focus
          </button>
        </div>

        {/* Right: Search Bar */}
        <div className="toolbar-group">
          <div className="search-input-wrapper">
            <span className="search-icon-inside">🔍</span>
            <input
              type="text"
              className="search-input"
              placeholder="Search graph entities…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                style={{ position: 'absolute', right: 12, background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {loading && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(8,10,15,0.7)', zIndex: 15, gap: 12 }}>
          <div className="spinner" /> Loading graph dataset…
        </div>
      )}

      {error && (
        <div style={{ position: 'absolute', top: 80, left: 24, zIndex: 15, padding: '12px 18px', background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 8, color: '#fda4af' }}>
          ⚠️ {error}
        </div>
      )}

      {/* 2D Force Directed Graph Canvas */}
      {!loading && (
        <ForceGraph2D
          ref={fgRef}
          graphData={{ nodes, links }}
          nodeId="id"
          nodeLabel={(n: any) => `${n.type}: ${n.name}`}
          nodeCanvasObject={paintNode as any}
          nodePointerAreaPaint={(node: any, color, ctx) => {
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeSize(node.type) + 3, 0, 2 * Math.PI, false);
            ctx.fillStyle = color;
            ctx.fill();
          }}
          onNodeClick={handleNodeClick as any}
          onNodeHover={(n: any) => setHoverNode(n ? { id: n.id, type: n.type, name: n.name, properties: n.properties } : null)}
          linkColor={(link: any) => {
            const isHighlighted = highlightedIds.has(link.source?.id || link.source) && highlightedIds.has(link.target?.id || link.target);
            if (isHighlighted) return 'rgba(129, 140, 248, 0.85)';
            return focusNeighborsMode && selectedNode ? 'rgba(255, 255, 255, 0.04)' : 'rgba(255, 255, 255, 0.12)';
          }}
          linkWidth={(link: any) => {
            const isHighlighted = highlightedIds.has(link.source?.id || link.source) && highlightedIds.has(link.target?.id || link.target);
            return isHighlighted ? 2.2 : 1;
          }}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          linkDirectionalParticleWidth={(link: any) => {
            const isHighlighted = highlightedIds.has(link.source?.id || link.source) && highlightedIds.has(link.target?.id || link.target);
            return isHighlighted ? 3 : 1.5;
          }}
          linkDirectionalParticleColor={(link: any) => {
            const isHighlighted = highlightedIds.has(link.source?.id || link.source) && highlightedIds.has(link.target?.id || link.target);
            return isHighlighted ? '#a855f7' : '#6366f1';
          }}
          backgroundColor="#080a0f"
          cooldownTicks={120}
        />
      )}

      {/* Floating Bottom Type Filter Pills */}
      <div className="type-pills-panel">
        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginRight: 4 }}>
          Filters:
        </span>
        {allTypes.map((type) => {
          const active = activeTypes.has(type);
          const count = graphData?.nodes.filter((n) => n.type === type).length || 0;
          return (
            <div
              key={type}
              className={`type-pill ${active ? 'active' : 'inactive'}`}
              onClick={() => toggleType(type)}
            >
              <span className="type-pill-dot" style={{ background: nodeColor(type) }} />
              <span>{type}</span>
              <span style={{ opacity: 0.6, fontSize: 10.5 }}>({count})</span>
            </div>
          );
        })}
      </div>

      {/* Floating Camera Actions */}
      <div className="camera-controls">
        <button className="camera-btn" onClick={handleZoomIn} title="Zoom In">
          ＋
        </button>
        <button className="camera-btn" onClick={handleZoomOut} title="Zoom Out">
          －
        </button>
        <button className="camera-btn" onClick={handleFitView} title="Center & Fit Graph">
          ⤢
        </button>
        <button
          className="camera-btn"
          onClick={handleTogglePhysics}
          title={isPhysicsPaused ? 'Resume Physics' : 'Freeze Graph Simulation'}
        >
          {isPhysicsPaused ? '▶' : '⏸'}
        </button>
        <button
          className="camera-btn"
          onClick={() => setShowLabels(!showLabels)}
          title={showLabels ? 'Hide Labels' : 'Show Labels'}
        >
          🏷️
        </button>
      </div>

      {/* Sliding Node Detail Drawer */}
      {selectedNode && (
        <NodeCard
          node={selectedNode}
          allNodes={graphData?.nodes || []}
          allEdges={graphData?.relationships || []}
          onNodeClick={handleNodeClickById}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}
