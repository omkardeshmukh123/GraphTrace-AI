import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppShell from './components/AppShell';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import GraphExplorer from './pages/GraphExplorer';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/projects/:projectId" element={<Dashboard />} />
          <Route path="/projects/:projectId/graph" element={<GraphExplorer />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
