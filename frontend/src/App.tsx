import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar, type NavigationPage } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { IncidentWorkspace } from './components/IncidentWorkspace';
import { KnowledgeBaseView } from './components/KnowledgeBaseView';
import { SystemHealthView } from './components/SystemHealthView';
import type { Incident, DashboardMetrics } from './types';
import { mockIncidents, mockMetrics } from './mockData';
import { api } from './services/api';

const DEMO_TEMPLATES = [
  {
    title: "Scenario 1: VPN Session Lock (Auto-Resolution)",
    desc: "My VPN keeps dropping every 5 minutes and says authentication session expired.",
    priority: "high",
    category: "Network / VPN"
  },
  {
    title: "Scenario 2: Auth Proxy Crash (Human Approval Gate)",
    desc: "Cannot reach internal git repo; port 8080 connection refused on auth proxy daemon.",
    priority: "medium",
    category: "Services"
  },
  {
    title: "Scenario 3: Hardware Memory Crash (Tier-2 Escalation)",
    desc: "Laptop screen started flickering purple then immediately threw kernel panic stop code 0x889FA.",
    priority: "critical",
    category: "Hardware"
  }
];

function App() {
  const [currentPage, setCurrentPage] = useState<NavigationPage>('dashboard');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>(mockIncidents);
  const [metrics, setMetrics] = useState<DashboardMetrics>(mockMetrics);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customDescription, setCustomDescription] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [fetchedIncidents, fetchedMetrics] = await Promise.all([
        api.getIncidents(),
        api.getDashboardMetrics()
      ]);
      setIncidents(fetchedIncidents);
      setMetrics(fetchedMetrics);
    } catch (err) {
      console.warn('Failed to load live backend data:', err);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        const [fetchedIncidents, fetchedMetrics] = await Promise.all([
          api.getIncidents(),
          api.getDashboardMetrics()
        ]);
        if (isMounted) {
          setIncidents(fetchedIncidents);
          setMetrics(fetchedMetrics);
        }
      } catch (err) {
        console.warn('Failed to load live backend data:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleNavigate = (page: NavigationPage) => {
    setCurrentPage(page);
    setSelectedIncident(null);
    if (page === 'dashboard' || page === 'incidents') {
      loadData();
    }
  };

  const handleIncidentClick = (incident: Incident) => {
    setSelectedIncident(incident);
  };

  const handleBackToDashboard = () => {
    setSelectedIncident(null);
    loadData();
  };

  const handleNewIncidentClick = () => {
    setIsModalOpen(true);
  };

  const handleCreateScenario = async (template: typeof DEMO_TEMPLATES[0]) => {
    setIsCreating(true);
    try {
      const newInc = await api.createIncident(template.desc, template.title, template.priority, template.category);
      setIsModalOpen(false);
      setSelectedIncident(newInc);
      loadData();
    } catch (err) {
      console.error('Failed to create scenario incident:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleCreateCustom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customDescription.trim()) return;

    setIsCreating(true);
    try {
      const newInc = await api.createIncident(customDescription.trim());
      setCustomDescription('');
      setIsModalOpen(false);
      setSelectedIncident(newInc);
      loadData();
    } catch (err) {
      console.error('Failed to create custom incident:', err);
    } finally {
      setIsCreating(false);
    }
  };

  // Filtered incidents for search query
  const filteredIncidents = incidents.filter(inc => {
    if (!searchQuery) return true;
    return (
      inc.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.category.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const activeCount = incidents.filter(
    i => i.status !== 'resolved' && i.status !== 'escalated'
  ).length;

  return (
    <div className="flex h-screen bg-[#0b0f19] text-slate-100 overflow-hidden font-sans">
      {/* 1. SIDEBAR */}
      <Sidebar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncidentClick}
        activeIncidentsCount={activeCount}
      />

      {/* 2. MAIN APPLICATION WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {selectedIncident ? (
          <IncidentWorkspace
            incident={selectedIncident}
            onBack={handleBackToDashboard}
          />
        ) : (
          <>
            {/* Command Center Header */}
            <Header
              title={
                currentPage === 'dashboard' ? 'Command Center Overview' :
                currentPage === 'incidents' ? 'Active Incident Queue' :
                currentPage === 'agent_activity' ? 'Autonomous Agent Telemetry' :
                currentPage === 'knowledge_base' ? 'Knowledge Base & Runbooks' :
                'Infrastructure & Service Health'
              }
              subtitle="ResolveAI Autonomous IT Service Desk"
              onNewIncident={handleNewIncidentClick}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />

            {/* View Switching */}
            <main className="flex-1 overflow-y-auto bg-[#0b0f19]">
              {currentPage === 'dashboard' || currentPage === 'incidents' || currentPage === 'agent_activity' ? (
                <Dashboard
                  metrics={metrics}
                  incidents={filteredIncidents}
                  onIncidentClick={handleIncidentClick}
                  onNewIncident={handleNewIncidentClick}
                />
              ) : currentPage === 'knowledge_base' ? (
                <KnowledgeBaseView />
              ) : (
                <SystemHealthView />
              )}
            </main>
          </>
        )}
      </div>

      {/* 3. NEW INCIDENT MODAL / DRAWER */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#0e1320] border border-slate-700/80 rounded-2xl shadow-2xl max-w-xl w-full p-6 text-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold">
                  +
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Create New IT Incident</h3>
                  <p className="text-[11px] text-slate-400 font-mono">Dispatches autonomous multi-agent investigation</p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Quick Demo Templates */}
            <div className="mt-4">
              <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 mb-2">
                Quick Demo Scenario Presets
              </div>
              <div className="space-y-2">
                {DEMO_TEMPLATES.map((tmpl, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleCreateScenario(tmpl)}
                    disabled={isCreating}
                    className="w-full text-left p-3 rounded-xl border border-slate-800 bg-slate-950/60 hover:border-blue-500/80 hover:bg-blue-950/20 transition flex flex-col gap-1 group active:scale-[0.99]"
                  >
                    <div className="font-semibold text-xs text-slate-200 group-hover:text-blue-300 transition flex items-center justify-between">
                      <span>{tmpl.title}</span>
                      <span className="text-[10px] font-mono text-slate-500 group-hover:text-blue-400">Launch →</span>
                    </div>
                    <div className="text-[11px] text-slate-400 line-clamp-1">{tmpl.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Issue Description */}
            <form onSubmit={handleCreateCustom} className="mt-5 pt-4 border-t border-slate-800 space-y-3">
              <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                Or Enter Custom Employee Issue
              </div>
              <textarea
                value={customDescription}
                onChange={(e) => setCustomDescription(e.target.value)}
                placeholder="Describe the employee IT problem in natural language (e.g. 'My email stopped syncing on Outlook after password reset')..."
                rows={3}
                className="w-full p-3 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500 placeholder:text-slate-500 resize-none leading-relaxed"
              />
              <div className="flex justify-end gap-2.5 pt-1">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isCreating}
                  className="px-4 py-2 text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating || !customDescription.trim()}
                  className="px-5 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-md shadow-blue-600/30 transition disabled:opacity-50 active:scale-95"
                >
                  {isCreating ? 'Dispatching Agents...' : 'Start Autonomous Investigation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
