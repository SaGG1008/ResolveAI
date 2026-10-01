import React from 'react';

interface ServiceItem {
  id: string;
  name: string;
  status: 'OPERATIONAL' | 'DEGRADED' | 'MAINTENANCE';
  latency: string;
  uptime: string;
  description: string;
}

const SERVICES: ServiceItem[] = [
  {
    id: "vpn_gateway",
    name: "Palo Alto GlobalProtect VPN Gateway (US-East)",
    status: "OPERATIONAL",
    latency: "24ms",
    uptime: "99.98%",
    description: "Enterprise VPN tunnel cluster handling remote workforce connectivity."
  },
  {
    id: "auth_proxy",
    name: "Internal Engineering Auth Proxy (Port 8080)",
    status: "DEGRADED",
    latency: "N/A",
    uptime: "98.42%",
    description: "Local daemon proxying git mirror pulls and internal artifact registry auth."
  },
  {
    id: "okta_sso",
    name: "Okta Enterprise SSO Identity Provider",
    status: "OPERATIONAL",
    latency: "42ms",
    uptime: "99.99%",
    description: "Cloud identity federation and SAML token authentication."
  },
  {
    id: "core_dns",
    name: "Corporate Core DNS Resolver Cluster",
    status: "OPERATIONAL",
    latency: "8ms",
    uptime: "100.0%",
    description: "Internal split-horizon DNS mapping *.internal.corp records."
  },
  {
    id: "jira_itsm",
    name: "Jira Service Desk ITSM API Gateway",
    status: "OPERATIONAL",
    latency: "85ms",
    uptime: "99.95%",
    description: "Ticketing integration layer for Tier-2 human handover."
  },
  {
    id: "ai_orchestrator",
    name: "ResolveAI Multi-Agent Orchestration Engine",
    status: "OPERATIONAL",
    latency: "12ms",
    uptime: "100.0%",
    description: "Asynchronous multi-agent execution pipeline and state machine."
  }
];

export const SystemHealthView: React.FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto text-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span>Infrastructure & Service Health</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 border border-emerald-800 text-emerald-400">
              ● 8/8 Monitored
            </span>
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Real-time telemetry and health diagnostics connected to autonomous investigation agents.
          </p>
        </div>
      </div>

      {/* Global Uptime & Telemetry Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Global Fleet Uptime</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">99.8%</div>
          <div className="text-[11px] text-slate-400 mt-1">Last 30 days operational</div>
        </div>

        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Average Gateway Latency</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">28.4ms</div>
          <div className="text-[11px] text-slate-400 mt-1">Within normal SLA limits</div>
        </div>

        <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Active Probes Dispatched</div>
          <div className="text-2xl font-bold text-blue-400 font-mono mt-1">1,482</div>
          <div className="text-[11px] text-slate-400 mt-1">Zero false verification rate</div>
        </div>
      </div>

      {/* Services Detail List */}
      <div className="bg-[#0e1320] border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-bold text-white">Monitored Service Infrastructure</h2>
        </div>

        <div className="divide-y divide-slate-800/80">
          {SERVICES.map((svc) => (
            <div key={svc.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-900/40 transition">
              <div className="space-y-1 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${
                    svc.status === 'OPERATIONAL' ? 'bg-emerald-400' :
                    svc.status === 'DEGRADED' ? 'bg-amber-400 animate-pulse' : 'bg-rose-400'
                  }`} />
                  <span className="font-bold text-white text-xs">{svc.name}</span>
                </div>
                <p className="text-xs text-slate-400 font-sans">{svc.description}</p>
              </div>

              <div className="flex items-center gap-6 text-xs font-mono shrink-0">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Latency</div>
                  <div className="text-slate-300 font-bold">{svc.latency}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Uptime</div>
                  <div className="text-slate-300 font-bold">{svc.uptime}</div>
                </div>
                <div>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                    svc.status === 'OPERATIONAL'
                      ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                      : 'bg-amber-950 text-amber-300 border-amber-800'
                  }`}>
                    {svc.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
