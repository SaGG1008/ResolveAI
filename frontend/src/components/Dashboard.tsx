import React, { useState } from 'react';
import type { Incident, DashboardMetrics, AgentEvent } from '../types';

interface DashboardProps {
  metrics: DashboardMetrics;
  incidents: Incident[];
  onIncidentClick: (incident: Incident) => void;
  onNewIncident: () => void;
  onSelectCategory?: (category: string) => void;
}

const COMMON_CATEGORIES = [
  { icon: "🌐", label: "VPN & Network", cat: "Network / VPN" },
  { icon: "📧", label: "Email & Outlook", cat: "Services" },
  { icon: "🔐", label: "Password & Account", cat: "Authentication" },
  { icon: "💻", label: "Computer & OS", cat: "Hardware" },
  { icon: "🔑", label: "Access & Permissions", cat: "Authentication" },
  { icon: "🖨", label: "Printers & Devices", cat: "Hardware" },
];

export const Dashboard: React.FC<DashboardProps> = ({
  metrics,
  incidents,
  onIncidentClick,
  onNewIncident,
  onSelectCategory,
}) => {
  const [filterTab, setFilterTab] = useState<'all' | 'open' | 'waiting' | 'resolved'>('all');

  // Filter incidents based on active tab
  const filteredIncidents = incidents.filter(inc => {
    if (filterTab === 'open') return inc.status === 'investigating' || inc.status === 'diagnosed' || inc.status === 'open';
    if (filterTab === 'waiting') return inc.status === 'pending_approval' || inc.status === 'escalated';
    if (filterTab === 'resolved') return inc.status === 'resolved';
    return true;
  });

  // Recent activity list
  const recentEvents: { event: AgentEvent; incident: Incident }[] = [];
  incidents.forEach(inc => {
    (inc.events || []).forEach(evt => {
      recentEvents.push({ event: evt, incident: inc });
    });
  });
  recentEvents.sort((a, b) => b.event.timestamp.getTime() - a.event.timestamp.getTime());
  const topRecent = recentEvents.slice(0, 5);

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'high':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'medium':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'resolved':
        return { label: 'Resolved', style: 'bg-emerald-50 text-emerald-700 border-emerald-200' };
      case 'escalated':
        return { label: 'Needs IT Support', style: 'bg-red-50 text-red-700 border-red-200' };
      case 'pending_approval':
        return { label: 'Waiting for Approval', style: 'bg-amber-50 text-amber-800 border-amber-300 font-semibold' };
      case 'executing':
        return { label: 'Applying Fix', style: 'bg-blue-50 text-blue-700 border-blue-200' };
      case 'verifying':
        return { label: 'Verifying Fix', style: 'bg-indigo-50 text-indigo-700 border-indigo-200' };
      case 'investigating':
      case 'diagnosed':
        return { label: 'AI Investigating', style: 'bg-blue-50 text-blue-700 border-blue-200' };
      default:
        return { label: 'Open', style: 'bg-slate-50 text-slate-700 border-slate-200' };
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-[1400px] mx-auto text-slate-800">
      {/* 1. EMPLOYEE "HOW CAN WE HELP?" HERO SECTION */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">How can we help you today?</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Search for common IT issues or report a problem for automated diagnosis and resolution.
            </p>
          </div>
          <button
            onClick={onNewIncident}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition active:scale-95 shrink-0"
          >
            + Report an IT Issue
          </button>
        </div>

        {/* Quick Category Tiles */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
          {COMMON_CATEGORIES.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                if (onSelectCategory) onSelectCategory(item.cat);
                onNewIncident();
              }}
              className="p-3 bg-slate-50 hover:bg-blue-50/60 border border-slate-200 hover:border-blue-200 rounded-lg text-left transition flex items-center gap-2.5 group"
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-xs font-medium text-slate-700 group-hover:text-blue-700">
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* 2. COMPACT SUPPORT OVERVIEW METRICS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Open Incidents
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {metrics.activeIncidents}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Currently being investigated
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Resolved by AI
          </div>
          <div className="text-2xl font-bold text-emerald-600 mt-1">
            {metrics.aiResolutions}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Avg time: {metrics.avgResolutionTime} mins
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Waiting for Approval
          </div>
          <div className="text-2xl font-bold text-amber-600 mt-1">
            {incidents.filter(i => i.status === 'pending_approval').length}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Requires operator authorization
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Needs Human Review
          </div>
          <div className="text-2xl font-bold text-slate-800 mt-1">
            {metrics.escalations}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Tier-2 support handover
          </div>
        </div>
      </div>

      {/* 3. MAIN WORKSPACE: INCIDENT QUEUE & RECENT ACTIVITY */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Incident Queue Table (8 cols) */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col justify-between">
          <div>
            <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Incident Queue</h3>
                <p className="text-xs text-slate-500">Track and manage workplace IT tickets</p>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-xs font-medium">
                <button
                  onClick={() => setFilterTab('all')}
                  className={`px-3 py-1 rounded-md transition ${filterTab === 'all' ? 'bg-white text-slate-900 shadow-xs font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  All ({incidents.length})
                </button>
                <button
                  onClick={() => setFilterTab('open')}
                  className={`px-3 py-1 rounded-md transition ${filterTab === 'open' ? 'bg-white text-slate-900 shadow-xs font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  Open
                </button>
                <button
                  onClick={() => setFilterTab('waiting')}
                  className={`px-3 py-1 rounded-md transition ${filterTab === 'waiting' ? 'bg-white text-slate-900 shadow-xs font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  Needs Attention
                </button>
                <button
                  onClick={() => setFilterTab('resolved')}
                  className={`px-3 py-1 rounded-md transition ${filterTab === 'resolved' ? 'bg-white text-slate-900 shadow-xs font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  Resolved
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/75 text-[11px] font-semibold text-slate-600">
                    <th className="px-4 py-3">Incident</th>
                    <th className="px-3 py-3">Priority</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Category</th>
                    <th className="px-3 py-3 text-right">Updated</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-sans">
                  {filteredIncidents.map((inc) => {
                    const statusObj = getStatusBadge(inc.status);
                    return (
                      <tr
                        key={inc.id}
                        onClick={() => onIncidentClick(inc)}
                        className="hover:bg-blue-50/40 cursor-pointer transition"
                      >
                        <td className="px-4 py-3.5">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-slate-500 font-medium text-[11px]">{inc.id}</span>
                            <span className="font-semibold text-slate-900 truncate max-w-[240px]">{inc.title}</span>
                          </div>
                          <div className="text-[11px] text-slate-500 truncate max-w-[300px] mt-0.5">
                            {inc.description}
                          </div>
                        </td>
                        <td className="px-3 py-3.5 whitespace-nowrap">
                          <span className={`px-2 py-0.5 rounded text-[10px] border font-medium ${getPriorityBadge(inc.priority)}`}>
                            {inc.priority.charAt(0).toUpperCase() + inc.priority.slice(1)}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 whitespace-nowrap">
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] border ${statusObj.style}`}>
                            {statusObj.label}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 whitespace-nowrap text-slate-600 text-xs">
                          {inc.category}
                        </td>
                        <td className="px-3 py-3.5 whitespace-nowrap text-right text-slate-500 text-[11px]">
                          {new Date(inc.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: Recent Activity & Service Health (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Recent Activity */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Recent Activity
              </h3>
              <span className="text-[11px] text-slate-400">Live Updates</span>
            </div>

            <div className="space-y-3">
              {topRecent.map(({ event, incident }, idx) => (
                <div key={event.id || idx} className="text-xs flex gap-2.5 items-start">
                  <span className="text-sm mt-0.5">
                    {event.status === 'completed' ? '✓' : event.status === 'failed' ? '⚠' : '→'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-slate-800 font-medium leading-tight">
                      {event.message}
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-1 font-mono">
                      <span>{incident.id}</span>
                      <span>•</span>
                      <span>{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Service Status */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Service Status
              </h3>
              <span className="text-[11px] text-emerald-600 font-medium">All Operational</span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-slate-700">VPN Gateway</span>
                </div>
                <span className="text-slate-400 text-[11px]">Operational</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-slate-700">Email & Outlook</span>
                </div>
                <span className="text-slate-400 text-[11px]">Operational</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-slate-700">Okta Identity & SSO</span>
                </div>
                <span className="text-slate-400 text-[11px]">Operational</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span className="text-slate-700">Internal Auth Proxy</span>
                </div>
                <span className="text-slate-400 text-[11px]">Operational</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
