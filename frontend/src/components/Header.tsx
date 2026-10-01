import React from 'react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onNewIncident: () => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle = "Autonomous IT Operations",
  onNewIncident,
  searchQuery = '',
  onSearchChange,
}) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur px-6 flex items-center justify-between shrink-0 z-10">
      {/* Title & Context */}
      <div className="flex items-center gap-4">
        <div>
          <div className="text-base font-bold text-slate-100 flex items-center gap-2">
            {title}
          </div>
          <div className="text-[11px] text-slate-400 font-mono">
            {subtitle}
          </div>
        </div>
      </div>

      {/* Live System Telemetry Chips & Actions */}
      <div className="flex items-center gap-3">
        {/* Search Bar */}
        {onSearchChange && (
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search incidents, tools, KB..."
              className="w-56 bg-slate-900/90 border border-slate-700/80 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500 transition placeholder:text-slate-500"
            />
            <span className="absolute right-2.5 top-2 text-slate-500 text-xs">🔍</span>
          </div>
        )}

        {/* Live Status Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 text-xs font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>AI Engine Operational</span>
        </div>

        <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-xs font-mono">
          <span className="text-emerald-400">●</span>
          <span>8/8 Services Healthy</span>
        </div>

        {/* Primary CTA */}
        <button
          onClick={onNewIncident}
          className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-sm shadow-blue-600/30 border border-blue-400/30 active:scale-95"
        >
          <span>+</span>
          <span>New Incident</span>
        </button>
      </div>
    </header>
  );
};
