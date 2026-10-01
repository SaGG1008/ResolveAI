import type { Incident, DashboardMetrics } from '../types';
import { mockIncidents, mockMetrics } from '../mockData';

const API_BASE = 'http://localhost:8000/api';

// Helper to convert backend date strings to Date objects
function parseIncident(data: any): Incident {
  return {
    ...data,
    createdAt: new Date(data.createdAt),
    updatedAt: new Date(data.updatedAt),
    events: (data.events || []).map((evt: any) => ({
      ...evt,
      timestamp: new Date(evt.timestamp),
    })),
    resolution: data.resolution ? {
      ...data.resolution,
      timestamp: new Date(data.resolution.timestamp),
    } : undefined
  };
}

export const api = {
  async getIncidents(): Promise<Incident[]> {
    try {
      const res = await fetch(`${API_BASE}/incidents`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.map(parseIncident);
    } catch (err) {
      console.warn('Backend unavailable, using fallback mock data:', err);
      return mockIncidents;
    }
  },

  async getIncident(id: string): Promise<Incident> {
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return parseIncident(data);
    } catch (err) {
      console.warn('Backend unavailable, using fallback mock data for incident:', err);
      const found = mockIncidents.find(i => i.id === id);
      if (found) return found;
      throw err;
    }
  },

  async createIncident(description: string, title?: string, priority?: string, category?: string): Promise<Incident> {
    try {
      const res = await fetch(`${API_BASE}/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, title, priority, category })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return parseIncident(data);
    } catch (err) {
      console.warn('Backend unavailable for creation, generating local mock incident:', err);
      const newMock: Incident = {
        id: `INC-${Math.floor(1000 + Math.random() * 9000)}`,
        title: title || description.slice(0, 50),
        description,
        status: 'open',
        priority: (priority as any) || 'medium',
        category: category || 'General IT',
        createdAt: new Date(),
        updatedAt: new Date(),
        events: [{
          id: `evt-${Date.now()}`,
          timestamp: new Date(),
          agent: 'triage',
          status: 'started',
          message: 'Intake recorded. Dispatched for investigation.'
        }],
        evidence: [],
        approvalRequired: false
      };
      return newMock;
    }
  },

  async submitApproval(incidentId: string, approved: boolean, notes?: string): Promise<Incident> {
    try {
      const res = await fetch(`${API_BASE}/incidents/${incidentId}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved, operator_id: 'admin', notes })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return parseIncident(data);
    } catch (err) {
      console.warn('Backend unavailable, applying local approval fallback:', err);
      throw err;
    }
  },

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    try {
      const res = await fetch(`${API_BASE}/dashboard/metrics`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('Using fallback metrics:', err);
      return mockMetrics;
    }
  },

  subscribeToIncident(incidentId: string, onUpdate: (incident: Incident) => void): () => void {
    try {
      const eventSource = new EventSource(`${API_BASE}/incidents/${incidentId}/stream`);
      
      eventSource.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          const parsed = parseIncident(raw);
          onUpdate(parsed);
        } catch (e) {
          console.error('Error parsing SSE event data:', e);
        }
      };

      eventSource.onerror = (err) => {
        console.warn('SSE stream connection closed or errored:', err);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    } catch (err) {
      console.warn('Unable to establish SSE stream:', err);
      return () => {};
    }
  }
};
