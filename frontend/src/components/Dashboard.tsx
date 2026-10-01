import React from 'react';
import type { Incident, DashboardMetrics, AgentEvent } from '../types';
import { AgentPipelineBar } from './AgentPipelineBar';

interface DashboardProps {
  metrics: DashboardMetrics;
  incidents: Incident[];
  onIncidentClick: (incident: Incident) => void;
  onNewIncident: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  metrics,
  incidents,
  onIncidentClick,
  onNewIncident,
}) => {
  // Find the most relevant active incident (investigating or pending approval) for the spotlight card
  const activeIncident = incidents.find(
    i => i.status === 'investigating' || i.status === 'diagnosed' || i.status === 'pending_approval' || i.status === 'executing'
  ) || incidents[0];

  // Aggregate recent agent events across all incidents for the AI Operations Feed
  const recentAgentEvents: { event: AgentEvent; incidentId: string }[] = [];
  incidents.forEach(inc => {
    (inc.events || []).forEach(evt => {
      recentAgentEvents.push({
        event: evt,
        incidentId: inc.id,
      });
    });
  });
  // Sort descending by timestamp
  recentAgentEvents.sort((a, b) => b.event.timestamp.getTime() - a.event.timestamp.getTime());
  const topAgentEvents = recentAgentEvents.slice(0, 5);

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-rose-950/60 text-rose-300 border-rose-800/80 font-bold';
      case 'high':
        return 'bg-amber-950/60 text-amber-300 border-amber-800/80 font-semibold';
      case 'medium':
        return 'bg-blue-950/60 text-blue-300 border-blue-800/80';
      default:
        return 'bg-slate-800/80 text-slate-300 border-slate-700';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'bg-emerald-950/60 text-emerald-300 border-emerald-800/80';
      case 'escalated':
        return 'bg-rose-950/60 text-rose-300 border-rose-800/80';
      case 'pending_approval':
        return 'bg-amber-950/60 text-amber-300 border-amber-800/80 animate-pulse';
      case 'executing':
      case 'verifying':
        return 'bg-indigo-950/60 text-indigo-300 border-indigo-800/80';
      case 'investigating':
      case 'diagnosed':
        return 'bg-blue-950/60 text-blue-300 border-blue-800/80';
      default:
        return 'bg-slate-800/80 text-slate-400 border-slate-700';
    }
  };

  const getAgentLabel = (agent: string) => {
    switch (agent) {
      case 'triage':
        return 'Triage Agent';
      case 'investigation':
        return 'Investigation Agent';
      case 'diagnosis':
        return 'Diagnosis Agent';
      case 'action_planner':
        return 'Action Planner';
      case 'verification':
        return 'Verification Agent';
      default:
        return 'Autonomous Agent';
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* 1. TOP OPERATIONAL KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Incidents */}
        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>ACTIVE INCIDENTS</span>
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
          </div>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">{metrics.activeIncidents}</span>
            <span className="text-[11px] font-mono text-blue-400 font-medium">investigating</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-800/60 pt-2 mt-1">
            <span>Live autonomous queue</span>
            <span className="text-slate-300 font-mono">0 pending queue</span>
          </div>
        </div>

        {/* Card 2: AI Resolutions */}
        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>AI RESOLUTIONS</span>
            <span className="text-emerald-400 text-xs font-bold">✓ 92%</span>
          </div>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">{metrics.aiResolutions}</span>
            <span className="text-[11px] font-mono text-emerald-400 font-medium">auto-resolved</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-800/60 pt-2 mt-1">
            <span>Avg resolution time</span>
            <span className="text-emerald-400 font-mono">{metrics.avgResolutionTime}m</span>
          </div>
        </div>

        {/* Card 3: Human Escalations */}
        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>HUMAN ESCALATIONS</span>
            <span className="text-amber-400 text-xs font-mono">12.5% rate</span>
          </div>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">{metrics.escalations}</span>
            <span className="text-[11px] font-mono text-amber-400 font-medium">tier-2 review</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-800/60 pt-2 mt-1">
            <span>Safety containment</span>
            <span className="text-slate-300 font-mono">100% policy strict</span>
          </div>
        </div>

        {/* Card 4: System Health */}
        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>SYSTEM HEALTH</span>
            <span className="text-emerald-400 font-mono font-bold">● 99.8%</span>
          </div>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">8 / 8</span>
            <span className="text-[11px] font-mono text-emerald-400 font-medium">services online</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-800/60 pt-2 mt-1">
            <span>Gateway telemetry</span>
            <span className="text-emerald-400 font-mono">24ms latency</span>
          </div>
        </div>
      </div>

      {/* 2. AGENT PIPELINE VISUALIZATION */}
      <div>
        <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
          <span>Multi-Agent Autonomous Pipeline Execution Flow</span>
          <span className="text-blue-400">Deterministic Guardrails Enabled</span>
        </div>
        <AgentPipelineBar currentStatus={activeIncident ? activeIncident.status : 'open'} />
      </div>

      {/* 3. MAIN COMMAND CENTER GRID (Balanced 2-Column Layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: Spotlight Card + Recent Incident Queue (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Spotlight: Currently Investigating */}
          {activeIncident && (
            <div className="bg-[#0e1320] border border-blue-900/50 rounded-xl p-5 shadow-md relative overflow-hidden">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                <div className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-ping"></span>
                  <span className="text-xs font-mono font-bold uppercase tracking-wider text-blue-400">
                    Live Incident Spotlight
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-900 border border-slate-700 text-slate-200">
                    {activeIncident.id}
                  </span>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono border ${getStatusBadge(activeIncident.status)}`}>
                  {activeIncident.status.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>

              <div className="mt-4">
                <h3 className="text-base font-bold text-white mb-1.5">{activeIncident.title}</h3>
                <p className="text-xs text-slate-300 line-clamp-2 mb-4 leading-relaxed">
                  {activeIncident.description}
                </p>

                {/* Hypothesis & Evidence Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                  <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                    <div className="text-[10px] font-mono text-slate-400 uppercase mb-1">Current Diagnosis</div>
                    <div className="text-xs font-semibold text-cyan-300">
                      {activeIncident.diagnosis?.likelyCause || "Analyzing logs and correlates..."}
                    </div>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3">
                    <div className="text-[10px] font-mono text-slate-400 uppercase mb-1">Grounded Evidence</div>
                    <div className="text-xs font-semibold text-emerald-300 flex items-center justify-between">
                      <span>{activeIncident.evidence?.length || 0} verified sources</span>
                      {activeIncident.diagnosis && (
                        <span className="font-mono text-[11px] text-cyan-400">{activeIncident.diagnosis.confidence}% conf</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* CTA Action */}
                <div className="flex items-center justify-between pt-2">
                  <div className="text-[11px] text-slate-400 font-mono">
                    Assigned: <span className="text-slate-200 font-semibold">{activeIncident.category}</span>
                  </div>
                  <button
                    onClick={() => onIncidentClick(activeIncident)}
                    className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-sm shadow-blue-500/20 active:scale-95"
                  >
                    <span>Inspect Investigation Workspace</span>
                    <span>→</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Incident Queue Table */}
          <div className="bg-[#0e1320] border border-slate-800 rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wide">Incident Queue</h3>
                <p className="text-[11px] text-slate-400 font-mono">Real-time status of all reported workplace incidents</p>
              </div>
              <button
                onClick={onNewIncident}
                className="text-xs text-blue-400 hover:text-blue-300 font-mono font-semibold"
              >
                + Create
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800/80 bg-slate-950/50 text-[10px] font-mono uppercase tracking-wider text-slate-400">
                    <th className="px-4 py-3">Incident</th>
                    <th className="px-3 py-3">Priority</th>
                    <th className="px-3 py-3">Category</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3 text-right">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {incidents.map((inc) => (
                    <tr
                      key={inc.id}
                      onClick={() => onIncidentClick(inc)}
                      className="hover:bg-slate-800/40 cursor-pointer transition group"
                    >
                      <td className="px-4 py-3.5">
                        <div className="font-bold text-slate-200 group-hover:text-blue-400 transition flex items-center gap-2">
                          <span className="font-mono text-xs text-slate-400">{inc.id}</span>
                          <span className="truncate max-w-[220px]">{inc.title}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 truncate max-w-[280px] mt-0.5 font-sans">
                          {inc.description}
                        </div>
                      </td>
                      <td className="px-3 py-3.5 whitespace-nowrap">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${getPriorityBadge(inc.priority)}`}>
                          {inc.priority.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-3 py-3.5 whitespace-nowrap text-slate-300 text-[11px]">
                        {inc.category}
                      </td>
                      <td className="px-3 py-3.5 whitespace-nowrap">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono border ${getStatusBadge(inc.status)}`}>
                          {inc.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-3 py-3.5 whitespace-nowrap text-right text-[11px] text-slate-400 font-mono">
                        {new Date(inc.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Live AI Operations Feed + Live System Health (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* AI Operations Center Feed */}
          <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-indigo-400 text-xs">✦</span>
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                  AI Operations Stream
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">Live Telemetry</span>
            </div>

            <div className="mt-3 space-y-3">
              {topAgentEvents.map(({ event, incidentId }, idx) => (
                <div key={event.id || idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-950/70 border border-blue-800/60 text-blue-300">
                        {getAgentLabel(event.agent)}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">{incidentId}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {event.message}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* System Services Monitor */}
          <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 text-xs">◈</span>
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                  System Health & Services
                </h3>
              </div>
              <span className="text-[10px] font-mono text-emerald-400">8 / 8 Online</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200 font-medium">VPN Gateway (Palo Alto)</span>
                </div>
                <div className="font-mono text-[11px] text-slate-400">24ms</div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                  <span className="text-slate-200 font-medium">Internal Auth Proxy (Port 8080)</span>
                </div>
                <div className="font-mono text-[11px] text-amber-400">Auto-Managed</div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200 font-medium">Okta Enterprise SSO</span>
                </div>
                <div className="font-mono text-[11px] text-slate-400">42ms</div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/50 border border-slate-800/60">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200 font-medium">Core DNS Resolver</span>
                </div>
                <div className="font-mono text-[11px] text-slate-400">8ms</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
