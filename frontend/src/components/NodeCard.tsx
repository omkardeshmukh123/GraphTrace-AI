import type { GraphNode, GraphEdge } from '../api';
import { nodeColor } from '../nodeColors';

interface Props {
  node: GraphNode | null;
  allNodes: GraphNode[];
  allEdges: GraphEdge[];
  onNodeClick: (id: string) => void;
  onClose: () => void;
}

export default function NodeCard({ node, allNodes, allEdges, onNodeClick, onClose }: Props) {
  if (!node) {
    return (
      <div className="detail-panel">
        <div className="detail-header">
          <span className="detail-header-title">Node Details</span>
        </div>
        <div className="detail-body">
          <div className="detail-empty">
            <div className="detail-empty-icon">🔍</div>
            <div className="detail-empty-text">Click any node in the graph to explore it</div>
          </div>
        </div>
      </div>
    );
  }

  const color = nodeColor(node.type);
  const props = Object.entries(node.properties).filter(([, v]) => v !== null && v !== undefined && v !== '');

  // Find connected nodes
  const neighbours: { edge: GraphEdge; other: GraphNode; direction: 'out' | 'in' }[] = [];
  const seen = new Set<string>();
  for (const e of allEdges) {
    if (e.source === node.id && !seen.has(e.target)) {
      const other = allNodes.find((n) => n.id === e.target);
      if (other) { neighbours.push({ edge: e, other, direction: 'out' }); seen.add(e.target); }
    } else if (e.target === node.id && !seen.has(e.source)) {
      const other = allNodes.find((n) => n.id === e.source);
      if (other) { neighbours.push({ edge: e, other, direction: 'in' }); seen.add(e.source); }
    }
  }

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <span className="detail-header-title">Node Details</span>
        <button className="btn btn-ghost" style={{ padding: '2px 8px', fontSize: 11 }} onClick={onClose}>✕</button>
      </div>
      <div className="detail-body">
        <div className="detail-node-name">{node.name}</div>
        <span
          className="badge detail-node-type"
          style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}
        >
          {node.type}
        </span>

        {props.length > 0 && (
          <div className="detail-props">
            {props.map(([k, v]) => (
              <div key={k}>
                <div className="detail-prop-key">{k}</div>
                <div className="detail-prop-val">{String(v)}</div>
              </div>
            ))}
          </div>
        )}

        {neighbours.length > 0 && (
          <>
            <div className="divider" />
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 8 }}>
              Connections ({neighbours.length})
            </div>
            <div className="neighbour-list">
              {neighbours.map(({ edge, other, direction }) => (
                <div key={`${edge.source}-${edge.type}-${edge.target}`} className="neighbour-item" onClick={() => onNodeClick(other.id)}>
                  <div className="legend-dot" style={{ background: nodeColor(other.type), flexShrink: 0 }} />
                  <div className="neighbour-name">{other.name}</div>
                  <div className="neighbour-rel">{direction === 'out' ? '→' : '←'} {edge.type}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
