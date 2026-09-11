import { useState } from 'react';
import { api } from '../api';
import type { ProjectSummary } from '../api';

interface Props {
  onClose: () => void;
  onSuccess: (project: ProjectSummary) => void;
}

type Tab = 'zip' | 'json';

export default function UploadModal({ onClose, onSuccess }: Props) {
  const [tab, setTab] = useState<Tab>('zip');
  const [file, setFile] = useState<File | null>(null);
  const [reqFile, setReqFile] = useState<File | null>(null);
  const [jsonText, setJsonText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  async function handleSubmit() {
    setError('');
    setLoading(true);
    try {
      if (tab === 'zip') {
        if (!file) {
          setError('Please select a project ZIP archive.');
          setLoading(false);
          return;
        }
        const fd = new FormData();
        fd.append('repository', file);
        if (reqFile) fd.append('requirements', reqFile);
        const project = await api.analyzeProject(fd);
        onSuccess(project);
      } else {
        if (!jsonText.trim()) {
          setError('Please paste a valid ArtifactGraph JSON.');
          setLoading(false);
          return;
        }
        const graph = JSON.parse(jsonText);
        const project = await api.importProject(graph);
        onSuccess(project);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed. Please check backend logs.');
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f?.name.endsWith('.zip')) {
      setFile(f);
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-window">
        {/* Header */}
        <div style={{ padding: '24px 28px 18px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#fff' }}>Add Project</h2>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
              Upload source repository or import artifact knowledge graph
            </p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: 20, cursor: 'pointer', padding: 4 }}
          >
            ✕
          </button>
        </div>

        {/* Tab Selectors */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', padding: '0 28px', background: 'rgba(0,0,0,0.15)' }}>
          <button
            style={{
              padding: '12px 18px',
              fontSize: 13,
              fontWeight: 600,
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: tab === 'zip' ? '#fff' : 'var(--text-muted)',
              borderBottom: `2px solid ${tab === 'zip' ? 'var(--primary-light)' : 'transparent'}`,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
            onClick={() => setTab('zip')}
          >
            <span>📦</span> Upload Source ZIP
          </button>
          <button
            style={{
              padding: '12px 18px',
              fontSize: 13,
              fontWeight: 600,
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: tab === 'json' ? '#fff' : 'var(--text-muted)',
              borderBottom: `2px solid ${tab === 'json' ? 'var(--primary-light)' : 'transparent'}`,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
            onClick={() => setTab('json')}
          >
            <span>📋</span> Import JSON Contract
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px 28px' }}>
          {error && (
            <div style={{ padding: '12px 16px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 8, color: '#fda4af', fontSize: 13, marginBottom: 18 }}>
              ⚠️ {error}
            </div>
          )}

          {tab === 'zip' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              {/* Dropzone */}
              <div
                className={`dropzone ${dragOver ? 'active' : ''}`}
                onClick={() => document.getElementById('zip-input-dialog')?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
              >
                <div style={{ fontSize: 36, marginBottom: 10 }}>{file ? '✅' : '📁'}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#fff', marginBottom: 4 }}>
                  {file ? file.name : 'Drop your repository .zip here'}
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
                  {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB archive selected` : 'or click to browse filesystem (max 20 MB)'}
                </div>
                <input
                  id="zip-input-dialog"
                  type="file"
                  accept=".zip"
                  style={{ display: 'none' }}
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
              </div>

              {/* Requirements File Upload */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <label style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Requirements Document (Optional &mdash; .md SRS / Spec)
                </label>
                <input
                  type="file"
                  accept=".md,.txt"
                  onChange={(e) => setReqFile(e.target.files?.[0] ?? null)}
                  style={{
                    background: 'var(--bg-raised)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 8,
                    padding: '8px 12px',
                    color: 'var(--text-secondary)',
                    fontSize: 13,
                    outline: 'none'
                  }}
                />
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-secondary)' }}>
                ArtifactGraph JSON Specification
              </label>
              <textarea
                value={jsonText}
                onChange={(e) => setJsonText(e.target.value)}
                placeholder='{"project_id": "demo", "nodes": [...], "relationships": [...]}'
                rows={9}
                style={{
                  width: '100%',
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  padding: 14,
                  color: '#fff',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 12,
                  resize: 'vertical',
                  outline: 'none',
                }}
              />
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{ padding: '16px 28px 24px', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12, background: 'rgba(0,0,0,0.1)' }}>
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                Analyzing Project…
              </>
            ) : (
              tab === 'zip' ? 'Analyze Repository' : 'Import Graph'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
