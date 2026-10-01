import React from 'react';
import type { AgentEvent } from '../types';

interface AgentTimelineProps {
  events: AgentEvent[];
}

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ events }) => {
  const getAgentTheme = (agent: string) => {
    switch (agent) {
      case 'triage':
        return {
          badge: 'bg-purple-950/70 border-purple-800/80 text-purple-300',
          dot: 'bg-purple-500 border-purple-300',
          label: 'Triage Agent',
        };
      case 'investigation':
        return {
          badge: 'bg-blue-950/70 border-blue-800/80 text-blue-300',
          dot: 'bg-blue-500 border-blue-300',
          label: 'Investigation Agent',
        };
      case 'diagnosis':
        return {
          badge: 'bg-cyan-950/70 border-cyan-800/80 text-cyan-300',
          dot: 'bg-cyan-500 border-cyan-300',
          label: 'Diagnosis Agent',
        };
      case 'action_planner':
        return {
          badge: 'bg-amber-950/70 border-amber-800/80 text-amber-300',
          dot: 'bg-amber-500 border-amber-300',
          label: 'Action Planner',
        };
      case 'verification':
        return {
          badge: 'bg-emerald-950/70 border-emerald-800/80 text-emerald-300',
          dot: 'bg-emerald-500 border-emerald-300',
          label: 'Verification Agent',
        };
      default:
        return {
          badge: 'bg-slate-800 border-slate-700 text-slate-300',
          dot: 'bg-slate-500 border-slate-400',
          label: 'Agent Runtime',
        };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'processing':
        return '▶';
      case 'failed':
        return '✕';
      default:
        return '●';
    }
  };

  return (
    <div className="space-y-4">
      {events.map((event, idx) => {
        const theme = getAgentTheme(event.agent);
        const isLatest = idx === events.length - 1;

        return (
          <div key={event.id || idx} className="relative flex gap-4 text-xs font-sans">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs border shadow-sm ${
                  event.status === 'completed'
                    ? 'bg-emerald-950/80 border-emerald-500/80 text-emerald-400'
                    : event.status === 'processing'
                    ? 'bg-blue-950/90 border-blue-400 text-blue-300 animate-pulse'
                    : event.status === 'failed'
                    ? 'bg-rose-950/80 border-rose-500/80 text-rose-400'
                    : 'bg-slate-900 border-slate-700 text-slate-400'
                }`}
              >
                {getStatusIcon(event.status)}
              </div>
              {idx < events.length - 1 && (
                <div className="w-[1px] h-full bg-slate-800 my-1 min-h-[30px]" />
              )}
            </div>

            {/* Event Body Card */}
            <div className={`flex-1 pb-4 ${isLatest ? 'opacity-100' : 'opacity-95'}`}>
              <div className="bg-[#0e1320] border border-slate-800/90 rounded-xl p-4 shadow-sm space-y-2.5">
                {/* Agent Header Tag */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold border ${theme.badge}`}>
                      {theme.label}
                    </span>
                    <span className="text-[10px] font-mono uppercase text-slate-500">
                      {event.status}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>

                {/* Main Message */}
                <p className="text-slate-200 text-xs leading-relaxed font-sans font-medium">
                  {event.message}
                </p>

                {/* Sub-Card: Grounded Evidence Items */}
                {event.evidence && event.evidence.length > 0 && (
                  <div className="mt-2.5 pt-2.5 border-t border-slate-800/80 space-y-2">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                      Discovered Evidence Sources ({event.evidence.length})
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {event.evidence.map((ev) => (
                        <div key={ev.id} className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/70 text-[11px]">
                          <div className="flex items-center justify-between font-bold text-slate-200 mb-1">
                            <span className="truncate">{ev.title}</span>
                            <span className="text-[10px] font-mono text-blue-400 shrink-0 ml-2">
                              {ev.relevance}% relevant
                            </span>
                          </div>
                          <p className="text-slate-400 text-[11px] line-clamp-2 leading-relaxed">
                            {ev.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sub-Card: Diagnosis Block */}
                {event.diagnosis && (
                  <div className="mt-2.5 p-3 rounded-lg bg-cyan-950/30 border border-cyan-900/40 text-[11px] space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-mono uppercase text-cyan-400 font-bold">
                      <span>Synthesized Root Cause</span>
                      <span>Confidence: {event.diagnosis.confidence}%</span>
                    </div>
                    <div className="font-semibold text-cyan-200">
                      {event.diagnosis.likelyCause}
                    </div>
                    {event.diagnosis.uncertainty && (
                      <div className="text-[10px] text-amber-300 italic pt-1">
                        ⚠️ Note: {event.diagnosis.uncertainty}
                      </div>
                    )}
                  </div>
                )}

                {/* Sub-Card: Action Plan Block */}
                {event.action && (
                  <div className="mt-2.5 p-3 rounded-lg bg-amber-950/20 border border-amber-900/40 text-[11px] space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-mono uppercase font-bold text-amber-400">
                      <span>Proposed Action: {event.action.tool}</span>
                      <span className="px-1.5 py-0.5 rounded bg-amber-900/40 border border-amber-700/50">
                        Risk: {event.action.riskLevel.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-slate-200">
                      {event.action.description}
                    </div>
                    <div className="text-[10px] text-slate-400 pt-1 font-mono">
                      Reasoning: {event.action.reasoning}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
