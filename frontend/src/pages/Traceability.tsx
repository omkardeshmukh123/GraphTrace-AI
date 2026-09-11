import { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import type { RequirementSummary, TraceabilityView } from '../api';
import { nodeColor } from '../nodeColors';

export default function Traceability() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [requirements, setRequirements] = useState<RequirementSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'mapped' | 'unmapped'>('all');
  const [search, setSearch] = useState('');
  const [selectedReqId, setSelectedReqId] = useState<string | null>(searchParams.get('reqId'));
  const [traceData, setTraceData] = useState<TraceabilityView | null>(null);
  const [traceLoading, setTraceLoading] = useState(false);

  // Load requirements
  useEffect(() => {
    if (!projectId) return;
    api.getRequirements(projectId)
      .then((data) => {
        setRequirements(data);
        setSelectedReqId((prev) => prev || (data.length > 0 ? data[0].requirement.id : null));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  // Load traceability details for selected requirement
  useEffect(() => {
    if (!projectId || !selectedReqId) return;
    setTraceLoading(true);
    api.getTraceability(projectId, selectedReqId)
      .then(setTraceData)
      .catch(() => setTraceData(null))
      .finally(() => setTraceLoading(false));
  }, [projectId, selectedReqId]);

  const filteredReqs = requirements.filter((r) => {
    const matchesStatus = statusFilter === 'all' || r.mapping_status === statusFilter;
    const searchLower = search.toLowerCase();
    const matchesSearch =
      !searchLower ||
      r.requirement.name.toLowerCase().includes(searchLower) ||
      String(r.requirement.properties?.reference ?? '').toLowerCase().includes(searchLower) ||
      String(r.requirement.properties?.description ?? '').toLowerCase().includes(searchLower);
    return matchesStatus && matchesSearch;
  });

  const mappedCount = requirements.filter((r) => r.mapping_status === 'mapped').length;
  const coveragePct = requirements.length > 0
    ? Math.round((mappedCount / requirements.length) * 100)
    : 0;

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 24 }}>📋</span>
            <h1 className="page-title">Requirement Traceability Matrix</h1>
            <span style={{ fontSize: 12, fontWeight: 700, background: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e', padding: '2px 8px', borderRadius: 999, border: '1px solid rgba(244, 63, 94, 0.3)' }}>
              M1 &bull; SRS &rarr; Code
            </span>
          </div>
          <p className="page-subtitle">
            Bidirectional mapping connecting software specifications to implementation classes, methods, and functions.
          </p>
        </div>

        <button className="btn btn-secondary" onClick={() => navigate(`/projects/${projectId}/graph`)}>
          <span>🔭</span> Open Graph Explorer
        </button>
      </div>

      {/* Coverage Metric Summary */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon">📑</div>
          <div className="stat-label">Total Requirements</div>
          <div className="stat-value">{requirements.length}</div>
          <div className="stat-desc">Parsed from SRS documentation</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-label">Mapped to Implementation</div>
          <div className="stat-value" style={{ color: '#34d399' }}>{mappedCount}</div>
          <div className="stat-desc">Linked directly to code entities</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-label">Unmapped / Pending</div>
          <div className="stat-value" style={{ color: '#fbbf24' }}>
            {requirements.length - mappedCount}
          </div>
          <div className="stat-desc">No direct implementation detected</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-label">Traceability Coverage</div>
          <div className="stat-value" style={{ color: coveragePct >= 80 ? '#34d399' : 'var(--primary-light)' }}>
            {coveragePct}%
          </div>
          <div className="stat-desc">Specification completion score</div>
        </div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60, gap: 12, color: 'var(--text-secondary)' }}>
          <div className="spinner" /> Loading requirements traceability index…
        </div>
      )}

      {error && (
        <div style={{ padding: 18, background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 10, color: '#fda4af', marginBottom: 20 }}>
          ⚠️ {error}
        </div>
      )}

      {!loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(340px, 420px) 1fr', gap: 24, alignItems: 'start' }}>
          {/* Left Column: Requirements List */}
          <div className="glass-card" style={{ padding: 20 }}>
            {/* Filter & Search */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 18 }}>
              <input
                type="text"
                className="search-input"
                style={{ width: '100%' }}
                placeholder="Search requirements by ID or keyword…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <div style={{ display: 'flex', gap: 6 }}>
                {(['all', 'mapped', 'unmapped'] as const).map((st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    style={{
                      flex: 1,
                      padding: '6px 10px',
                      fontSize: 12,
                      fontWeight: 600,
                      borderRadius: 6,
                      border: '1px solid',
                      cursor: 'pointer',
                      background: statusFilter === st ? 'var(--bg-raised)' : 'transparent',
                      borderColor: statusFilter === st ? 'var(--primary)' : 'var(--border-subtle)',
                      color: statusFilter === st ? '#fff' : 'var(--text-muted)',
                      textTransform: 'capitalize'
                    }}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            {/* List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 'calc(100vh - 380px)', overflowY: 'auto' }}>
              {filteredReqs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-muted)' }}>
                  No matching requirements found.
                </div>
              ) : (
                filteredReqs.map((r) => {
                  const isSelected = selectedReqId === r.requirement.id;
                  const ref = r.requirement.properties?.reference || r.requirement.name;

                  return (
                    <div
                      key={r.requirement.id}
                      onClick={() => setSelectedReqId(r.requirement.id)}
                      style={{
                        padding: '14px 16px',
                        borderRadius: 10,
                        border: '1px solid',
                        borderColor: isSelected ? 'var(--primary)' : 'var(--border-subtle)',
                        background: isSelected ? 'var(--bg-raised)' : 'var(--bg-surface)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11.5, fontWeight: 700, color: 'var(--primary-light)' }}>
                          {String(ref)}
                        </span>
                        <span className={r.mapping_status === 'mapped' ? 'badge-mapped' : 'badge-unmapped'}>
                          {r.mapping_status === 'mapped' ? '● Mapped' : '○ Unmapped'}
                        </span>
                      </div>
                      <div style={{ fontSize: 13.5, fontWeight: 600, color: '#fff', marginBottom: 4 }}>
                        {r.requirement.name}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span>Linked Code Entities:</span>
                        <strong style={{ color: '#fff' }}>{r.implementation_count}</strong>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Detailed Traceability Chain */}
          <div className="glass-card" style={{ padding: 28 }}>
            {traceLoading && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60, gap: 10, color: 'var(--text-secondary)' }}>
                <div className="spinner" /> Loading implementation evidence…
              </div>
            )}

            {!traceLoading && !traceData && (
              <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
                Select a requirement to inspect its implementation evidence and traceability path.
              </div>
            )}

            {!traceLoading && traceData && (
              <div>
                {/* Requirement Overview Banner */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 20, marginBottom: 24 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <span className="code-chip" style={{ color: 'var(--primary-light)' }}>
                        {String(traceData.requirement.properties?.reference || traceData.requirement.name)}
                      </span>
                      <span className={traceData.mapping_status === 'mapped' ? 'badge-mapped' : 'badge-unmapped'}>
                        {traceData.mapping_status === 'mapped' ? 'Verified Mapped' : 'Unmapped Specification'}
                      </span>
                    </div>
                    <h2 style={{ fontSize: 20, fontWeight: 800, color: '#fff', margin: '6px 0' }}>
                      {traceData.requirement.name}
                    </h2>
                    {Boolean(traceData.requirement.properties?.description) && (
                      <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 640 }}>
                        {String(traceData.requirement.properties.description)}
                      </p>
                    )}
                  </div>

                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => navigate(`/projects/${projectId}/graph`)}
                    title="Highlight in Graph Observatory"
                  >
                    🔭 View in Graph
                  </button>
                </div>

                {/* Linked Code Implementations */}
                <h3 style={{ fontSize: 15, fontWeight: 700, color: '#fff', marginBottom: 14 }}>
                  Linked Code Implementations ({traceData.implementation_ids.length})
                </h3>

                {traceData.implementation_ids.length === 0 ? (
                  <div style={{ padding: 24, background: 'var(--bg-raised)', borderRadius: 10, border: '1px dashed var(--border-card)', textAlign: 'center', color: 'var(--text-muted)', marginBottom: 28 }}>
                    ⚠️ No direct code entities mapped to this requirement yet. Add manual mapping via JSON or SRS reference identifiers.
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12, marginBottom: 28 }}>
                    {traceData.implementation_ids.map((implId) => {
                      const node = traceData.nodes.find((n) => n.id === implId);
                      const type = node?.type || 'CODE';
                      return (
                        <div
                          key={implId}
                          onClick={() => navigate(`/projects/${projectId}/dependencies?nodeId=${encodeURIComponent(implId)}`)}
                          style={{
                            padding: '12px 16px',
                            background: 'var(--bg-raised)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 10,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.borderColor = nodeColor(type))}
                          onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ fontSize: 11, fontWeight: 700, color: nodeColor(type) }}>
                              {type}
                            </span>
                            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Inspect →</span>
                          </div>
                          <div style={{ fontSize: 14, fontWeight: 700, color: '#fff' }}>
                            {node?.name || implId}
                          </div>
                          {Boolean(node?.properties?.path) && (
                            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginTop: 4 }}>
                              {String(node?.properties?.path)}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Evidence Traversal Paths */}
                {traceData.evidence_paths && traceData.evidence_paths.length > 0 && (
                  <div>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#fff', marginBottom: 12 }}>
                      Graph Evidence Traversal Paths
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {traceData.evidence_paths.map((path, idx) => (
                        <div key={idx} className="traversal-path-card">
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                            {path.map((nodeId, sIdx) => {
                              const node = traceData.nodes.find((n) => n.id === nodeId);
                              const isLast = sIdx === path.length - 1;
                              return (
                                <span key={nodeId} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                                  <span className="path-step-badge" style={{ color: node ? nodeColor(node.type) : 'inherit' }}>
                                    {node ? `${node.name}` : nodeId}
                                  </span>
                                  {!isLast && <span style={{ color: 'var(--text-muted)' }}>&rarr;</span>}
                                </span>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Note */}
                {traceData.note && (
                  <div style={{ marginTop: 24, fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    💡 Note: {traceData.note}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
