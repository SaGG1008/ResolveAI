import React from 'react';

export type NavigationPage = 
  | 'dashboard' 
  | 'incidents' 
  | 'agent_activity' 
  | 'knowledge_base' 
  | 'system_health';

interface SidebarProps {
  currentPage: NavigationPage;
  onNavigate: (page: NavigationPage) => void;
  onNewIncident: () => void;
  activeIncidentsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  onNewIncident,
  activeIncidentsCount,
}) => {
  return (
    <aside className="w-64 bg-[#090d16] border-r border-slate-800/80 text-slate-300 flex flex-col h-screen select-none shrink-0 z-20">
      {/* Brand & Mission Title */}
      <div className="px-5 py-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-blue-500/20 border border-blue-400/30">
            R
          </div>
          <div>
            <div className="font-bold text-white tracking-wide text-base flex items-center gap-1.5">
              RESOLVE<span className="text-blue-400">AI</span>
            </div>
            <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400">
              Autonomous IT Ops
            </div>
          </div>
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="px-4 pt-4 pb-2">
        <button
          onClick={onNewIncident}
          className="w-full py-2.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs tracking-wide transition flex items-center justify-center gap-2 shadow-md shadow-blue-600/30 border border-blue-400/30 active:scale-[0.98]"
        >
          <span className="text-sm font-bold leading-none">+</span>
          <span>New Incident</span>
        </button>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto space-y-6 text-xs font-medium">
        {/* Main Section */}
        <div>
          <div className="px-3 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Command Center
          </div>
          <button
            onClick={() => onNavigate('dashboard')}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition ${
              currentPage === 'dashboard'
                ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="text-sm">⌂</span>
              <span>Overview</span>
            </div>
            {activeIncidentsCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/20 text-blue-400 border border-blue-400/30">
                {activeIncidentsCount}
              </span>
            )}
          </button>
        </div>

        {/* Incidents Section */}
        <div>
          <div className="px-3 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Incidents
          </div>
          <div className="space-y-1">
            <button
              onClick={() => onNavigate('incidents')}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition ${
                currentPage === 'incidents'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="text-amber-400 text-xs">◉</span>
                <span>Incident Queue</span>
              </div>
            </button>
          </div>
        </div>

        {/* AI Operations */}
        <div>
          <div className="px-3 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            AI Operations
          </div>
          <div className="space-y-1">
            <button
              onClick={() => onNavigate('agent_activity')}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition ${
                currentPage === 'agent_activity'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="text-indigo-400 text-xs">✦</span>
                <span>Agent Telemetry</span>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </button>

            <button
              onClick={() => onNavigate('knowledge_base')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md transition ${
                currentPage === 'knowledge_base'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <span className="text-cyan-400 text-xs">◎</span>
              <span>Knowledge Base & Runbooks</span>
            </button>
          </div>
        </div>

        {/* System Health */}
        <div>
          <div className="px-3 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Infrastructure
          </div>
          <button
            onClick={() => onNavigate('system_health')}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition ${
              currentPage === 'system_health'
                ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="text-emerald-400 text-xs">◈</span>
              <span>System & Service Health</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400">8/8</span>
          </button>
        </div>
      </nav>

      {/* AI Engine Status Indicator Footer */}
      <div className="p-3.5 border-t border-slate-800/80 bg-[#070a11]">
        <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <div>
              <div className="text-[11px] font-bold text-slate-200">AI Engine Active</div>
              <div className="text-[9px] font-mono text-slate-400">5 Agents Standby</div>
            </div>
          </div>
          <div className="text-[9px] font-mono text-slate-400 px-1.5 py-0.5 bg-slate-800/80 rounded border border-slate-700/50">
            v1.0
          </div>
        </div>
      </div>
    </aside>
  );
};
