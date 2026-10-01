import React, { useState, useEffect } from 'react';
import type { Incident } from '../types';
import { api } from '../services/api';

interface IncidentWorkspaceProps {
  incident: Incident;
  onBack: () => void;
}

export const IncidentWorkspace: React.FC<IncidentWorkspaceProps> = ({ incident: initialIncident, onBack }) => {
  const [incident, setIncident] = useState<Incident>(initialIncident);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showTechnicalAudit, setShowTechnicalAudit] = useState(false);

  useEffect(() => {
    // Subscribe to real-time updates via SSE
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
        return { label: '✓ Resolved', style: 'bg-emerald-50 text-emerald-700 border-emerald-300 font-semibold' };
      case 'escalated':
        return { label: '⚠ Needs IT Support', style: 'bg-red-50 text-red-700 border-red-300 font-semibold' };
      case 'pending_approval':
        return { label: 'Waiting for Approval', style: 'bg-amber-50 text-amber-800 border-amber-300 font-semibold' };
      case 'executing':
        return { label: 'Applying Fix', style: 'bg-blue-50 text-blue-700 border-blue-300 font-semibold' };
      case 'verifying':
        return { label: 'Verifying Fix', style: 'bg-indigo-50 text-indigo-700 border-indigo-300 font-semibold' };
      case 'investigating':
      case 'diagnosed':
        return { label: 'AI Investigating', style: 'bg-blue-50 text-blue-700 border-blue-300 font-semibold' };
      default:
        return { label: 'Open', style: 'bg-slate-100 text-slate-700 border-slate-300 font-semibold' };
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'high':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'medium':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const statusBadge = getStatusBadge(incident.status);

  return (
    <div className="flex flex-col h-screen bg-[#f8fafc] text-slate-800 font-sans">
      {/* 1. TOP INCIDENT HEADER */}
      <div className="bg-white border-b border-slate-200 px-8 py-5 shrink-0">
        <div className="flex items-center justify-between mb-3">
          <button
            onClick={onBack}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1.5 transition"
          >
            <span>←</span>
            <span>Back to Incident Queue</span>
          </button>
          <div className="text-xs text-slate-400">
            Created: {new Date(incident.createdAt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-sm font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                {incident.id}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityBadge(incident.priority)}`}>
                {incident.priority.toUpperCase()} Priority
              </span>
              <span className="px-2 py-0.5 rounded text-xs bg-slate-100 text-slate-600 border border-slate-200">
                {incident.category}
              </span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 mt-1.5">{incident.title}</h1>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <span className={`px-3 py-1 rounded-full text-xs border ${statusBadge.style}`}>
              {statusBadge.label}
            </span>
          </div>
        </div>

        {/* Humanized AI Assistance Progress Tracker */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 overflow-x-auto gap-3">
          <div className="flex items-center gap-2 font-medium shrink-0">
            <span className="text-blue-600 font-bold">AI Assistance:</span>
            <span>
              {incident.status === 'resolved' ? '✓ Investigation complete and fix verified.' :
               incident.status === 'escalated' ? '⚠ Escalated to Tier-2 support team.' :
               incident.status === 'pending_approval' ? '⏳ Proposed remediation waiting for authorization.' :
               'ResolveAI is currently analyzing the issue and checking systems...'}
            </span>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-slate-500 shrink-0">
            <span className={incident.status !== 'open' ? 'text-emerald-600 font-semibold' : 'text-slate-400'}>
              ✓ Classified
            </span>
            <span>→</span>
            <span className={incident.evidence?.length ? 'text-emerald-600 font-semibold' : 'text-slate-400'}>
              ✓ Checked Systems
            </span>
            <span>→</span>
            <span className={incident.diagnosis ? 'text-emerald-600 font-semibold' : 'text-slate-400'}>
              ✓ Root Cause Found
            </span>
            <span>→</span>
            <span className={incident.status === 'resolved' ? 'text-emerald-600 font-semibold' : 'text-blue-600 font-semibold'}>
              {incident.status === 'resolved' ? '✓ Verified' : '○ Verifying'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. MAIN WORKSPACE */}
      <div className="flex-1 overflow-auto flex">
        {/* LEFT COLUMN: Problem Details, Diagnosis, Action & Why (60%) */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* Issue Statement */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2">
            <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Reported Problem
            </div>
            <p className="text-sm text-slate-800 leading-relaxed">
              {incident.description}
            </p>
          </div>

          {/* What We Found (AI Diagnosis) */}
          {incident.diagnosis && (
            <div className="bg-white border border-blue-200 rounded-xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-blue-900 uppercase tracking-wider flex items-center gap-2">
                  <span>💡</span>
                  <span>What We Found (Root Cause)</span>
                </div>
                <div className="text-xs font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                  Confidence: {incident.diagnosis.confidence}%
                </div>
              </div>

              <p className="text-sm font-semibold text-slate-900 leading-relaxed">
                {incident.diagnosis.likelyCause}
              </p>

              {incident.diagnosis.uncertainty && (
                <div className="text-xs text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                  ⚠️ Note: {incident.diagnosis.uncertainty}
                </div>
              )}
            </div>
          )}

          {/* Why This Recommendation? (Explainability) */}
          {incident.proposedAction && (
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
              <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Why this recommendation?
              </div>

              <div className="space-y-2 text-xs text-slate-700 leading-relaxed">
                <div className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>{incident.proposedAction.reasoning}</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Targeted remediation: <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono text-[11px]">{incident.proposedAction.tool}</code></span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Risk classification: <span className="font-semibold text-slate-900">{incident.proposedAction.riskLevel.toUpperCase()} RISK</span></span>
                </div>
              </div>
            </div>
          )}

          {/* Recommended Action Card */}
          {incident.proposedAction && (
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Recommended Action
                </div>
                <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                  incident.proposedAction.riskLevel === 'low' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                  incident.proposedAction.riskLevel === 'medium' ? 'bg-amber-50 text-amber-800 border border-amber-300' :
                  'bg-red-50 text-red-700 border border-red-200'
                }`}>
                  {incident.proposedAction.riskLevel.toUpperCase()} RISK
                </span>
              </div>

              <div className="text-sm text-slate-800">
                {incident.proposedAction.description}
              </div>

              {/* Action Buttons */}
              {incident.status === 'pending_approval' && (
                <div className="pt-2 flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => setApprovalModalOpen(true)}
                    className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg text-xs shadow-sm transition active:scale-95"
                  >
                    Authorize & Apply Fix
                  </button>
                  <button
                    onClick={handleEscalate}
                    disabled={isSubmitting}
                    className="py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs transition"
                  >
                    Escalate to IT Support
                  </button>
                </div>
              )}

              {incident.status === 'resolved' && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 font-medium flex items-center gap-2">
                  <span>✓</span>
                  <span>Action executed and verified successfully by ResolveAI.</span>
                </div>
              )}
            </div>
          )}

          {/* Collapsible Technical AI Audit Trail (For Admins & Judges) */}
          <div className="border border-slate-200 rounded-xl bg-white overflow-hidden shadow-sm">
            <button
              onClick={() => setShowTechnicalAudit(!showTechnicalAudit)}
              className="w-full p-4 text-left flex items-center justify-between text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              <div className="flex items-center gap-2">
                <span>🤖</span>
                <span>AI Technical Investigation Details & Agent Trace</span>
              </div>
              <span className="text-slate-400 font-mono text-xs">
                {showTechnicalAudit ? '▲ Collapse' : '▼ Expand'}
              </span>
            </button>

            {showTechnicalAudit && (
              <div className="p-4 border-t border-slate-200 bg-slate-50/50 space-y-3">
                {incident.events.map((evt, idx) => (
                  <div key={evt.id || idx} className="p-3 bg-white border border-slate-200 rounded-lg text-xs space-y-1">
                    <div className="flex items-center justify-between font-semibold text-slate-800">
                      <span className="capitalize">{evt.agent.replace(/_/g, ' ')} Agent</span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {new Date(evt.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">{evt.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Grounded Evidence & Activity Timeline (40%) */}
        <div className="w-96 bg-white border-l border-slate-200 p-6 overflow-y-auto space-y-6 shrink-0 text-xs">
          {/* Grounded Evidence Sources */}
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Evidence Found ({incident.evidence?.length || 0})
              </h3>
              <span className="text-[11px] text-slate-400">Verified Signals</span>
            </div>

            {incident.evidence && incident.evidence.length > 0 ? (
              <div className="space-y-2.5">
                {incident.evidence.map((ev) => (
                  <div key={ev.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50/70 space-y-1">
                    <div className="flex items-center justify-between font-semibold text-slate-900">
                      <span className="truncate">{ev.title}</span>
                      <span className="text-[10px] font-mono font-bold text-blue-600 shrink-0 ml-1">
                        {ev.relevance}% match
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs leading-relaxed">
                      {ev.content}
                    </p>
                    <div className="text-[10px] text-slate-400 pt-0.5">
                      Source: {ev.source || ev.type}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 italic text-xs py-2">
                Searching knowledge base and system telemetry...
              </p>
            )}
          </div>

          {/* Activity Timeline */}
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Activity Log
              </h3>
            </div>

            <div className="space-y-2.5">
              {incident.events.map((evt, idx) => (
                <div key={evt.id || idx} className="flex gap-2.5 items-start text-xs">
                  <span className="text-xs mt-0.5">
                    {evt.status === 'completed' ? '✓' : evt.status === 'failed' ? '✕' : '●'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-slate-800 leading-snug">{evt.message}</div>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                      {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Resolution Confirmation */}
          {incident.resolution && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
              <div className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                <span>✓</span>
                <span>Verification & Closure</span>
              </div>
              <p className="text-xs text-emerald-800">
                Method: {incident.resolution.verificationMethod}
              </p>
              <div className="text-[11px] text-emerald-700">
                Resolved at {new Date(incident.resolution.timestamp).toLocaleTimeString()}
              </div>
            </div>
          )}

          {/* Escalation Handover */}
          {incident.escalationReason && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2">
              <div className="text-xs font-bold text-red-900 flex items-center gap-1.5">
                <span>⚠</span>
                <span>Tier-2 Handover</span>
              </div>
              <p className="text-xs text-red-800">
                {incident.escalationReason}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 3. HUMAN AUTHORIZATION MODAL */}
      {approvalModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl shadow-2xl max-w-md w-full p-6 text-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Authorize Remediation Action</h3>
              <button
                onClick={() => setApprovalModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              ResolveAI has proposed an action that requires operator confirmation before execution:
            </p>

            {incident.proposedAction && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-2 text-xs">
                <div className="flex items-center justify-between font-bold">
                  <span className="text-slate-900 font-mono">{incident.proposedAction.tool}</span>
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200 text-[10px]">
                    {incident.proposedAction.riskLevel.toUpperCase()} RISK
                  </span>
                </div>
                <div className="text-slate-700">{incident.proposedAction.description}</div>
                <div className="text-slate-500 pt-1 border-t border-slate-200 text-[11px]">
                  Reason: {incident.proposedAction.reasoning}
                </div>
              </div>
            )}

            <div className="pt-2 flex gap-3">
              <button
                onClick={() => setApprovalModalOpen(false)}
                disabled={isSubmitting}
                className="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={isSubmitting}
                className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition shadow-sm"
              >
                {isSubmitting ? 'Executing...' : 'Authorize & Execute'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
