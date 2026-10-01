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
  subtitle = "How can we help you today?",
  onNewIncident,
  searchQuery = '',
  onSearchChange,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0 z-10">
      {/* Title / Greeting */}
      <div>
        <h1 className="text-base font-bold text-slate-900 leading-tight">
          {title}
        </h1>
        <p className="text-xs text-slate-500">
          {subtitle}
        </p>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Search */}
        {onSearchChange && (
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search help, tickets, or services..."
              className="w-64 bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-lg pl-8 pr-3 py-1.5 focus:outline-none focus:bg-white focus:border-blue-500 transition placeholder:text-slate-400"
            />
            <span className="absolute left-2.5 top-2 text-slate-400 text-xs">🔍</span>
          </div>
        )}

        {/* Operational Status Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>All Systems Operational</span>
        </div>

        {/* Primary CTA */}
        <button
          onClick={onNewIncident}
          className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition shadow-sm active:scale-95 flex items-center gap-1.5"
        >
          <span>+</span>
          <span>Report an Issue</span>
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center font-bold text-slate-700 text-xs">
            SS
          </div>
        </div>
      </div>
    </header>
  );
};
