import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../api';
import type { GraphNode, GraphEdge, GraphView } from '../api';
import { nodeColor, nodeSize } from '../nodeColors';
import NodeCard from '../components/NodeCard';

interface FGNode extends GraphNode {
  x?: number; y?: number;
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
  const [search, setSearch] = useState('');
  const [activeTypes, setActiveTypes] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  // Load graph
  useEffect(() => {
    if (!projectId) return;
    const nodeType = searchParams.get('nodeType');
    api.getGraph(projectId, nodeType ? { nodeTypes: [nodeType] } : undefined)
      .then((data) => {
        setGraphData(data);
        // enable all types by default
        setActiveTypes(new Set(data.nodes.map((n) => n.type)));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId, searchParams]);

  // Derived: filter by active types + search
  const { nodes, links } = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    const searchLower = search.toLowerCase();
    const filtered = graphData.nodes.filter(
      (n) =>
        activeTypes.has(n.type) &&
        (!searchLower || n.name.toLowerCase().includes(searchLower) ||
          String(n.properties?.path ?? '').toLowerCase().includes(searchLower))
    );
    const filteredIds = new Set(filtered.map((n) => n.id));

    const filteredLinks = graphData.relationships.filter(
      (e) => filteredIds.has(e.source) && filteredIds.has(e.target)
    );

    return { nodes: filtered as FGNode[], links: filteredLinks as FGLink[] };
  }, [graphData, activeTypes, search]);

