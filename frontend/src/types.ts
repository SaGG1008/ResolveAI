// Domain types
export type IncidentStatus = 'open' | 'investigating' | 'diagnosed' | 'pending_approval' | 'executing' | 'verifying' | 'resolved' | 'escalated';
export type AgentType = 'triage' | 'investigation' | 'diagnosis' | 'action_planner' | 'verification';
export type EvidenceType = 'knowledge_base' | 'ticket' | 'system_status' | 'procedure';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Evidence {
  id: string;
  type: EvidenceType;
  title: string;
  content: string;
  relevance: number; // 0-100
  source?: string;
}

export interface Diagnosis {
  likelyCause: string;
  confidence: number; // 0-100
  supportingEvidence: Evidence[];
  uncertainty?: string;
}

export interface Action {
  id: string;
  tool: string;
  description: string;
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  linkedEvidence: Evidence[];
  reasoning: string;
}

export interface AgentEvent {
  id: string;
  timestamp: Date;
  agent: AgentType;
  status: 'started' | 'processing' | 'completed' | 'failed';
  message: string;
  evidence?: Evidence[];
  diagnosis?: Diagnosis;
  action?: Action;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  status: IncidentStatus;
  createdAt: Date;
  updatedAt: Date;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  events: AgentEvent[];
  evidence: Evidence[];
  diagnosis?: Diagnosis;
  proposedAction?: Action;
  approvalRequired: boolean;
  escalationReason?: string;
  resolution?: {
    timestamp: Date;
    verificationMethod: string;
    success: boolean;
  };
}

export interface DashboardMetrics {
  activeIncidents: number;
  aiResolutions: number;
  escalations: number;
  avgResolutionTime: number; // minutes
}
