import React from 'react';
import type { Incident } from '../types';

interface KPICardProps {
  label: string;
  value: number;
  subtext?: string;
  trend?: 'up' | 'down' | 'stable';
}

export const KPICard: React.FC<KPICardProps> = ({ label, value, subtext, trend }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
      <div className="text-sm font-medium text-slate-600 mb-2">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="text-3xl font-bold text-slate-900">{value}</div>
        {trend && (
          <div className={`text-xs font-semibold ${trend === 'up' ? 'text-red-600' : trend === 'down' ? 'text-green-600' : 'text-slate-500'}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          </div>
        )}
      </div>
      {subtext && <div className="text-xs text-slate-500 mt-2">{subtext}</div>}
    </div>
  );
};

interface RecentIncidentsTableProps {
  incidents: Incident[];
  onIncidentClick: (incident: Incident) => void;
}

export const RecentIncidentsTable: React.FC<RecentIncidentsTableProps> = ({ incidents, onIncidentClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'escalated':
        return 'bg-red-100 text-red-800';
      case 'investigating':
      case 'diagnosed':
      case 'pending_approval':
      case 'executing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'text-red-600 font-bold';
      case 'high':
        return 'text-orange-600 font-semibold';
      case 'medium':
        return 'text-yellow-600';
      default:
        return 'text-slate-600';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            <th className="text-left px-6 py-3 text-xs font-semibold text-slate-700">Incident</th>
            <th className="text-left px-6 py-3 text-xs font-semibold text-slate-700">Priority</th>
            <th className="text-left px-6 py-3 text-xs font-semibold text-slate-700">Status</th>
            <th className="text-left px-6 py-3 text-xs font-semibold text-slate-700">Category</th>
            <th className="text-left px-6 py-3 text-xs font-semibold text-slate-700">Time</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((incident) => (
            <tr
              key={incident.id}
              onClick={() => onIncidentClick(incident)}
              className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition"
            >
              <td className="px-6 py-4">
                <div className="font-medium text-slate-900">{incident.id}</div>
                <div className="text-sm text-slate-600">{incident.title}</div>
              </td>
              <td className="px-6 py-4">
                <span className={`text-sm font-semibold ${getPriorityColor(incident.priority)}`}>
                  {incident.priority.charAt(0).toUpperCase() + incident.priority.slice(1)}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(incident.status)}`}>
                  {incident.status.replace(/_/g, ' ').charAt(0).toUpperCase() + incident.status.replace(/_/g, ' ').slice(1)}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-slate-600">{incident.category}</td>
              <td className="px-6 py-4 text-sm text-slate-500">
                {new Date(incident.createdAt).toLocaleTimeString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
