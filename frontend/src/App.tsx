import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { KPICard, RecentIncidentsTable } from './components/Dashboard';
import { IncidentWorkspace } from './components/IncidentWorkspace';
import type { Incident, DashboardMetrics } from './types';
import { mockIncidents, mockMetrics } from './mockData';
import { api } from './services/api';

type AppPage = 'dashboard' | 'incident';

interface AppState {
  currentPage: AppPage;
  selectedIncident: Incident | null;
}

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
  const [state, setState] = useState<AppState>({
    currentPage: 'dashboard',
    selectedIncident: null,
  });

  const [incidents, setIncidents] = useState<Incident[]>(mockIncidents);
  const [metrics, setMetrics] = useState<DashboardMetrics>(mockMetrics);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customDescription, setCustomDescription] = useState('');
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

  const handleNavigate = (page: AppPage) => {
    setState({
      currentPage: page,
      selectedIncident: null,
    });
    if (page === 'dashboard') {
      loadData();
    }
  };

  const handleNewIncidentClick = () => {
    setIsModalOpen(true);
  };

  const handleIncidentClick = (incident: Incident) => {
    setState({
      currentPage: 'incident',
      selectedIncident: incident,
    });
  };

  const handleBackToDashboard = () => {
    handleNavigate('dashboard');
  };

  const handleCreateScenario = async (template: typeof DEMO_TEMPLATES[0]) => {
    setIsCreating(true);
    try {
      const newInc = await api.createIncident(template.desc, template.title, template.priority, template.category);
      setIsModalOpen(false);
      setState({
        currentPage: 'incident',
        selectedIncident: newInc,
      });
      loadData();
    } catch (err) {
      console.error('Failed to create incident:', err);
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
      setState({
        currentPage: 'incident',
        selectedIncident: newInc,
      });
      loadData();
    } catch (err) {
      console.error('Failed to create custom incident:', err);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <Sidebar
        currentPage={state.currentPage}
        onNavigate={handleNavigate}
        onNewIncident={handleNewIncidentClick}
      />

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {state.currentPage === 'dashboard' ? (
          <div className="p-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Dashboard</h1>
                <p className="text-slate-600">AI IT Service Desk — Autonomous Multi-Agent Resolution Engine</p>
              </div>
              <button
                onClick={handleNewIncidentClick}
                className="px-5 py-2.5 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700 transition"
              >
                + New Incident
              </button>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <KPICard
                label="Active Incidents"
                value={metrics.activeIncidents}
                subtext="Currently investigating or executing"
                trend="stable"
              />
              <KPICard
                label="AI Resolutions"
                value={metrics.aiResolutions}
                subtext="Resolved autonomously"
                trend="up"
              />
              <KPICard
                label="Escalations"
                value={metrics.escalations}
                subtext="Requiring human tier-2 review"
                trend="down"
              />
            </div>

            {/* Recent Incidents */}
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-4">Recent Incidents</h2>
              <RecentIncidentsTable
                incidents={incidents}
                onIncidentClick={handleIncidentClick}
              />
            </div>
          </div>
        ) : state.selectedIncident ? (
          <IncidentWorkspace
            incident={state.selectedIncident}
            onBack={handleBackToDashboard}
          />
        ) : null}
      </div>

      {/* New Incident Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-xl w-full p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="text-xl font-bold text-slate-900">Create New IT Incident</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            {/* Quick Demo Templates */}
            <div className="mt-4">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Quick Demo Scenarios
              </div>
              <div className="space-y-2">
                {DEMO_TEMPLATES.map((tmpl, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleCreateScenario(tmpl)}
                    disabled={isCreating}
                    className="w-full text-left p-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition flex flex-col gap-1"
                  >
                    <div className="font-semibold text-sm text-slate-900">{tmpl.title}</div>
                    <div className="text-xs text-slate-600 line-clamp-1">{tmpl.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Issue Description */}
            <form onSubmit={handleCreateCustom} className="mt-6 pt-4 border-t border-slate-100">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Or Type Custom Issue
              </div>
              <textarea
                value={customDescription}
                onChange={(e) => setCustomDescription(e.target.value)}
                placeholder="Describe the employee IT issue in natural language..."
                rows={3}
                className="w-full p-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex justify-end gap-3 mt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isCreating}
                  className="px-4 py-2 text-sm text-slate-700 bg-slate-100 hover:bg-slate-200 font-medium rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating || !customDescription.trim()}
                  className="px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
                >
                  {isCreating ? 'Dispatching Agents...' : 'Submit & Investigate'}
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
