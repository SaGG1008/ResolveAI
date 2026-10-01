import React, { useState, useEffect } from 'react';
import type { Incident } from '../types';
import { AgentTimeline } from './AgentTimeline';
import { AgentPipelineBar } from './AgentPipelineBar';
import { api } from '../services/api';

interface IncidentWorkspaceProps {
  incident: Incident;
  onBack: () => void;
}

export const IncidentWorkspace: React.FC<IncidentWorkspaceProps> = ({ incident: initialIncident, onBack }) => {
  const [incident, setIncident] = useState<Incident>(initialIncident);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Subscribe to live Server-Sent Events (SSE) updates
    const unsubscribe = api.subscribeToIncident(initialIncident.id, (updated) => {
      setIncident(updated);
    });
    return () => {
      unsubscribe();
    };
  }, [initialIncident.id]);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      const updated = await api.submitApproval(incident.id, true);
      setIncident(updated);
      setApprovalModalOpen(false);
    } catch (e) {
      console.error('Approval failed:', e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEscalate = async () => {
    setIsSubmitting(true);
    try {
      const updated = await api.submitApproval(incident.id, false, "Operator requested Tier-2 human escalation");
      setIncident(updated);
      setApprovalModalOpen(false);
    } catch (e) {
      console.error('Escalation failed:', e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'bg-emerald-950/80 text-emerald-300 border-emerald-600/80';
      case 'escalated':
        return 'bg-rose-950/80 text-rose-300 border-rose-600/80';
      case 'pending_approval':
        return 'bg-amber-950/80 text-amber-300 border-amber-600/80 animate-pulse';
      case 'executing':
      case 'verifying':
        return 'bg-indigo-950/80 text-indigo-300 border-indigo-600/80';
      case 'investigating':
      case 'diagnosed':
        return 'bg-blue-950/80 text-blue-300 border-blue-600/80';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-rose-950/80 text-rose-300 border-rose-800 font-bold';
      case 'high':
        return 'bg-amber-950/80 text-amber-300 border-amber-800 font-semibold';
      case 'medium':
        return 'bg-blue-950/80 text-blue-300 border-blue-800';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0b0f19] text-slate-200">
      {/* 1. TOP HEADER BAR */}
      <div className="bg-[#0e1320] border-b border-slate-800/80 px-6 py-4 shrink-0">
        <div className="flex items-center justify-between mb-3">
          <button
            onClick={onBack}
            className="text-xs text-blue-400 hover:text-blue-300 font-mono font-medium flex items-center gap-1.5 transition"
          >
            <span>←</span>
            <span>Back to Command Center</span>
          </button>
          <div className="text-[11px] font-mono text-slate-400">
            Created: {new Date(incident.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </div>
        </div>

        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xl font-bold text-white font-mono">{incident.id}</span>
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono uppercase border ${getPriorityBadge(incident.priority)}`}>
                {incident.priority} Priority
              </span>
              <span className="px-2.5 py-0.5 rounded text-[10px] font-mono bg-slate-900 border border-slate-700 text-slate-300">
                {incident.category}
              </span>
            </div>
            <h1 className="text-base font-semibold text-slate-100 mt-1">{incident.title}</h1>
            <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{incident.description}</p>
          </div>

          <div className="text-right shrink-0">
            <span className={`inline-block px-3.5 py-1 rounded-full font-mono font-bold text-xs border ${getStatusBadge(incident.status)}`}>
              {incident.status.replace(/_/g, ' ').toUpperCase()}
            </span>
          </div>
        </div>

        {/* Multi-Agent Pipeline Strip */}
        <div className="mt-4">
          <AgentPipelineBar currentStatus={incident.status} />
        </div>
      </div>

      {/* 2. MAIN INVESTIGATION WORKSPACE */}
      <div className="flex-1 overflow-auto flex">
        {/* LEFT COLUMN: Live Agent Activity Timeline (60%) */}
        <div className="flex-1 overflow-y-auto border-r border-slate-800/80 p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <span className="text-indigo-400 text-xs">✦</span>
              <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                Autonomous Agent Execution Trace
              </h2>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              {incident.events.length} audit steps recorded
            </span>
          </div>

          <AgentTimeline events={incident.events} />
        </div>

        {/* RIGHT COLUMN: Evidence, Diagnosis & Decision Panel (40%) */}
        <div className="w-96 bg-[#090d16] p-6 overflow-y-auto space-y-5 shrink-0 border-l border-slate-800/80 text-xs">
          {/* AI Diagnosis Card */}
          {incident.diagnosis && (
            <div className="bg-[#0e1320] border border-cyan-900/50 rounded-xl p-4 shadow-sm space-y-2.5">
              <div className="flex items-center justify-between text-cyan-400 text-[10px] font-mono uppercase font-bold">
                <span>AI Root Cause Diagnosis</span>
                <span className="px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-700/60">
                  {incident.diagnosis.confidence}% Confidence
                </span>
              </div>
              <div className="font-bold text-cyan-200 text-xs leading-relaxed">
                {incident.diagnosis.likelyCause}
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-cyan-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${incident.diagnosis.confidence}%` }}
                />
              </div>
              {incident.diagnosis.uncertainty && (
                <div className="text-[10px] text-amber-300 italic pt-1">
                  ⚠️ Note: {incident.diagnosis.uncertainty}
                </div>
              )}
            </div>
          )}

          {/* Action Decision Card */}
          {incident.proposedAction && (
            <div className="bg-[#0e1320] border border-amber-900/50 rounded-xl p-4 shadow-sm space-y-2.5">
              <div className="flex items-center justify-between text-[10px] font-mono uppercase font-bold text-amber-400">
                <span>Recommended Action</span>
                <span className="px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-700/60">
                  Risk: {incident.proposedAction.riskLevel.toUpperCase()}
                </span>
              </div>
              <div className="font-bold text-white text-xs font-mono">
                {incident.proposedAction.tool}
              </div>
              <p className="text-slate-300 text-[11px] leading-relaxed">
                {incident.proposedAction.description}
              </p>
              <div className="bg-slate-950/70 border border-slate-800 p-2.5 rounded-lg text-[11px] text-slate-400 space-y-1">
                <div className="text-[10px] font-mono uppercase text-slate-300 font-bold">Why this action?</div>
                <div>{incident.proposedAction.reasoning}</div>
              </div>

              {/* Action Buttons for Pending Approval */}
              {incident.status === 'pending_approval' && (
                <div className="pt-2 space-y-2">
                  <button
                    onClick={() => setApprovalModalOpen(true)}
                    className="w-full py-2 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg text-xs shadow-md shadow-green-600/30 transition active:scale-95"
                  >
                    Review & Authorize Execution
                  </button>
                  <button
                    onClick={handleEscalate}
                    disabled={isSubmitting}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg text-xs transition"
                  >
                    Escalate to Tier-2
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Grounded Evidence Drawer */}
          <div className="bg-[#0e1320] border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-300 font-bold">
                Grounded Evidence Sources ({incident.evidence?.length || 0})
              </div>
              <span className="text-[10px] font-mono text-emerald-400">Zero-Hallucination</span>
            </div>

            {incident.evidence && incident.evidence.length > 0 ? (
              <div className="space-y-2">
                {incident.evidence.map((ev) => (
                  <div key={ev.id} className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-[11px] space-y-1">
                    <div className="flex items-center justify-between font-bold text-slate-200">
                      <span className="truncate">{ev.title}</span>
                      <span className="text-[10px] font-mono text-blue-400 shrink-0 ml-1">
                        {ev.relevance}%
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px] line-clamp-2 leading-relaxed">
                      {ev.content}
                    </p>
                    <div className="text-[9px] font-mono text-slate-500 pt-0.5">
                      Source: {ev.source || ev.type}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-500 text-[11px] italic py-2">
                Investigation in progress; searching telemetry and runbooks...
              </div>
            )}
          </div>

          {/* Resolution Outcome Block */}
          {incident.resolution && (
            <div className="bg-emerald-950/30 border border-emerald-800/60 rounded-xl p-4 shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-mono font-bold text-[10px] uppercase">
                <span>✓ Verified Resolution</span>
              </div>
              <div className="text-slate-200 font-semibold text-xs">
                {incident.resolution.success ? "Incident Successfully Resolved & Verified" : "Verification Failed"}
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
                Method: {incident.resolution.verificationMethod}
              </div>
            </div>
          )}

          {/* Escalation Outcome Block */}
          {incident.escalationReason && (
            <div className="bg-rose-950/30 border border-rose-800/60 rounded-xl p-4 shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-rose-400 font-mono font-bold text-[10px] uppercase">
                <span>⚠ Human Escalation Handover</span>
              </div>
              <div className="text-slate-300 text-[11px] leading-relaxed">
                {incident.escalationReason}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 3. HUMAN APPROVAL MODAL */}
      {approvalModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#0e1320] border border-slate-700 rounded-2xl shadow-2xl max-w-lg w-full p-6 text-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
                <h3 className="text-base font-bold text-white">Operator Authorization Required</h3>
              </div>
              <button
                onClick={() => setApprovalModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 font-bold"
              >
                ✕
              </button>
            </div>

            <div className="text-xs text-slate-300 space-y-3 leading-relaxed">
              <p>
                The AI Action Planner has selected an elevated-risk tool. In accordance with autonomous safety policies, execution requires human sign-off:
              </p>

              {incident.proposedAction && (
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono font-bold">
                    <span className="text-amber-400">{incident.proposedAction.tool}</span>
                    <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                      Risk: {incident.proposedAction.riskLevel.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-slate-300 text-xs">
                    {incident.proposedAction.description}
                  </div>
                  <div className="text-[11px] text-slate-400 pt-1 font-mono border-t border-slate-800/80">
                    Justification: {incident.proposedAction.reasoning}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-800 flex gap-3">
              <button
                onClick={() => setApprovalModalOpen(false)}
                disabled={isSubmitting}
                className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={isSubmitting}
                className="flex-1 py-2.5 bg-green-600 hover:bg-green-500 text-white rounded-lg text-xs font-bold shadow-md shadow-green-600/30 transition"
              >
                {isSubmitting ? 'Executing Remediation...' : 'Authorize & Execute'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
