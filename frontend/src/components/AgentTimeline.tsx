import React from 'react';
import type { AgentEvent } from '../types';

interface AgentTimelineProps {
  events: AgentEvent[];
}

const getAgentColor = (agent: string) => {
  switch (agent) {
    case 'triage':
      return 'bg-purple-100 text-purple-800 border-purple-300';
    case 'investigation':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    case 'diagnosis':
      return 'bg-cyan-100 text-cyan-800 border-cyan-300';
    case 'action_planner':
      return 'bg-orange-100 text-orange-800 border-orange-300';
    case 'verification':
      return 'bg-green-100 text-green-800 border-green-300';
    default:
      return 'bg-slate-100 text-slate-800 border-slate-300';
  }
};

const getAgentLabel = (agent: string) => {
  return agent.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return '✓';
    case 'processing':
      return '⏳';
    case 'failed':
      return '✗';
    default:
      return '●';
  }
};

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ events }) => {
  return (
    <div className="space-y-4">
      {events.map((event, idx) => (
        <div key={event.id} className="flex gap-4">
          {/* Timeline line */}
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${getAgentColor(event.agent)}`}>
              {getStatusIcon(event.status)}
            </div>
            {idx < events.length - 1 && (
              <div className="w-1 h-12 bg-slate-200 mt-2"></div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 pt-1 pb-4">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getAgentColor(event.agent)}`}>
                {getAgentLabel(event.agent)}
              </span>
              <span className="text-xs text-slate-500">
                {event.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <p className="text-sm text-slate-700">{event.message}</p>

            {/* Evidence cards */}
            {event.evidence && event.evidence.length > 0 && (
              <div className="mt-3 space-y-2">
                {event.evidence.map((evidence) => (
                  <div key={evidence.id} className="bg-slate-50 border border-slate-200 rounded p-3 text-xs">
                    <div className="font-semibold text-slate-900">{evidence.title}</div>
                    <div className="text-slate-600 mt-1">{evidence.content}</div>
                    <div className="flex gap-2 mt-2 text-slate-500">
                      <span className="bg-slate-200 px-2 py-1 rounded">{evidence.type.replace(/_/g, ' ')}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">{evidence.relevance}% relevant</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Diagnosis */}
            {event.diagnosis && (
              <div className="mt-3 bg-cyan-50 border border-cyan-200 rounded p-3">
                <div className="text-xs font-semibold text-cyan-900">Diagnosis</div>
                <div className="text-sm text-cyan-800 mt-1">{event.diagnosis.likelyCause}</div>
                <div className="flex items-center gap-2 mt-2">
                  <div className="text-xs font-semibold">Confidence:</div>
                  <div className="w-20 bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${event.diagnosis.confidence}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-bold text-cyan-900">{event.diagnosis.confidence}%</span>
                </div>
                {event.diagnosis.uncertainty && (
                  <div className="text-xs text-cyan-700 mt-2 italic">⚠️ {event.diagnosis.uncertainty}</div>
                )}
              </div>
            )}

            {/* Action */}
            {event.action && (
              <div className="mt-3 bg-orange-50 border border-orange-200 rounded p-3">
                <div className="text-xs font-semibold text-orange-900">Action: {event.action.tool}</div>
                <div className="text-sm text-orange-800 mt-1">{event.action.description}</div>
                <div className="flex gap-2 mt-2">
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${
                    event.action.riskLevel === 'low' ? 'bg-green-100 text-green-800' :
                    event.action.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    event.action.riskLevel === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Risk: {event.action.riskLevel}
                  </span>
                  {event.action.requiresApproval && (
                    <span className="text-xs font-semibold px-2 py-1 rounded bg-red-100 text-red-800">
                      Requires Approval
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-600 mt-2">{event.action.reasoning}</div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