  // Highlight neighbours on selection
  const highlightedIds = useMemo(() => {
    if (!selectedNode) return new Set<string>();
    const ids = new Set<string>([selectedNode.id]);
    for (const e of links) {
      if (e.source === selectedNode.id) ids.add(e.target as string);
      if (e.target === selectedNode.id) ids.add(e.source as string);
    }
    return ids;
  }, [selectedNode, links]);

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
      // Zoom to node
      const fgNode = nodes.find((n) => n.id === id);
      if (fgNode?.x !== undefined && fgRef.current?.centerAt) {
        fgRef.current.centerAt(fgNode.x, fgNode.y, 500);
      }
    },
    [graphData, nodes]
  );

  const allTypes = useMemo(() => {
    if (!graphData) return [];
    const types = [...new Set(graphData.nodes.map((n) => n.type))].sort();
    return types;
  }, [graphData]);

  function toggleType(type: string) {
    setActiveTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }

  const hasHighlight = highlightedIds.size > 0;

  if (loading) return (
    <div className="explorer-shell">
      <div className="loading" style={{ flex: 1 }}><div className="spinner" /> Loading graph…</div>
    </div>
  );

  if (error) return (
    <div className="page-content">
      <div className="error-box">⚠ {error}</div>
      <button className="btn btn-ghost" onClick={() => navigate(-1)}>← Back</button>
    </div>
  );

  return (
    <div className="explorer-shell">
      {/* Graph canvas */}
      <div className="graph-panel">
        {/* Search bar */}
        <div className="graph-search">
          <input
            className="input"
            placeholder="Search nodes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ boxShadow: 'var(--shadow-md)' }}
          />
        </div>

        {/* Controls */}
        <div className="graph-controls">
          <button className="btn btn-ghost" onClick={() => navigate(`/projects/${projectId}`)}>
            ← Dashboard
          </button>
          <button
            className={`btn ${showFilters ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setShowFilters((v) => !v)}
          >
            🎛 Filter
          </button>
        </div>

        {/* Filter panel */}
        {showFilters && (
          <div className="filter-panel" style={{ right: 'calc(var(--sidebar-w) + 16px)' }}>
            <div className="filter-title">Node Types</div>
            <div
              className="filter-item"
              style={{ marginBottom: 6, borderBottom: '1px solid var(--border)', paddingBottom: 6 }}
              onClick={() =>
                setActiveTypes(activeTypes.size === allTypes.length ? new Set() : new Set(allTypes))
              }
            >
              <div className={`filter-check ${activeTypes.size === allTypes.length ? 'checked' : ''}`}>
                {activeTypes.size === allTypes.length && <span style={{ fontSize: 9, color: '#fff' }}>✓</span>}
              </div>
              All types
            </div>
            {allTypes.map((t) => (
              <div key={t} className="filter-item" onClick={() => toggleType(t)}>
                <div className={`filter-check ${activeTypes.has(t) ? 'checked' : ''}`}>
                  {activeTypes.has(t) && <span style={{ fontSize: 9, color: '#fff' }}>✓</span>}
                </div>
                <div className="legend-dot" style={{ background: nodeColor(t) }} />
                {t}
              </div>
            ))}
          </div>
        )}

        {/* Legend */}
        <div className="graph-legend">
          {allTypes.map((t) => (
            <div key={t} className="legend-item">
              <div className="legend-dot" style={{ background: nodeColor(t) }} />
              {t}
            </div>
          ))}
        </div>

        {/* Stats overlay */}
        <div
          style={{
            position: 'absolute', bottom: 16, right: 'calc(var(--sidebar-w) + 16px)',
            background: 'var(--bg-surface)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)', padding: '6px 12px',
            fontSize: 11, color: 'var(--text-muted)', zIndex: 10,
          }}
        >
          {nodes.length} nodes · {links.length} edges
        </div>

        <ForceGraph2D
          ref={fgRef}
          graphData={{ nodes, links }}
          nodeId="id"
          nodeLabel="name"
          linkSource="source"
          linkTarget="target"
          backgroundColor="var(--bg-base)"
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n = node as FGNode;
            const color = nodeColor(n.type);
            const size = nodeSize(n.type);
            const x = n.x ?? 0;
            const y = n.y ?? 0;
            const dimmed = hasHighlight && !highlightedIds.has(n.id);
            const selected = selectedNode?.id === n.id;

            // Glow for selected
            if (selected) {
              ctx.shadowBlur = 16;
              ctx.shadowColor = color;
            }

            ctx.globalAlpha = dimmed ? 0.15 : 1;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();

            // Selection ring
            if (selected) {
              ctx.strokeStyle = '#fff';
              ctx.lineWidth = 1.5;
              ctx.stroke();
              ctx.shadowBlur = 0;
            }

            ctx.globalAlpha = 1;

            // Label when zoomed in
            if (globalScale > 1.8) {
              ctx.font = `${Math.max(8, 10 / globalScale)}px Inter`;
              ctx.fillStyle = dimmed ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.8)';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(n.name.length > 20 ? n.name.slice(0, 18) + '…' : n.name, x, y + size + 8 / globalScale);
            }
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            const n = node as FGNode;
            const size = nodeSize(n.type) + 3;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(n.x ?? 0, n.y ?? 0, size, 0, 2 * Math.PI);
            ctx.fill();
          }}
          linkColor={(link) => {
            const l = link as FGLink;
            const src = typeof l.source === 'object' ? (l.source as FGNode).id : l.source;
            const tgt = typeof l.target === 'object' ? (l.target as FGNode).id : l.target;
            if (!hasHighlight) return 'rgba(100,116,139,0.35)';
            if (selectedNode && (src === selectedNode.id || tgt === selectedNode.id))
              return 'rgba(255,255,255,0.6)';
            return 'rgba(100,116,139,0.08)';
          }}
          linkWidth={(link) => {
            const l = link as FGLink;
            const src = typeof l.source === 'object' ? (l.source as FGNode).id : l.source;
            const tgt = typeof l.target === 'object' ? (l.target as FGNode).id : l.target;
            if (selectedNode && (src === selectedNode.id || tgt === selectedNode.id)) return 2;
            return 0.8;
          }}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          linkDirectionalArrowColor={() => 'rgba(100,116,139,0.5)'}
          onNodeClick={handleNodeClick}
          onBackgroundClick={() => setSelectedNode(null)}
          cooldownTime={3000}
        />
      </div>

      {/* Detail panel */}
      <NodeCard
        node={selectedNode}
        allNodes={graphData?.nodes ?? []}
        allEdges={graphData?.relationships ?? []}
        onNodeClick={handleNodeClickById}
        onClose={() => setSelectedNode(null)}
      />
    </div>
  );
}
