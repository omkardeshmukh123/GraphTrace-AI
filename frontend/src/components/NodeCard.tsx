import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { GraphNode, GraphEdge } from '../api';
import { nodeColor, nodeIcon } from '../nodeColors';

interface Props {
  node: GraphNode | null;
  allNodes: GraphNode[];
  allEdges: GraphEdge[];
  onNodeClick: (id: string) => void;
  onClose: () => void;
}

type DrawerTab = 'overview' | 'properties' | 'relationships';

export default function NodeCard({ node, allNodes, allEdges, onNodeClick, onClose }: Props) {
  const [tab, setTab] = useState<DrawerTab>('overview');
  const navigate = useNavigate();
  const { projectId } = useParams();

  if (!node) return null;

  const color = nodeColor(node.type);
  const icon = nodeIcon(node.type);

  // Categorize relationships
  const outgoing = allEdges.filter((e) => e.source === node.id);
  const incoming = allEdges.filter((e) => e.target === node.id);

  const nodeMap = new Map(allNodes.map((n) => [n.id, n]));

  return (
    <div className="node-drawer">
      {/* Drawer Header */}
      <div className="drawer-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            className="drawer-type-badge"
            style={{
              background: `${color}22`,
              color: color,
              border: `1px solid ${color}44`,
            }}
          >
            <span>{icon}</span>
            <span>{node.type}</span>
          </div>
          <h2 className="drawer-node-name" title={node.name}>
            {node.name}
          </h2>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
            ID: {node.id.slice(0, 16)}…
          </div>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: 20,
            cursor: 'pointer',
            padding: 4,
          }}
        >
          ✕
        </button>
      </div>

      {/* Tabs */}
      <div className="drawer-tabs">
        <button
          className={`drawer-tab-btn ${tab === 'overview' ? 'active' : ''}`}
          onClick={() => setTab('overview')}
        >
          Overview
        </button>
        <button
          className={`drawer-tab-btn ${tab === 'properties' ? 'active' : ''}`}
          onClick={() => setTab('properties')}
        >
          Properties ({Object.keys(node.properties || {}).length})
        </button>
        <button
          className={`drawer-tab-btn ${tab === 'relationships' ? 'active' : ''}`}
          onClick={() => setTab('relationships')}
        >
          Connections ({outgoing.length + incoming.length})
        </button>
      </div>

      {/* Body */}
      <div className="drawer-body">
        {tab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Quick Actions */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => navigate(`/projects/${projectId}/dependencies?nodeId=${encodeURIComponent(node.id)}`)}
              >
                🕸️ Dependencies
              </button>
              {node.type === 'REQUIREMENT' ? (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => navigate(`/projects/${projectId}/traceability?reqId=${encodeURIComponent(node.id)}`)}
                >
                  📋 Trace Code
                </button>
              ) : (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => navigate(`/projects/${projectId}/ask?query=${encodeURIComponent(`Explain the function and connections of ${node.name}`)}`)}
                >
                  💬 Ask AI
                </button>
              )}
            </div>

            {/* Core Info */}
            <div style={{ padding: 14, background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 10 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Source Details
              </div>
              {Boolean(node.properties?.path) && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>File Path</div>
                  <div style={{ fontSize: 12.5, fontFamily: 'var(--font-mono)', color: '#fff', wordBreak: 'break-all' }}>
                    {String(node.properties.path)}
                  </div>
                </div>
              )}
              {Boolean(node.properties?.reference) && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Reference</div>
                  <div style={{ fontSize: 12.5, fontFamily: 'var(--font-mono)', color: 'var(--primary-light)' }}>
                    {String(node.properties.reference)}
                  </div>
                </div>
              )}
              {Boolean(node.properties?.description) && (
                <div>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Description</div>
                  <div style={{ fontSize: 13, color: 'var(--text-primary)', marginTop: 2, lineHeight: 1.5 }}>
                    {String(node.properties.description)}
                  </div>
                </div>
              )}
            </div>

            {/* Connectivity Summary */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div style={{ padding: 12, background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 8 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>OUTGOING EDGES</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#fff', marginTop: 4 }}>{outgoing.length}</div>
              </div>
              <div style={{ padding: 12, background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 8 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>INCOMING EDGES</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#fff', marginTop: 4 }}>{incoming.length}</div>
              </div>
            </div>
          </div>
        )}

        {tab === 'properties' && (
          <div>
            {Object.keys(node.properties || {}).length === 0 ? (
              <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 30 }}>
                No extra properties found.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {Object.entries(node.properties || {}).map(([key, val]) => (
                  <div
                    key={key}
                    style={{
                      padding: '10px 12px',
                      background: 'var(--bg-surface)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 8,
                    }}
                  >
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      {key}
                    </div>
                    <div style={{ fontSize: 12.5, fontFamily: 'var(--font-mono)', color: '#fff', marginTop: 2, wordBreak: 'break-all' }}>
                      {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'relationships' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Outgoing */}
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Outgoing ({outgoing.length})
              </div>
              {outgoing.length === 0 ? (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>None</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {outgoing.map((e, idx) => {
                    const targetNode = nodeMap.get(e.target);
                    return (
                      <div
                        key={idx}
                        onClick={() => onNodeClick(e.target)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '8px 12px',
                          background: 'var(--bg-surface)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 8,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--primary-light)', background: 'var(--primary-dim)', padding: '2px 6px', borderRadius: 4 }}>
                            {e.type}
                          </span>
                          <span style={{ fontSize: 13, color: '#fff' }}>
                            {targetNode ? targetNode.name : e.target}
                          </span>
                        </div>
                        <span style={{ fontSize: 11, color: nodeColor(targetNode?.type || '') }}>
                          {targetNode?.type} →
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Incoming */}
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Incoming ({incoming.length})
              </div>
              {incoming.length === 0 ? (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>None</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {incoming.map((e, idx) => {
                    const sourceNode = nodeMap.get(e.source);
                    return (
                      <div
                        key={idx}
                        onClick={() => onNodeClick(e.source)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '8px 12px',
                          background: 'var(--bg-surface)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 8,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontSize: 10, fontWeight: 700, color: '#fb923c', background: 'rgba(251, 146, 60, 0.15)', padding: '2px 6px', borderRadius: 4 }}>
                            {e.type}
                          </span>
                          <span style={{ fontSize: 13, color: '#fff' }}>
                            {sourceNode ? sourceNode.name : e.source}
                          </span>
                        </div>
                        <span style={{ fontSize: 11, color: nodeColor(sourceNode?.type || '') }}>
                          ← {sourceNode?.type}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
