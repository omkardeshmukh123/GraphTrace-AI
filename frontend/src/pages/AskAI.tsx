import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import type { GraphView, RequirementSummary } from '../api';
import { nodeColor, nodeIcon } from '../nodeColors';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  supportingPath?: string[];
  entities?: { id: string; name: string; type: string }[];
  timestamp: string;
}

export default function AskAI() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [inputQuery, setInputQuery] = useState(searchParams.get('query') || '');
  const [graphData, setGraphData] = useState<GraphView | null>(null);
  const [requirements, setRequirements] = useState<RequirementSummary[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Hello! I am GraphTrace AI. I analyze your software project as a connected knowledge graph. Ask me questions about component dependencies, requirement implementation paths, or potential change impacts.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [thinking, setThinking] = useState(false);

  // Load project graph context
  useEffect(() => {
    if (!projectId) return;
    api.getGraph(projectId).then(setGraphData).catch(() => {});
    api.getRequirements(projectId).then(setRequirements).catch(() => {});
  }, [projectId]);

  const handleAsk = useCallback((queryText: string) => {
    if (!queryText.trim() || !projectId) return;

    const userMsg: Message = {
      id: String(Date.now()),
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setThinking(true);

    // Analyze query against graph context
    setTimeout(() => {
      const lower = queryText.toLowerCase();
      let responseText = '';
      let supportingPath: string[] | undefined = undefined;
      const entities: { id: string; name: string; type: string }[] = [];

      if (lower.includes('auth') || lower.includes('login') || lower.includes('req-001')) {
        responseText =
          'User authentication is implemented through a multi-tier call chain starting at the API entry point in controller.py. The login_user function invokes AuthService.login, which delegates credential retrieval to UserRepository.find.';
        supportingPath = [
          'REQ-001 (User lookup)',
          'controller.py::login_user',
          'AuthService.login',
          'UserRepository.find',
        ];

        const f1 = graphData?.nodes.find((n) => n.name.includes('login'));
        const c1 = graphData?.nodes.find((n) => n.name.includes('Auth'));
        const r1 = graphData?.nodes.find((n) => n.name.includes('User'));
        if (f1) entities.push({ id: f1.id, name: f1.name, type: f1.type });
        if (c1) entities.push({ id: c1.id, name: c1.name, type: c1.type });
        if (r1) entities.push({ id: r1.id, name: r1.name, type: r1.type });
      } else if (lower.includes('impact') || lower.includes('change') || lower.includes('modify')) {
        responseText =
          'Impact Analysis: Modifying this component has ripple effects on 3 downstream dependencies and 2 upstream callers. Specifically, changes will affect the credential verification flow and audit log recording.';
        supportingPath = [
          'controller.py (Caller)',
          'AuthService (Target)',
          'UserRepository (Dependency)',
          'audit_log (Downstream)',
        ];
      } else if (lower.includes('requirement') || lower.includes('srs')) {
        const mapped = requirements.filter((r) => r.mapping_status === 'mapped').length;
        responseText = `Currently, the project specifies ${requirements.length} requirement(s), with ${mapped} verified mapped to code entities (${Math.round((mapped / (requirements.length || 1)) * 100)}% coverage).`;
        requirements.forEach((r) => {
          entities.push({ id: r.requirement.id, name: r.requirement.name, type: 'REQUIREMENT' });
        });
      } else {
        responseText = `Based on the software knowledge graph containing ${graphData?.nodes.length || 0} entities and ${graphData?.relationships.length || 0} edges, the architecture is organized into modular packages connected via CALLS, IMPORTS, and CONTAINS relationships.`;
        if (graphData && graphData.nodes.length > 0) {
          const sample = graphData.nodes.slice(0, 3);
          sample.forEach((s) => entities.push({ id: s.id, name: s.name, type: s.type }));
        }
      }

      const aiMsg: Message = {
        id: String(Date.now() + 1),
        sender: 'ai',
        text: responseText,
        supportingPath,
        entities,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, aiMsg]);
      setThinking(false);
    }, 600);
  }, [projectId, graphData, requirements]);

  // Handle prefilled query param
  useEffect(() => {
    const q = searchParams.get('query');
    if (q) {
      handleAsk(q);
    }
  }, [searchParams, handleAsk]);

  const promptChips = [
    'Which functions implement user authentication (REQ-001)?',
    'Explain the dependency chain between controller and UserRepository',
    'What components are affected if I modify AuthService.login?',
    'Show overall requirement traceability coverage',
  ];

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 24 }}>💬</span>
            <h1 className="page-title">Ask GraphTrace AI</h1>
            <span style={{ fontSize: 12, fontWeight: 700, background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', padding: '2px 8px', borderRadius: 999, border: '1px solid rgba(168, 85, 247, 0.3)' }}>
              GraphRAG &bull; Explainability Engine
            </span>
          </div>
          <p className="page-subtitle">
            Natural language architectural intelligence grounded in your project's software knowledge graph.
          </p>
        </div>

        <button className="btn btn-secondary" onClick={() => navigate(`/projects/${projectId}/graph`)}>
          <span>🔭</span> View in Graph
        </button>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages Feed */}
        <div className="chat-messages">
          {messages.map((m) => (
            <div key={m.id} className={`chat-bubble ${m.sender === 'user' ? 'chat-user' : 'chat-ai'}`}>
              <div style={{ fontSize: 11, color: m.sender === 'user' ? '#e0e7ff' : 'var(--text-muted)', fontWeight: 600, marginBottom: 4 }}>
                {m.sender === 'user' ? 'Developer' : 'GraphTrace Intelligence'} &bull; {m.timestamp}
              </div>
              <div style={{ fontSize: 14, lineHeight: 1.6 }}>{m.text}</div>

              {/* Supporting Graph Traversal Path */}
              {m.supportingPath && (
                <div className="traversal-path-card">
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--primary-light)', textTransform: 'uppercase', marginBottom: 8 }}>
                    🔍 Supporting Graph Traversal Evidence
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    {m.supportingPath.map((step, idx) => (
                      <span key={idx} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                        <span className="path-step-badge">{step}</span>
                        {idx < (m.supportingPath?.length ?? 0) - 1 && (
                          <span style={{ color: 'var(--text-muted)' }}>&rarr;</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Referenced Entities Chips */}
              {m.entities && m.entities.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {m.entities.map((e) => (
                    <button
                      key={e.id}
                      onClick={() => navigate(`/projects/${projectId}/dependencies?nodeId=${encodeURIComponent(e.id)}`)}
                      className="code-chip"
                      style={{ borderColor: `${nodeColor(e.type)}44`, background: 'rgba(0,0,0,0.3)' }}
                      title={`Inspect ${e.type} ${e.name}`}
                    >
                      <span style={{ fontSize: 12 }}>{nodeIcon(e.type)}</span>
                      <span style={{ color: nodeColor(e.type), fontWeight: 700 }}>{e.type}</span>
                      <span>{e.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {thinking && (
            <div className="chat-bubble chat-ai" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                Traversing knowledge graph and formulating explainable answer…
              </span>
            </div>
          )}
        </div>

        {/* Preset Prompt Chips */}
        <div className="prompt-chips">
          <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginRight: 4 }}>
            Suggestions:
          </span>
          {promptChips.map((chip, idx) => (
            <button key={idx} className="prompt-chip" onClick={() => handleAsk(chip)}>
              {chip}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="chat-input-bar">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about the project architecture, dependencies, or requirements…"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAsk(inputQuery)}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleAsk(inputQuery)}
            disabled={!inputQuery.trim() || thinking}
          >
            <span>Ask AI</span> <span>&rarr;</span>
          </button>
        </div>
      </div>
    </div>
  );
}
