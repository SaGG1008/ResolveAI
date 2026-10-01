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
    <div className="p-8 space-y-6 max-w-[1400px] mx-auto text-slate-800 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900">
            Knowledge Base & Help Articles
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Verified enterprise troubleshooting runbooks and standard operating procedures.
          </p>
        </div>

        {/* Search */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search articles by keyword or tag..."
          className="w-full sm:w-72 bg-white border border-slate-200 text-xs text-slate-800 rounded-lg px-3.5 py-2 focus:outline-none focus:border-blue-500 placeholder:text-slate-400 shadow-xs"
        />
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-xs font-semibold'
                : 'bg-white border border-slate-200 text-slate-600 hover:text-slate-900'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((art) => (
          <div key={art.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2.5 hover:border-slate-300 transition">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {art.id}
              </span>
              <span className="px-2 py-0.5 rounded text-[11px] bg-slate-100 border border-slate-200 text-slate-600">
                {art.category}
              </span>
            </div>
            <h3 className="text-sm font-bold text-slate-900">{art.title}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">{art.content}</p>
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-100">
              {art.tags.map((t) => (
                <span key={t} className="px-2 py-0.5 rounded text-[10px] bg-slate-50 border border-slate-200 text-slate-500">
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
