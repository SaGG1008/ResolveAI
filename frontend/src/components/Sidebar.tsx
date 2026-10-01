import React from 'react';

interface SidebarProps {
  currentPage: 'dashboard' | 'incident';
  onNavigate: (page: 'dashboard' | 'incident') => void;
  onNewIncident: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate, onNewIncident }) => {
  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-screen">
      {/* Logo */}
      <div className="px-6 py-8 border-b border-slate-800">
        <h1 className="text-2xl font-bold">ResolveAI</h1>
        <p className="text-xs text-slate-400 mt-1">IT Service Desk</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className={`w-full text-left px-4 py-3 rounded-lg font-medium transition mb-2 ${
            currentPage === 'dashboard'
              ? 'bg-slate-700 text-white'
              : 'text-slate-300 hover:bg-slate-800'
          }`}
        >
          Dashboard
        </button>
        <button
          onClick={onNewIncident}
          className="w-full px-4 py-3 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition"
        >
          + New Incident
        </button>
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-slate-800 text-xs text-slate-400">
        <p>AI-Powered Resolution</p>
      </div>
    </div>
  );
};
