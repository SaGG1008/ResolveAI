import React from 'react';
import type { IncidentStatus } from '../types';

interface AgentPipelineBarProps {
  currentStatus: IncidentStatus;
  className?: string;
}

const STAGES = [
  { key: 'intake', label: '1. Intake' },
  { key: 'triage', label: '2. Triage' },
  { key: 'investigation', label: '3. Investigate' },
  { key: 'diagnosis', label: '4. Diagnose' },
  { key: 'action', label: '5. Action' },
  { key: 'verification', label: '6. Verify' },
];

export const AgentPipelineBar: React.FC<AgentPipelineBarProps> = ({ currentStatus, className = '' }) => {
  // Map incident status to stage index
  const getActiveStageIndex = (status: IncidentStatus): number => {
    switch (status) {
      case 'open':
        return 0;
      case 'investigating':
        return 2;
      case 'diagnosed':
        return 3;
      case 'pending_approval':
      case 'executing':
        return 4;
      case 'verifying':
        return 5;
      case 'resolved':
      case 'escalated':
        return 6;
      default:
        return 0;
    }
  };

  const activeIdx = getActiveStageIndex(currentStatus);
  const isResolved = currentStatus === 'resolved';
  const isEscalated = currentStatus === 'escalated';

  return (
    <div className={`bg-[#0f1422] border border-slate-800 rounded-xl p-3 ${className}`}>
      <div className="flex items-center justify-between gap-2 overflow-x-auto">
        {STAGES.map((stage, idx) => {
          let stateStyle = 'bg-slate-900 border-slate-800 text-slate-400';
          let icon = '○';

          if (isResolved) {
            stateStyle = 'bg-emerald-950/40 border-emerald-700/60 text-emerald-400 font-semibold';
            icon = '✓';
          } else if (isEscalated) {
            if (idx <= activeIdx) {
              stateStyle = 'bg-rose-950/40 border-rose-800/60 text-rose-400 font-semibold';
              icon = '⚠';
            }
          } else if (idx < activeIdx) {
            stateStyle = 'bg-emerald-950/30 border-emerald-800/40 text-emerald-400 font-semibold';
            icon = '✓';
          } else if (idx === activeIdx) {
            stateStyle = 'bg-blue-950/70 border-blue-500/80 text-blue-300 font-bold shadow-sm shadow-blue-500/20';
            icon = '▶';
          }

          return (
            <React.Fragment key={stage.key}>
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono transition-all shrink-0 ${stateStyle}`}
              >
                <span className="text-[11px]">{icon}</span>
                <span>{stage.label}</span>
              </div>
              {idx < STAGES.length - 1 && (
                <div className={`h-[1px] flex-1 min-w-3 ${idx < activeIdx || isResolved ? 'bg-emerald-500/50' : 'bg-slate-800'}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
