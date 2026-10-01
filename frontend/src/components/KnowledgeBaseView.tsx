import React, { useState } from 'react';

interface Article {
  id: string;
  title: string;
  category: string;
  content: string;
  tags: string[];
}

const KB_ARTICLES: Article[] = [
  {
    id: "KB-104",
    title: "Resolving GlobalProtect VPN Stale Session Locks",
    category: "Network / VPN",
    content: "When a client drops abruptly, the gateway may retain a ghost session. Error message: 'Authentication Session Expired' or repeated disconnects every 5 minutes. Resolution: Run reset_vpn_session to clear the dead token, then reconnect client.",
    tags: ["vpn", "globalprotect", "disconnect", "session", "expired", "network"]
  },
  {
    id: "KB-208",
    title: "Flushing Corrupted DNS Resolver Cache",
    category: "Network",
    content: "Local DNS cache corruption causes intermittent resolution failures for internal company domains (*.internal.corp). Resolution: Execute flush_dns_cache to purge resolver table.",
    tags: ["dns", "lookup", "resolution", "internal", "domain", "network"]
  },
  {
    id: "KB-318",
    title: "Internal Engineering Auth Proxy Service Recovery",
    category: "Services",
    content: "If internal git mirrors or artifact registries reject connection on port 8080, verify if local auth_proxy daemon crashed with exit code 137 (OOM). Procedure requires restarting auth_proxy service. This is a medium-risk operational change.",
    tags: ["proxy", "auth_proxy", "git", "port 8080", "connection refused", "service"]
  },
  {
    id: "KB-412",
    title: "Handling Hardware Memory Parity & Kernel Panics",
    category: "Hardware",
    content: "Kernel stop code 0x889FA or flickering color bands indicate physical VRAM or ECC memory hardware degradation. Automated remediation is NOT possible. Immediately escalate to Tier-2 Hardware Provisioning for machine swap.",
    tags: ["kernel", "panic", "screen", "flickering", "purple", "memory", "hardware", "0x889fa"]
  },
  {
    id: "KB-501",
    title: "SaaS SSO Token Refresh & Okta Session Renewal",
    category: "Authentication",
    content: "When single sign-on apps continuously loop on the login screen, invalidate user auth token cache and re-prompt authentication.",
    tags: ["sso", "okta", "token", "login", "loop", "authentication"]
  }
];

export const KnowledgeBaseView: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = ['ALL', 'Network / VPN', 'Network', 'Services', 'Hardware', 'Authentication'];

  const filtered = KB_ARTICLES.filter(art => {
    const matchesCat = selectedCategory === 'ALL' || art.category === selectedCategory;
    const matchesSearch = !search || 
      art.title.toLowerCase().includes(search.toLowerCase()) ||
      art.content.toLowerCase().includes(search.toLowerCase()) ||
      art.tags.some(t => t.toLowerCase().includes(search.toLowerCase()));
    return matchesCat && matchesSearch;
  });

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto text-slate-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span>Knowledge Base & Autonomous Runbooks</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-950/80 border border-blue-800 text-blue-400">
              RAG Corpus
            </span>
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Standard operating procedures indexed for real-time investigation and automated resolution.
          </p>
        </div>

        {/* Search */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search runbooks by keyword, tag, or ID..."
          className="w-full sm:w-72 bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 placeholder:text-slate-500"
        />
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg font-mono text-[11px] transition ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white font-bold'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((art) => (
          <div key={art.id} className="bg-[#0e1320] border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-blue-400">{art.id}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 border border-slate-700 text-slate-300">
                {art.category}
              </span>
            </div>
            <h3 className="text-sm font-bold text-white">{art.title}</h3>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">{art.content}</p>
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/80">
              {art.tags.map((t) => (
                <span key={t} className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-950 border border-slate-800 text-slate-400">
                  #{t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
