import { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import type { DependencyView, GraphNode, PathView } from '../api';
import { nodeColor, nodeIcon } from '../nodeColors';

export default function Dependencies() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const initialNodeId = searchParams.get('nodeId') || '';

  const [allNodes, setAllNodes] = useState<GraphNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string>(initialNodeId);
  const [direction, setDirection] = useState<'downstream' | 'upstream'>('downstream');
  const [maxDepth, setMaxDepth] = useState<number>(3);
  const [depData, setDepData] = useState<DependencyView | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Shortest Path State
  const [sourceNodeId, setSourceNodeId] = useState<string>('');
  const [targetNodeId, setTargetNodeId] = useState<string>('');
  const [pathData, setPathData] = useState<PathView | null>(null);
  const [pathLoading, setPathLoading] = useState<boolean>(false);
  const [pathError, setPathError] = useState<string>('');

  // Load all nodes for the pickers
  useEffect(() => {
    if (!projectId) return;
    api.getGraph(projectId)
      .then((data) => {
        setAllNodes(data.nodes);
        setSelectedNodeId((prev) => {
          if (prev) return prev;
          const preferred = data.nodes.find((n) => n.type === 'FUNCTION' || n.type === 'CLASS') || data.nodes[0];
          return preferred ? preferred.id : '';
        });
        if (data.nodes.length >= 2) {
          setSourceNodeId(data.nodes[0].id);
          setTargetNodeId(data.nodes[data.nodes.length - 1].id);
        }
      })
      .catch((e) => setError(e.message));
  }, [projectId]);

  // Fetch Dependencies when selected node, direction, or depth changes
  useEffect(() => {
    if (!projectId || !selectedNodeId) return;
    setLoading(true);
    api.getDependencies(projectId, selectedNodeId, direction, maxDepth)
      .then(setDepData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId, selectedNodeId, direction, maxDepth]);

  // Calculate Shortest Path
  function calculatePath() {
    if (!projectId || !sourceNodeId || !targetNodeId) return;
    setPathLoading(true);
    setPathError('');
    api.getPaths(projectId, sourceNodeId, targetNodeId, 6, true)
      .then(setPathData)
      .catch((e) => setPathError(e.message))
      .finally(() => setPathLoading(false));
  }

  const selectedNode = allNodes.find((n) => n.id === selectedNodeId);

  // Group dependencies by distance
  const groupedByDistance: Record<number, GraphNode[]> = {};
  if (depData && depData.distances) {
    for (const [nodeId, dist] of Object.entries(depData.distances)) {
      if (nodeId === selectedNodeId) continue; // skip root
      if (!groupedByDistance[dist]) groupedByDistance[dist] = [];
      const nodeObj = depData.nodes.find((n) => n.id === nodeId);
      if (nodeObj) groupedByDistance[dist].push(nodeObj);
    }
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 24 }}>🕸️</span>
            <h1 className="page-title">Dependency & Impact Explorer</h1>
            <span style={{ fontSize: 12, fontWeight: 700, background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '2px 8px', borderRadius: 999, border: '1px solid rgba(56, 189, 248, 0.3)' }}>
              BFS &bull; Upstream & Downstream
            </span>
          </div>
          <p className="page-subtitle">
            Analyze call graphs, module dependencies, and trace exact shortest connection paths across your system.
          </p>
        </div>

        <button className="btn btn-secondary" onClick={() => navigate(`/projects/${projectId}/graph`)}>
          <span>🔭</span> Open Graph Observatory
        </button>
      </div>

      {/* Main Grid: Left Control & Hierarchy, Right Shortest Path */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 380px', gap: 24, alignItems: 'start' }}>
        {/* Left Column: Dependency Exploration */}
        <div className="glass-card" style={{ padding: 28 }}>
          {/* Controls Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 14, alignItems: 'end', marginBottom: 24 }}>
            {/* Focal Node Selector */}
            <div>
              <label style={{ display: 'block', fontSize: 12.5, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 6 }}>
                Focal Entity
              </label>
              <select
                value={selectedNodeId}
                onChange={(e) => setSelectedNodeId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  color: '#fff',
                  fontSize: 13,
                  outline: 'none',
                }}
              >
                {allNodes.map((n) => (
                  <option key={n.id} value={n.id} style={{ background: '#0f121a' }}>
                    [{n.type}] {n.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Direction Switcher */}
            <div>
              <label style={{ display: 'block', fontSize: 12.5, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 6 }}>
                Direction
              </label>
              <div style={{ display: 'flex', background: 'var(--bg-raised)', borderRadius: 8, padding: 3, border: '1px solid var(--border-subtle)' }}>
                <button
                  onClick={() => setDirection('downstream')}
                  style={{
                    padding: '7px 12px',
                    fontSize: 12,
                    fontWeight: 600,
                    borderRadius: 6,
                    border: 'none',
                    cursor: 'pointer',
                    background: direction === 'downstream' ? 'var(--primary)' : 'transparent',
                    color: direction === 'downstream' ? '#fff' : 'var(--text-muted)',
                  }}
                  title="Entities called or imported by this node"
                >
                  ↓ Downstream (Calls)
                </button>
                <button
                  onClick={() => setDirection('upstream')}
                  style={{
                    padding: '7px 12px',
                    fontSize: 12,
                    fontWeight: 600,
                    borderRadius: 6,
                    border: 'none',
                    cursor: 'pointer',
                    background: direction === 'upstream' ? 'var(--primary)' : 'transparent',
                    color: direction === 'upstream' ? '#fff' : 'var(--text-muted)',
                  }}
                  title="Entities that call or import this node"
                >
                  ↑ Upstream (Callers)
                </button>
              </div>
            </div>

            {/* Max Depth Slider */}
            <div>
              <label style={{ display: 'block', fontSize: 12.5, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 6 }}>
                Depth: <strong style={{ color: '#fff' }}>{maxDepth}</strong>
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={maxDepth}
                onChange={(e) => setMaxDepth(Number(e.target.value))}
                style={{ width: 100, accentColor: 'var(--primary)' }}
              />
            </div>
          </div>

          {/* Focal Entity Banner */}
          {selectedNode && (
            <div style={{ padding: '16px 20px', background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', borderRadius: 12, marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: `${nodeColor(selectedNode.type)}22`, border: `1px solid ${nodeColor(selectedNode.type)}44`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>
                  {nodeIcon(selectedNode.type)}
                </div>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: nodeColor(selectedNode.type), textTransform: 'uppercase' }}>
                    {selectedNode.type} Root
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: '#fff' }}>
                    {selectedNode.name}
                  </div>
                  {Boolean(selectedNode.properties?.path) && (
                    <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      {String(selectedNode.properties.path)}
                    </div>
                  )}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#fff' }}>
                  {Object.keys(depData?.distances || {}).length - 1}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Reachable Entities
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60, gap: 10, color: 'var(--text-secondary)' }}>
              <div className="spinner" /> Traversing dependency graph…
            </div>
          )}

          {error && (
            <div style={{ padding: 14, background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 8, color: '#fda4af', marginBottom: 20 }}>
              ⚠️ {error}
            </div>
          )}

          {/* Grouped Tree List */}
          {!loading && Object.keys(groupedByDistance).length === 0 && (
            <div style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
              No {direction} dependencies detected within depth {maxDepth}.
            </div>
          )}

          {!loading && Object.keys(groupedByDistance).length > 0 && (
            <div className="dep-tree-container">
              {Object.entries(groupedByDistance)
                .sort(([a], [b]) => Number(a) - Number(b))
                .map(([distStr, nodesList]) => {
                  const dist = Number(distStr);
                  return (
                    <div key={dist} style={{ marginBottom: 16 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                        <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.05em', textTransform: 'uppercase', background: 'var(--primary-dim)', color: 'var(--primary-light)', padding: '2px 8px', borderRadius: 4 }}>
                          Distance {dist} &bull; {dist === 1 ? 'Direct' : `${dist} Hops Away`}
                        </span>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>({nodesList.length} entities)</span>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
                        {nodesList.map((n) => (
                          <div
                            key={n.id}
                            className="dep-node-item"
                            onClick={() => setSelectedNodeId(n.id)}
                            style={{ cursor: 'pointer' }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                              <span style={{ fontSize: 15 }}>{nodeIcon(n.type)}</span>
                              <div style={{ minWidth: 0 }}>
                                <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                                  {n.name}
                                </div>
                                <div style={{ fontSize: 10.5, color: nodeColor(n.type), fontWeight: 600 }}>
                                  {n.type}
                                </div>
                              </div>
                            </div>

                            <button
                              className="btn btn-ghost btn-sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedNodeId(n.id);
                              }}
                              title="Focus this node"
                            >
                              Inspect →
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>

        {/* Right Column: Shortest Path Finder */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <span style={{ fontSize: 20 }}>⚡</span>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#fff' }}>Shortest Path Calculator</h3>
          </div>
          <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 18 }}>
            Find the exact shortest structural chain connecting any two entities across the knowledge graph.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 18 }}>
            <div>
              <label style={{ display: 'block', fontSize: 11.5, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 4 }}>
                SOURCE ENTITY
              </label>
              <select
                value={sourceNodeId}
                onChange={(e) => setSourceNodeId(e.target.value)}
                style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', borderRadius: 6, color: '#fff', fontSize: 12 }}
              >
                {allNodes.map((n) => (
                  <option key={n.id} value={n.id} style={{ background: '#0f121a' }}>
                    [{n.type}] {n.name}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
              ↓
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 11.5, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 4 }}>
                TARGET ENTITY
              </label>
              <select
                value={targetNodeId}
                onChange={(e) => setTargetNodeId(e.target.value)}
                style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)', borderRadius: 6, color: '#fff', fontSize: 12 }}
              >
                {allNodes.map((n) => (
                  <option key={n.id} value={n.id} style={{ background: '#0f121a' }}>
                    [{n.type}] {n.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="btn btn-primary"
              style={{ width: '100%', marginTop: 6 }}
              onClick={calculatePath}
              disabled={pathLoading || !sourceNodeId || !targetNodeId}
            >
              {pathLoading ? 'Finding Path…' : 'Calculate Traversal Path'}
            </button>
          </div>

          {pathError && (
            <div style={{ padding: 10, background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 6, color: '#fda4af', fontSize: 12, marginBottom: 14 }}>
              ⚠️ {pathError}
            </div>
          )}

          {pathData && (
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: pathData.found ? '#34d399' : '#fbbf24' }}>
                  {pathData.found ? `✓ Path Found (${pathData.node_ids.length - 1} steps)` : '✕ No direct path within max depth'}
                </span>
              </div>

              {pathData.found && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {pathData.node_ids.map((id, idx) => {
                    const node = allNodes.find((n) => n.id === id);
                    const isLast = idx === pathData.node_ids.length - 1;
                    return (
                      <div key={id} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', background: 'var(--bg-raised)', borderRadius: 6, border: '1px solid var(--border-subtle)' }}>
                          <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--primary-light)' }}>#{idx + 1}</span>
                          <span style={{ fontSize: 12, fontWeight: 600, color: '#fff' }}>{node ? node.name : id}</span>
                          <span style={{ fontSize: 10, color: node ? nodeColor(node.type) : 'inherit', marginLeft: 'auto' }}>
                            {node?.type}
                          </span>
                        </div>
                        {!isLast && (
                          <div style={{ paddingLeft: 20, color: 'var(--text-muted)', fontSize: 11 }}>
                            ↓
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
