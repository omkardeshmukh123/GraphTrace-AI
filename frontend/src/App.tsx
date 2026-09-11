import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppShell from './components/AppShell';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import GraphExplorer from './pages/GraphExplorer';
import Traceability from './pages/Traceability';
import Dependencies from './pages/Dependencies';
import AskAI from './pages/AskAI';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/projects/:projectId" element={<Dashboard />} />
          <Route path="/projects/:projectId/graph" element={<GraphExplorer />} />
          <Route path="/projects/:projectId/traceability" element={<Traceability />} />
          <Route path="/projects/:projectId/dependencies" element={<Dependencies />} />
          <Route path="/projects/:projectId/ask" element={<AskAI />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
