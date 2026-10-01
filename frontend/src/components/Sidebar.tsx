import React from 'react';

export type NavigationPage = 
  | 'dashboard' 
  | 'incidents' 
  | 'my_requests'
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
    <aside className="w-64 bg-[#0f172a] text-slate-300 flex flex-col h-screen select-none shrink-0 z-20 border-r border-slate-800">
      {/* Brand & Organization Title */}
      <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white text-sm shadow-sm">
            R
          </div>
          <div>
            <div className="font-bold text-white tracking-tight text-sm">
              ResolveAI
            </div>
            <div className="text-[11px] text-slate-400">
              IT Service Desk
            </div>
          </div>
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="px-4 pt-4 pb-2">
        <button
          onClick={onNewIncident}
          className="w-full py-2.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs tracking-wide transition flex items-center justify-center gap-2 shadow-sm active:scale-[0.98]"
        >
          <span className="text-sm font-bold leading-none">+</span>
          <span>Report an Issue</span>
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto space-y-6 text-xs font-medium">
        {/* Home */}
        <div>
          <div className="px-3 pb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Home
          </div>
          <button
            onClick={() => onNavigate('dashboard')}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition ${
              currentPage === 'dashboard'
                ? 'bg-slate-800 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span>🏠</span>
              <span>Overview</span>
            </div>
          </button>
        </div>

        {/* Requests */}
        <div>
          <div className="px-3 pb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Requests
          </div>
          <div className="space-y-1">
            <button
              onClick={() => onNavigate('incidents')}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition ${
                currentPage === 'incidents'
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span>📋</span>
                <span>Incident Queue</span>
              </div>
              {activeIncidentsCount > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-blue-600/30 text-blue-300">
                  {activeIncidentsCount}
                </span>
              )}
            </button>

            <button
              onClick={() => onNavigate('my_requests')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition ${
                currentPage === 'my_requests'
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <span>👤</span>
              <span>My Requests</span>
            </button>
          </div>
        </div>

        {/* Knowledge */}
        <div>
          <div className="px-3 pb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Knowledge
          </div>
          <button
            onClick={() => onNavigate('knowledge_base')}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition ${
              currentPage === 'knowledge_base'
                ? 'bg-slate-800 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <span>📚</span>
            <span>Knowledge Base</span>
          </button>
        </div>

        {/* Services & Admin */}
        <div>
          <div className="px-3 pb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Services & Health
          </div>
          <button
            onClick={() => onNavigate('system_health')}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition ${
              currentPage === 'system_health'
                ? 'bg-slate-800 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span>⚡</span>
              <span>Service Status</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-medium">Operational</span>
          </button>
        </div>
      </nav>

      {/* Footer Support Card */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span className="text-[11px] text-slate-300 font-medium">AI Support Active</span>
          </div>
          <span className="text-[10px] text-slate-400">v1.0</span>
        </div>
      </div>
    </aside>
  );
};
