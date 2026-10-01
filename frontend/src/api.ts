import type { Incident, DashboardMetrics } from './types';

const API_BASE = 'http://localhost:8000/api';

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  try {
    const response = await fetch(`${API_BASE}/dashboard-metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    // Return mock data as fallback
    return {
      activeIncidents: 2,
      aiResolutions: 24,
      escalations: 3,
      avgResolutionTime: 8,
    };
  }
}

export async function fetchIncidents(): Promise<Incident[]> {
  try {
    const response = await fetch(`${API_BASE}/incidents`);
    if (!response.ok) throw new Error('Failed to fetch incidents');
    const data = await response.json();
    // Convert ISO strings to Date objects
    return data.map((inc: any) => ({
      ...inc,
      createdAt: new Date(inc.createdAt),
      updatedAt: new Date(inc.updatedAt),
      events: inc.events.map((evt: any) => ({
        ...evt,
        timestamp: new Date(evt.timestamp),
      })),
      resolution: inc.resolution ? {
        ...inc.resolution,
        timestamp: new Date(inc.resolution.timestamp),
      } : undefined,
    }));
  } catch (error) {
    console.error('Error fetching incidents:', error);
    throw error;
  }
}

export async function fetchIncident(id: string): Promise<Incident> {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}`);
    if (!response.ok) throw new Error(`Failed to fetch incident ${id}`);
    const data = await response.json();
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      events: data.events.map((evt: any) => ({
        ...evt,
        timestamp: new Date(evt.timestamp),
      })),
      resolution: data.resolution ? {
        ...data.resolution,
        timestamp: new Date(data.resolution.timestamp),
      } : undefined,
    };
  } catch (error) {
    console.error(`Error fetching incident ${id}:`, error);
    throw error;
  }
}

export async function createIncident(title: string, description: string, category: string): Promise<Incident> {
  try {
    const response = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description, category }),
    });
    if (!response.ok) throw new Error('Failed to create incident');
    const data = await response.json();
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      events: [],
    };
  } catch (error) {
    console.error('Error creating incident:', error);
    throw error;
  }
}

export async function approveIncident(id: string): Promise<Incident> {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}/approve`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to approve incident');
    const data = await response.json();
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      events: data.events.map((evt: any) => ({
        ...evt,
        timestamp: new Date(evt.timestamp),
      })),
    };
  } catch (error) {
    console.error('Error approving incident:', error);
    throw error;
  }
}

export async function escalateIncident(id: string, reason: string): Promise<Incident> {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}/escalate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reason }),
    });
    if (!response.ok) throw new Error('Failed to escalate incident');
    const data = await response.json();
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      events: data.events.map((evt: any) => ({
        ...evt,
        timestamp: new Date(evt.timestamp),
      })),
    };
  } catch (error) {
    console.error('Error escalating incident:', error);
    throw error;
  }
}

export async function resolveIncident(id: string, verificationMethod: string): Promise<Incident> {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}/resolve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ verification_method: verificationMethod }),
    });
    if (!response.ok) throw new Error('Failed to resolve incident');
    const data = await response.json();
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      events: data.events.map((evt: any) => ({
        ...evt,
        timestamp: new Date(evt.timestamp),
      })),
      resolution: data.resolution ? {
        ...data.resolution,
        timestamp: new Date(data.resolution.timestamp),
      } : undefined,
    };
  } catch (error) {
    console.error('Error resolving incident:', error);
    throw error;
  }
}
