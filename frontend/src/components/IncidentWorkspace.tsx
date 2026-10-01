import React, { useState, useEffect } from 'react';
import type { Incident } from '../types';
import { AgentTimeline } from './AgentTimeline';
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
      const updated = await api.submitApproval(incident.id, false, "Operator chose manual escalation");
      setIncident(updated);
      setApprovalModalOpen(false);
    } catch (e) {
      console.error('Escalation failed:', e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'escalated':
        return 'bg-red-100 text-red-800';
      case 'pending_approval':
        return 'bg-amber-100 text-amber-800';
      case 'executing':
      case 'verifying':
      case 'investigating':
      case 'diagnosed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-8 py-6">
        <button
          onClick={onBack}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium mb-4"
        >
          ← Back to Dashboard
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{incident.id}</h1>
            <h2 className="text-xl text-slate-700 mt-2">{incident.title}</h2>
            <p className="text-slate-600 mt-1">{incident.description}</p>
          </div>
          <div className="text-right">
            <span className={`inline-block px-4 py-2 rounded-lg font-semibold text-sm ${getStatusColor(incident.status)}`}>
              {incident.status.replace(/_/g, ' ').toUpperCase()}
            </span>
            <div className="text-sm text-slate-500 mt-3">
              Created: {new Date(incident.createdAt).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Main content - Two column layout */}
      <div className="flex-1 overflow-auto flex">
        {/* Left: Agent Activity Timeline */}
        <div className="flex-1 border-r border-slate-200 px-8 py-6">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Agent Activity</h3>
          <AgentTimeline events={incident.events} />
        </div>

        {/* Right: Incident Overview Panel */}
        <div className="w-80 bg-white border-l border-slate-200 px-6 py-6 overflow-auto">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Overview</h3>

          {/* Status details */}
          <div className="mb-6">
            <h4 className="text-xs font-semibold text-slate-600 uppercase mb-2">Status Details</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Priority:</span>
                <span className="font-semibold text-slate-900">{incident.priority.charAt(0).toUpperCase() + incident.priority.slice(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Category:</span>
                <span className="font-semibold text-slate-900">{incident.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Current Status:</span>
                <span className="font-semibold text-slate-900">{incident.status.replace(/_/g, ' ')}</span>
              </div>
            </div>
          </div>

          {/* Diagnosis if available */}
          {incident.diagnosis && (
            <div className="mb-6 bg-cyan-50 border border-cyan-200 rounded p-4">
              <h4 className="text-xs font-semibold text-cyan-900 uppercase mb-2">Diagnosis</h4>
              <p className="text-sm text-cyan-900 font-semibold mb-2">{incident.diagnosis.likelyCause}</p>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs text-cyan-700">Confidence:</span>
                <div className="flex-1 bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${incident.diagnosis.confidence}%` }}
                  ></div>
                </div>
                <span className="text-xs font-bold text-cyan-900">{incident.diagnosis.confidence}%</span>
              </div>
              {incident.diagnosis.uncertainty && (
                <p className="text-xs text-cyan-700 italic">⚠️ {incident.diagnosis.uncertainty}</p>
              )}
            </div>
          )}

          {/* Evidence */}
          {incident.evidence && incident.evidence.length > 0 && (
            <div className="mb-6">
              <h4 className="text-xs font-semibold text-slate-600 uppercase mb-3">Evidence</h4>
              <div className="space-y-2">
                {incident.evidence.map((ev) => (
                  <div key={ev.id} className="bg-slate-50 border border-slate-200 rounded p-2 text-xs">
                    <div className="font-semibold text-slate-900">{ev.title}</div>
                    <div className="text-slate-600 text-xs mt-1">{ev.source}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Resolution */}
          {incident.resolution && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded p-4">
              <h4 className="text-xs font-semibold text-green-900 uppercase mb-2">Resolution</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Status:</span>
                  <span className="font-semibold text-green-900">{incident.resolution.success ? 'Success' : 'Failed'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Method:</span>
                  <span className="font-semibold text-green-900">{incident.resolution.verificationMethod}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Resolved:</span>
                  <span className="font-semibold text-green-900">{new Date(incident.resolution.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Escalation */}
          {incident.escalationReason && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded p-4">
              <h4 className="text-xs font-semibold text-red-900 uppercase mb-2">Escalation</h4>
              <p className="text-sm text-red-800">{incident.escalationReason}</p>
            </div>
          )}

          {/* Actions */}
          {incident.approvalRequired && incident.status === 'pending_approval' && (
            <div className="mt-6 space-y-2">
              <button
                onClick={() => setApprovalModalOpen(true)}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 text-sm"
              >
                Approve Action
              </button>
              <button
                onClick={handleEscalate}
                disabled={isSubmitting}
                className="w-full px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 text-sm"
              >
                Escalate
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Approval Modal */}
      {approvalModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-slate-200">
              <h3 className="text-lg font-bold">Approve Action?</h3>
            </div>
            <div className="px-6 py-4">
              <p className="text-sm text-slate-600 mb-4">
                This will execute the proposed action. Review the risk level and evidence before proceeding.
              </p>
              {incident.proposedAction && (
                <div className="bg-slate-50 border border-slate-200 rounded p-3 mb-4">
                  <div className="text-sm font-semibold">{incident.proposedAction.tool}</div>
                  <div className="text-xs text-slate-600 mt-1">{incident.proposedAction.description}</div>
                  <div className="text-xs text-amber-700 font-semibold mt-2">Risk: {incident.proposedAction.riskLevel.toUpperCase()}</div>
                </div>
              )}
            </div>
            <div className="px-6 py-4 border-t border-slate-200 flex gap-3">
              <button
                onClick={() => setApprovalModalOpen(false)}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-slate-200 text-slate-900 rounded-lg font-semibold hover:bg-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              >
                {isSubmitting ? 'Executing...' : 'Approve & Execute'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
