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
    title: "VPN Session Disconnects",
    desc: "My VPN keeps dropping every 5 minutes and says authentication session expired.",
    priority: "high",
    category: "VPN / Network",
    icon: "🌐"
  },
  {
    title: "Auth Proxy Service Crash",
    desc: "Cannot reach internal git repo; port 8080 connection refused on auth proxy daemon.",
    priority: "medium",
    category: "Services",
    icon: "🔒"
  },
  {
    title: "Laptop Kernel Panic / Hardware Crash",
    desc: "Laptop screen started flickering purple then immediately threw kernel panic stop code 0x889FA.",
    priority: "critical",
    category: "Hardware",
    icon: "💻"
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
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* 1. SIDEBAR */}
      <Sidebar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncidentClick}
        activeIncidentsCount={activeCount}
      />

      {/* 2. MAIN APPLICATION WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-50">
        {selectedIncident ? (
          <IncidentWorkspace
            incident={selectedIncident}
            onBack={handleBackToDashboard}
          />
        ) : (
          <>
            {/* Header */}
            <Header
              title={
                currentPage === 'dashboard' ? 'IT Service Desk' :
                currentPage === 'incidents' ? 'Incident Management Queue' :
                currentPage === 'my_requests' ? 'My Submitted Requests' :
                currentPage === 'knowledge_base' ? 'Knowledge Base & Runbooks' :
                'Corporate Service Status'
              }
              subtitle={
                currentPage === 'dashboard' ? 'Good afternoon, Sagar · How can we help you today?' :
                currentPage === 'incidents' ? 'All employee tickets and autonomous investigation statuses' :
                currentPage === 'my_requests' ? 'Track status and updates on your reported IT issues' :
                currentPage === 'knowledge_base' ? 'Standard operating procedures and troubleshooting guides' :
                'Real-time operational status for corporate IT services'
              }
              onNewIncident={handleNewIncidentClick}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />

            {/* View Switching */}
            <main className="flex-1 overflow-y-auto bg-slate-50">
              {currentPage === 'dashboard' || currentPage === 'incidents' || currentPage === 'my_requests' ? (
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

      {/* 3. REPORT AN ISSUE MODAL */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-xl max-w-xl w-full p-6 text-slate-900">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 font-bold text-lg">
                  +
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Report an IT Problem</h3>
                  <p className="text-xs text-slate-500">ResolveAI will investigate and start diagnostics immediately</p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition"
              >
                ✕
              </button>
            </div>

            {/* Common Incident Presets for Fast Testing */}
            <div className="mt-5">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2.5">
                Common IT Scenarios (Quick Select)
              </div>
              <div className="space-y-2">
                {DEMO_TEMPLATES.map((tmpl, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleCreateScenario(tmpl)}
                    disabled={isCreating}
                    className="w-full text-left p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:border-blue-300 hover:bg-blue-50/40 transition flex items-start gap-3 group active:scale-[0.99]"
                  >
                    <span className="text-xl shrink-0 mt-0.5">{tmpl.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-xs text-slate-900 group-hover:text-blue-700 transition flex items-center justify-between">
                        <span>{tmpl.title}</span>
                        <span className="text-xs text-blue-600 font-medium">Select →</span>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5 line-clamp-1">{tmpl.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Problem Description */}
            <form onSubmit={handleCreateCustom} className="mt-5 pt-4 border-t border-slate-200 space-y-3">
              <label className="block text-xs font-semibold text-slate-700">
                Or describe your IT problem in your own words
              </label>
              <textarea
                value={customDescription}
                onChange={(e) => setCustomDescription(e.target.value)}
                placeholder="E.g., My VPN keeps disconnecting when I try to open Jira, or Outlook won't sync emails..."
                rows={3}
                className="w-full p-3 bg-white border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 placeholder:text-slate-400 resize-none leading-relaxed"
              />
              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isCreating}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating || !customDescription.trim()}
                  className="px-5 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition disabled:opacity-50 active:scale-95"
                >
                  {isCreating ? 'Submitting...' : 'Submit Request'}
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
