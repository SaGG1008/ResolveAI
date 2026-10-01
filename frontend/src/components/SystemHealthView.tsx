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
    name: "Enterprise VPN Gateway (GlobalProtect US-East)",
    status: "OPERATIONAL",
    latency: "24ms",
    uptime: "99.98%",
    description: "Corporate VPN tunnel cluster handling secure remote workforce connectivity."
  },
  {
    id: "auth_proxy",
    name: "Engineering Local Auth Proxy (Port 8080)",
    status: "DEGRADED",
    latency: "Timeout",
    uptime: "98.42%",
    description: "Internal proxy service for developer repository access and artifact registries."
  },
  {
    id: "okta_sso",
    name: "Okta Enterprise Single Sign-On (SSO)",
    status: "OPERATIONAL",
    latency: "42ms",
    uptime: "99.99%",
    description: "Identity federation, SAML token authentication, and employee login access."
  },
  {
    id: "core_dns",
    name: "Corporate Internal DNS Resolvers",
    status: "OPERATIONAL",
    latency: "8ms",
    uptime: "100.0%",
    description: "Internal split-horizon DNS mapping *.internal.corp services and endpoints."
  },
  {
    id: "jira_itsm",
    name: "ITSM Integration & Ticketing Sync",
    status: "OPERATIONAL",
    latency: "85ms",
    uptime: "99.95%",
    description: "Enterprise ticketing sync gateway for Tier-2 helpdesk escalations."
  },
  {
    id: "ai_orchestrator",
    name: "ResolveAI Autonomous Support Engine",
    status: "OPERATIONAL",
    latency: "12ms",
    uptime: "100.0%",
    description: "Background diagnostic workflow engine and automated remediation service."
  }
];

export const SystemHealthView: React.FC = () => {
  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-[1300px] mx-auto text-slate-900">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-slate-900">Service Status & System Health</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 border border-emerald-200 text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              All Core Systems Operational
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Real-time operational status for corporate networks, identity services, and internal applications.
          </p>
        </div>
      </div>

      {/* Global Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overall Service Uptime</div>
          <div className="text-2xl font-bold text-emerald-600 mt-1">99.8%</div>
          <div className="text-xs text-slate-500 mt-1">Last 30 days rolling average</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Response Time</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">28ms</div>
          <div className="text-xs text-slate-500 mt-1">Well within SLA benchmark (50ms)</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Automated Checks</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">1,482</div>
          <div className="text-xs text-slate-500 mt-1">Continuous health verification probes</div>
        </div>
      </div>

      {/* Monitored Services List */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900">Monitored Corporate Services</h2>
          <span className="text-xs text-slate-500">Updated automatically every 30 seconds</span>
        </div>

        <div className="divide-y divide-slate-100">
          {SERVICES.map((svc) => (
            <div key={svc.id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/60 transition">
              <div className="space-y-1 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${
                    svc.status === 'OPERATIONAL' ? 'bg-emerald-500' :
                    svc.status === 'DEGRADED' ? 'bg-amber-500 animate-pulse' : 'bg-rose-500'
                  }`} />
                  <span className="font-semibold text-slate-900 text-sm">{svc.name}</span>
                </div>
                <p className="text-xs text-slate-500">{svc.description}</p>
              </div>

              <div className="flex items-center gap-6 text-xs shrink-0">
                <div className="text-right">
                  <div className="text-[11px] text-slate-400">Response</div>
                  <div className="text-slate-700 font-medium font-mono">{svc.latency}</div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] text-slate-400">Uptime</div>
                  <div className="text-slate-700 font-medium font-mono">{svc.uptime}</div>
                </div>
                <div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${
                    svc.status === 'OPERATIONAL'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {svc.status === 'OPERATIONAL' ? 'Operational' : 'Degraded'}
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
