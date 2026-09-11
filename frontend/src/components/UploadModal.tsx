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
        if (!file) { setError('Please select a ZIP file.'); setLoading(false); return; }
        const fd = new FormData();
        fd.append('repository', file);
        if (reqFile) fd.append('requirements', reqFile);
        const project = await api.analyzeProject(fd);
        onSuccess(project);
      } else {
        if (!jsonText.trim()) { setError('Please paste a valid ArtifactGraph JSON.'); setLoading(false); return; }
        const graph = JSON.parse(jsonText);
        const project = await api.importProject(graph);
        onSuccess(project);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f?.name.endsWith('.zip')) setFile(f);
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-title">Add Project</div>

        <div className="modal-tabs">
          <button className={`modal-tab ${tab === 'zip' ? 'active' : ''}`} onClick={() => setTab('zip')}>
            📦 Upload ZIP
          </button>
          <button className={`modal-tab ${tab === 'json' ? 'active' : ''}`} onClick={() => setTab('json')}>
            📋 Import JSON
          </button>
        </div>

        {tab === 'zip' ? (
          <>
            <div
              className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
              onClick={() => document.getElementById('zip-input')?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
            >
              <div className="drop-zone-icon">{file ? '✅' : '📁'}</div>
              <div className="drop-zone-text">
                {file ? file.name : 'Drop your project ZIP here'}
              </div>
              <div className="drop-zone-sub">or click to browse (max 20 MB)</div>
              <input
                id="zip-input"
                type="file"
                accept=".zip"
                style={{ display: 'none' }}
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>

            <div className="form-field">
              <label className="form-label">Requirements file (optional — .md SRS)</label>
              <input
                type="file"
                accept=".md,.txt"
                className="input"
                style={{ padding: '5px' }}
                onChange={(e) => setReqFile(e.target.files?.[0] ?? null)}
              />
            </div>
          </>
        ) : (
          <div className="form-field">
            <label className="form-label">ArtifactGraph JSON</label>
            <textarea
              className="input"
              rows={10}
              style={{ resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: 11 }}
              placeholder='{"project_id": "...", "nodes": [...], "relationships": [...]}'
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
            />
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Analysing…</> : 'Analyse'}
          </button>
        </div>
      </div>
    </div>
  );
}
